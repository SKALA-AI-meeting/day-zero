# Report Worker

세션 종료 후 행동 기준 척도로 평가하고, 담당자 검토를 거쳐 리포트를 확정한다.

```sh
uv sync --frozen
uv run python -m report_worker
```

- 그래프: 수집 → 사실 집계 → 요소별 평가 → draft 저장 → 담당자 검토 대기(interrupt) → 확정
- `assessment.py`: 별도 토큰을 사용한 assessment-mcp 클라이언트
- `evaluate.py`: 요소별 평가·지원자 행동 근거 검증·확신도 제한
- `report.py`: 차원별 근거·맥락·사실 지표·AI 활용 기록 조립
- `consumer.py`: `report.generate`, `report.approve`, `report.dlq` 소비·재시도
- 체크포인트 thread: `report:{session_id}:{eval_round}`
- 모델: `MODEL_EVALUATOR`(기본 `gpt-4o-mini`), temperature 0.1
- 시나리오 경로: `SCENARIOS_DIR`(Compose에서 `/scenarios` 읽기 전용 마운트)

환경 설정과 전체 실행 방법은 루트 `README.md`를 참조한다.
