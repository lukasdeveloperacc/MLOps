# BoGeumjaRiLoAN-QA (Ko) — SFT LLaMA + KServe Serving

한국주택금융공사(HF) **보금자리론 FAQ**를 기반으로, 한국어 특화 Q&A 모델을 **SFT(QLoRA/LoRA)**로 튜닝하고 **KServe**로 서빙하는 MLOps 포트폴리오 프로젝트입니다.

> 목표: **데이터 수집 → 전처리 → SFT 학습 → 평가 → (Ollama 로컬 검증) → KServe 배포**까지 End-to-End로 재현 가능하게 구축

- [Reference Page](https://velog.io/@judy_choi/LLMLLaMA3-Fine-Tuning-%EB%B0%A9%EB%B2%95-%EC%A0%95%EB%A6%AC)

---

## What this project builds
- **한국어 Q&A API**: 보금자리론 FAQ 범위 내 답변
- **안전장치(Fallback)**: 근거가 부족하거나 범위 밖이면 “FAQ에서 확인 어려움 + 공식 안내”로 응답
- **MLOps 파이프라인**: 재현 가능한 데이터/학습/평가/배포 워크플로
- **KServe 운영**: GPU 기반 서빙 + 모델 버전 롤백 가능

---

## Scope
### In
- HF 보금자리론 FAQ 페이지에서 Q/A 수집 및 학습 데이터 생성
- LLaMA 기반 한국어 모델 SFT(LoRA/QLoRA)
- KServe(vLLM/HF runtime)로 서빙
- 평가/회귀 테스트 + 기본 모니터링/런북

### Out
- 실제 대출 심사/승인 결과 보장
- 실시간 정책 변경 자동 반영(추후 확장)

---

## Data
### Source
- [HF 보금자리론 FAQ 페이지](https://www.hf.go.kr/ko/sub01/sub01_07_01.do?mode=list&&pagerLimit=10&pager.offset=0)(자주하는 질문)

### Important: dataset handling
- **원문 FAQ 텍스트는 repo에 커밋하지 않습니다.**
- 대신 `scripts/scrape_faq.py` 실행으로 로컬에서 데이터가 생성됩니다.

### Dataset format (LLaMA Instruct SFT JSONL)
```json
{
  "text": "<s>[INST] <<SYS>>\n너는 보금자리론 FAQ 상담 도우미야. 제공된 FAQ 범위 내에서만 답하고, 확실하지 않으면 공식 안내로 유도해.\n<</SYS>>\n\n보금자리론 신청 자격이 어떻게 되나요? [/INST] 만 19세 이상 무주택자로서... </s>"
}
