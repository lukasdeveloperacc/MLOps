#!/usr/bin/env python3
"""
HF 보금자리론 FAQ 웹 스크래핑 스크립트

사용법:
    python scrape_faq.py --output ../data/raw_faq.json
"""

import argparse
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HFBogeumFAQScraper:
    """한국주택금융공사 보금자리론 FAQ 스크래퍼"""

    BASE_URL = "https://www.hf.go.kr/ko/sub01/sub01_07_01.do"

    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        """
        Args:
            max_retries: 재시도 최대 횟수
            retry_delay: 재시도 간 대기 시간 (초)
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_page(self, offset: int = 0, page_limit: int = 10) -> Optional[str]:
        """FAQ 페이지 HTML 가져오기

        Args:
            offset: 페이지 오프셋
            page_limit: 페이지당 항목 수

        Returns:
            HTML 문자열 또는 None (실패 시)
        """
        params = {
            'mode': 'list',
            'pagerLimit': page_limit,
            'pager.offset': offset
        }

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching page offset={offset} (attempt {attempt + 1}/{self.max_retries})")
                response = self.session.get(self.BASE_URL, params=params, timeout=10)
                response.raise_for_status()
                response.encoding = 'utf-8'
                return response.text

            except requests.RequestException as e:
                logger.warning(f"Request failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to fetch page after {self.max_retries} attempts")
                    return None

        return None

    def parse_faq_items(self, html: str, base_offset: int) -> List[Dict[str, str]]:
        """HTML에서 FAQ 항목 파싱

        Args:
            html: 페이지 HTML
            base_offset: 현재 페이지 오프셋 (item_id 생성용)

        Returns:
            FAQ 항목 리스트
        """
        soup = BeautifulSoup(html, 'lxml')
        items = []

        # HF FAQ 페이지의 실제 구조: <li class="J_list">
        faq_containers = soup.select('li.J_list')

        if not faq_containers:
            logger.warning("No FAQ items found with selector 'li.J_list'")
            return items

        logger.debug(f"Found {len(faq_containers)} FAQ containers")

        for idx, container in enumerate(faq_containers):
            try:
                # 질문 추출: <div class="list-header"> > <a>
                question_elem = container.select_one('.list-header a')
                if not question_elem:
                    logger.debug(f"Item {idx}: No question element found")
                    continue

                question = question_elem.get_text(strip=True)

                # 답변 추출: <div class="list-content">
                answer_elem = container.select_one('.list-content')
                if not answer_elem:
                    logger.debug(f"Item {idx}: No answer element found")
                    continue

                answer = answer_elem.get_text(strip=True)

                # "Question:" 또는 "Answer:" 접두사 제거
                answer = answer.replace('Answer:', '').strip()

                # 빈 항목 스킵
                if not question or not answer:
                    logger.debug(f"Item {idx}: Empty question or answer")
                    continue

                items.append({
                    'question': question,
                    'answer': answer,
                    'url': f"{self.BASE_URL}?mode=list&pager.offset={base_offset}",
                    'item_id': f"faq_{base_offset + idx + 1:03d}",
                    'retrieved_at': datetime.now().strftime('%Y-%m-%d')
                })

                logger.debug(f"Item {idx}: Successfully parsed (Q: {question[:50]}...)")

            except Exception as e:
                logger.warning(f"Failed to parse FAQ item {idx}: {e}")
                continue

        return items

    def scrape_all(self, page_limit: int = 10, max_pages: Optional[int] = None) -> List[Dict[str, str]]:
        """모든 FAQ 페이지 스크래핑

        Args:
            page_limit: 페이지당 항목 수
            max_pages: 최대 페이지 수 (None이면 무제한)

        Returns:
            전체 FAQ 항목 리스트
        """
        all_items = []
        offset = 0
        page_count = 0
        consecutive_empty = 0

        while True:
            # 최대 페이지 체크
            if max_pages and page_count >= max_pages:
                logger.info(f"Reached max pages limit: {max_pages}")
                break

            # 페이지 가져오기
            html = self.fetch_page(offset, page_limit)
            if not html:
                logger.warning(f"Skipping offset={offset} due to fetch failure")
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    logger.info("Too many consecutive failures, stopping")
                    break
                offset += page_limit
                page_count += 1
                continue

            # FAQ 항목 파싱
            items = self.parse_faq_items(html, offset)

            if not items:
                consecutive_empty += 1
                logger.info(f"No items found at offset={offset}")
                # 연속 3번 빈 페이지면 중단 (2번이 아니라 3번으로 변경)
                if consecutive_empty >= 3:
                    logger.info("No more items found (3 consecutive empty pages), stopping")
                    break
            else:
                consecutive_empty = 0
                all_items.extend(items)
                logger.info(f"Found {len(items)} items at offset={offset} (total: {len(all_items)})")

            # 다음 페이지로
            offset += page_limit
            page_count += 1

            # 서버 부하 방지
            time.sleep(1)

        return all_items

    def save_to_json(self, items: List[Dict[str, str]], output_path: Path) -> None:
        """JSON 파일로 저장

        Args:
            items: FAQ 항목 리스트
            output_path: 출력 파일 경로
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(items)} items to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='HF 보금자리론 FAQ 스크래퍼')
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent.parent / 'data' / 'raw_faq.json',
        help='출력 JSON 파일 경로'
    )
    parser.add_argument(
        '--page-limit',
        type=int,
        default=10,
        help='페이지당 항목 수'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=None,
        help='최대 페이지 수 (기본값: 무제한)'
    )

    args = parser.parse_args()

    # 스크래핑 실행
    scraper = HFBogeumFAQScraper()
    logger.info("Starting FAQ scraping...")

    items = scraper.scrape_all(page_limit=args.page_limit, max_pages=args.max_pages)

    if not items:
        logger.error("No FAQ items collected!")
        return 1

    # 저장
    scraper.save_to_json(items, args.output)
    logger.info(f"Scraping completed! Total items: {len(items)}")

    return 0


if __name__ == '__main__':
    exit(main())
