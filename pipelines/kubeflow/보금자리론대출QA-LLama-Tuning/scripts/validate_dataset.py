#!/usr/bin/env python3
"""
SFT 데이터셋 품질 검증 스크립트

검증 항목:
- LLaMA 토큰 포맷 유효성
- UTF-8 인코딩
- 최소 데이터 임계값
- 한국어 비율
- 중복 검사
- 답변 길이 통계
"""

import argparse
import json
import logging
import re
from collections import Counter
from pathlib import Path
from typing import List, Dict, Tuple


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatasetValidator:
    """SFT 데이터셋 검증기"""

    # LLaMA Instruct 토큰 패턴
    LLAMA_PATTERN = re.compile(
        r'<s>\[INST\].*?\[/INST\].*?</s>',
        re.DOTALL
    )

    # 한국어 문자 패턴
    KOREAN_PATTERN = re.compile(r'[가-힣]')

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.stats = {
            'total_items': 0,
            'valid_format': 0,
            'invalid_format': 0,
            'duplicates': 0,
            'avg_answer_length': 0,
            'min_answer_length': float('inf'),
            'max_answer_length': 0,
            'avg_korean_ratio': 0
        }

    def load_dataset(self, path: Path) -> List[Dict[str, str]]:
        """JSONL 데이터셋 로드

        Args:
            path: JSONL 파일 경로

        Returns:
            데이터셋 항목 리스트
        """
        logger.info(f"Loading dataset from {path}")

        items = []
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    item = json.loads(line.strip())
                    items.append(item)
                except json.JSONDecodeError as e:
                    self.issues.append(f"Line {line_num}: Invalid JSON - {e}")

        self.stats['total_items'] = len(items)
        logger.info(f"Loaded {len(items)} items")
        return items

    def validate_llama_format(self, text: str) -> bool:
        """LLaMA Instruct 포맷 검증

        Args:
            text: 검증할 텍스트

        Returns:
            유효 여부
        """
        # 필수 토큰 체크
        required_tokens = ['<s>', '[INST]', '[/INST]', '</s>']
        for token in required_tokens:
            if token not in text:
                return False

        # 전체 패턴 매칭
        if not self.LLAMA_PATTERN.search(text):
            return False

        return True

    def calculate_korean_ratio(self, text: str) -> float:
        """한국어 비율 계산

        Args:
            text: 텍스트

        Returns:
            한국어 비율 (0.0 ~ 1.0)
        """
        if not text:
            return 0.0

        # 공백 제외한 문자 수
        non_space_chars = len(text.replace(' ', '').replace('\n', ''))
        if non_space_chars == 0:
            return 0.0

        # 한국어 문자 수
        korean_chars = len(self.KOREAN_PATTERN.findall(text))

        return korean_chars / non_space_chars

    def extract_answer(self, text: str) -> str:
        """텍스트에서 답변 부분 추출

        Args:
            text: LLaMA Instruct 포맷 텍스트

        Returns:
            답변 텍스트
        """
        match = re.search(r'\[/INST\]\s*(.*?)\s*</s>', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def validate_items(self, items: List[Dict[str, str]]) -> None:
        """전체 항목 검증

        Args:
            items: 데이터셋 항목 리스트
        """
        seen_texts = set()
        answer_lengths = []
        korean_ratios = []

        for idx, item in enumerate(items, 1):
            text = item.get('text', '')

            # 포맷 검증
            if self.validate_llama_format(text):
                self.stats['valid_format'] += 1
            else:
                self.stats['invalid_format'] += 1
                self.issues.append(f"Item {idx}: Invalid LLaMA format")

            # 중복 체크
            if text in seen_texts:
                self.stats['duplicates'] += 1
                self.warnings.append(f"Item {idx}: Duplicate text")
            else:
                seen_texts.add(text)

            # 답변 길이 통계
            answer = self.extract_answer(text)
            answer_len = len(answer)
            answer_lengths.append(answer_len)

            self.stats['min_answer_length'] = min(
                self.stats['min_answer_length'],
                answer_len
            )
            self.stats['max_answer_length'] = max(
                self.stats['max_answer_length'],
                answer_len
            )

            # 한국어 비율
            korean_ratio = self.calculate_korean_ratio(text)
            korean_ratios.append(korean_ratio)

            # 낮은 한국어 비율 경고
            if korean_ratio < 0.5:
                self.warnings.append(
                    f"Item {idx}: Low Korean ratio ({korean_ratio:.2%})"
                )

            # 너무 짧은 답변 경고
            if answer_len < 10:
                self.warnings.append(
                    f"Item {idx}: Very short answer ({answer_len} chars)"
                )

        # 통계 계산
        if answer_lengths:
            self.stats['avg_answer_length'] = sum(answer_lengths) / len(answer_lengths)
        if korean_ratios:
            self.stats['avg_korean_ratio'] = sum(korean_ratios) / len(korean_ratios)

    def check_minimum_threshold(self, min_items: int = 50) -> None:
        """최소 데이터 임계값 체크

        Args:
            min_items: 최소 항목 수
        """
        if self.stats['total_items'] < min_items:
            self.issues.append(
                f"Dataset has only {self.stats['total_items']} items "
                f"(minimum: {min_items})"
            )

    def check_korean_ratio_threshold(self, min_ratio: float = 0.7) -> None:
        """한국어 비율 임계값 체크

        Args:
            min_ratio: 최소 한국어 비율
        """
        if self.stats['avg_korean_ratio'] < min_ratio:
            self.issues.append(
                f"Average Korean ratio is {self.stats['avg_korean_ratio']:.2%} "
                f"(minimum: {min_ratio:.0%})"
            )

    def print_report(self) -> None:
        """검증 보고서 출력"""
        logger.info("\n" + "="*80)
        logger.info("VALIDATION REPORT")
        logger.info("="*80)

        # 통계
        logger.info("\n📊 Statistics:")
        logger.info(f"  Total items: {self.stats['total_items']}")
        logger.info(f"  Valid format: {self.stats['valid_format']}")
        logger.info(f"  Invalid format: {self.stats['invalid_format']}")
        logger.info(f"  Duplicates: {self.stats['duplicates']}")
        logger.info(f"  Avg answer length: {self.stats['avg_answer_length']:.1f} chars")
        logger.info(f"  Min answer length: {self.stats['min_answer_length']} chars")
        logger.info(f"  Max answer length: {self.stats['max_answer_length']} chars")
        logger.info(f"  Avg Korean ratio: {self.stats['avg_korean_ratio']:.2%}")

        # 이슈
        if self.issues:
            logger.warning(f"\n❌ Critical Issues ({len(self.issues)}):")
            for issue in self.issues[:10]:  # 최대 10개만 출력
                logger.warning(f"  - {issue}")
            if len(self.issues) > 10:
                logger.warning(f"  ... and {len(self.issues) - 10} more issues")
        else:
            logger.info("\n✅ No critical issues found!")

        # 경고
        if self.warnings:
            logger.info(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # 최대 10개만 출력
                logger.info(f"  - {warning}")
            if len(self.warnings) > 10:
                logger.info(f"  ... and {len(self.warnings) - 10} more warnings")

        logger.info("\n" + "="*80)

    def is_valid(self) -> bool:
        """검증 통과 여부

        Returns:
            Critical issue가 없으면 True
        """
        return len(self.issues) == 0


def main():
    parser = argparse.ArgumentParser(description='SFT 데이터셋 품질 검증')
    parser.add_argument(
        '--input',
        type=Path,
        default=Path(__file__).parent.parent / 'data' / 'sft_dataset.jsonl',
        help='입력 JSONL 파일 경로'
    )
    parser.add_argument(
        '--min-items',
        type=int,
        default=50,
        help='최소 항목 수'
    )
    parser.add_argument(
        '--min-korean-ratio',
        type=float,
        default=0.7,
        help='최소 한국어 비율 (0.0 ~ 1.0)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='엄격 모드 (경고도 실패로 처리)'
    )

    args = parser.parse_args()

    # 입력 파일 존재 확인
    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        return 1

    # 검증 실행
    validator = DatasetValidator()

    items = validator.load_dataset(args.input)
    if not items:
        logger.error("No items to validate!")
        return 1

    validator.validate_items(items)
    validator.check_minimum_threshold(args.min_items)
    validator.check_korean_ratio_threshold(args.min_korean_ratio)

    # 보고서 출력
    validator.print_report()

    # 결과 판정
    if not validator.is_valid():
        logger.error("\n❌ Validation FAILED!")
        return 1

    if args.strict and validator.warnings:
        logger.error(f"\n❌ Validation FAILED (strict mode: {len(validator.warnings)} warnings)")
        return 1

    logger.info("\n✅ Validation PASSED!")
    return 0


if __name__ == '__main__':
    exit(main())
