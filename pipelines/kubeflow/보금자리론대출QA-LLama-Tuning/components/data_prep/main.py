#!/usr/bin/env python3
"""
원문 FAQ를 LLaMA Instruct SFT 포맷으로 변환

입력: raw_faq.json
출력: sft_dataset.jsonl (LLaMA Instruct format)

포맷:
{
  "text": "<s>[INST] <<SYS>>\\n{system_prompt}\\n<</SYS>>\\n\\n{question} [/INST] {answer} </s>"
}
"""

import argparse
import json
import logging
from pathlib import Path
from typing import List, Dict


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# System prompt 정의
SYSTEM_PROMPT = """너는 보금자리론 FAQ 상담 도우미야. 제공된 FAQ 범위 내에서만 답하고, 확실하지 않으면 공식 안내로 유도해."""


def load_raw_faq(input_path: Path) -> List[Dict[str, str]]:
    """원문 FAQ JSON 로드

    Args:
        input_path: raw_faq.json 경로

    Returns:
        FAQ 항목 리스트
    """
    logger.info(f"Loading raw FAQ from {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    logger.info(f"Loaded {len(data)} FAQ items")
    return data


def convert_to_llama_instruct(
    question: str,
    answer: str,
    system_prompt: str = SYSTEM_PROMPT,
    include_system: bool = True
) -> str:
    """LLaMA Instruct 포맷으로 변환

    Args:
        question: 질문
        answer: 답변
        system_prompt: 시스템 프롬프트
        include_system: 시스템 프롬프트 포함 여부

    Returns:
        LLaMA Instruct 포맷 문자열
    """
    if include_system:
        text = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{question} [/INST] {answer} </s>"
    else:
        text = f"<s>[INST] {question} [/INST] {answer} </s>"

    return text


def convert_dataset(
    raw_items: List[Dict[str, str]],
    include_system: bool = True,
    remove_duplicates: bool = True
) -> List[Dict[str, str]]:
    """전체 데이터셋 변환

    Args:
        raw_items: 원문 FAQ 항목
        include_system: 시스템 프롬프트 포함 여부
        remove_duplicates: 중복 제거 여부

    Returns:
        SFT 포맷 항목 리스트
    """
    sft_items = []
    seen_questions = set()

    for item in raw_items:
        question = item.get('question', '').strip()
        answer = item.get('answer', '').strip()

        # 빈 항목 스킵
        if not question or not answer:
            logger.warning(f"Skipping empty item: {item.get('item_id', 'unknown')}")
            continue

        # 중복 체크
        if remove_duplicates:
            if question in seen_questions:
                logger.debug(f"Skipping duplicate question: {question[:50]}...")
                continue
            seen_questions.add(question)

        # LLaMA Instruct 포맷 변환
        text = convert_to_llama_instruct(
            question=question,
            answer=answer,
            include_system=include_system
        )

        sft_items.append({'text': text})

    logger.info(f"Converted {len(sft_items)} items (removed {len(raw_items) - len(sft_items)} duplicates/invalid)")
    return sft_items


def save_to_jsonl(items: List[Dict[str, str]], output_path: Path) -> None:
    """JSONL 파일로 저장

    Args:
        items: SFT 항목 리스트
        output_path: 출력 파일 경로
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for item in items:
            json_line = json.dumps(item, ensure_ascii=False)
            f.write(json_line + '\n')

    logger.info(f"Saved {len(items)} items to {output_path}")


def preview_samples(items: List[Dict[str, str]], num_samples: int = 3) -> None:
    """변환 결과 미리보기

    Args:
        items: SFT 항목 리스트
        num_samples: 출력할 샘플 수
    """
    logger.info(f"\n{'='*80}\nPreview of {num_samples} samples:\n{'='*80}")

    for idx, item in enumerate(items[:num_samples], 1):
        text = item['text']
        # 보기 좋게 정리
        display_text = text.replace('<s>', '[START] ').replace('</s>', ' [END]')
        logger.info(f"\nSample {idx}:\n{display_text}\n{'-'*80}")


def main():
    parser = argparse.ArgumentParser(description='FAQ를 LLaMA Instruct SFT 포맷으로 변환')
    parser.add_argument(
        '--input',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'data' / 'raw_faq.json',
        help='입력 raw_faq.json 경로'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'data' / 'sft_dataset.jsonl',
        help='출력 JSONL 파일 경로'
    )
    parser.add_argument(
        '--no-system',
        action='store_true',
        help='시스템 프롬프트 제외'
    )
    parser.add_argument(
        '--keep-duplicates',
        action='store_true',
        help='중복 항목 유지'
    )
    parser.add_argument(
        '--preview',
        type=int,
        default=3,
        help='미리보기 샘플 수 (0이면 미리보기 안 함)'
    )

    args = parser.parse_args()

    # 입력 파일 존재 확인
    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        return 1

    # 원문 로드
    raw_items = load_raw_faq(args.input)

    if not raw_items:
        logger.error("No items to convert!")
        return 1

    # SFT 포맷 변환
    sft_items = convert_dataset(
        raw_items,
        include_system=not args.no_system,
        remove_duplicates=not args.keep_duplicates
    )

    if not sft_items:
        logger.error("Conversion resulted in no valid items!")
        return 1

    # 미리보기
    if args.preview > 0:
        preview_samples(sft_items, args.preview)

    # 저장
    save_to_jsonl(sft_items, args.output)
    logger.info(f"Conversion completed! {len(sft_items)} items saved.")

    return 0


if __name__ == '__main__':
    exit(main())
