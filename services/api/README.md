# API

공개 FastAPI 앱(8000)과 내부 앱(8001)을 한 asyncio 프로세스에서 실행한다. 세션별 메일박스·WebSocket 허브·스케줄러를 공유한다.

```sh
uv sync --frozen
uv run python -m app.run --reload
```

- 공개: `/admin`, `/s/{token}`, `/sessions/{id}`, `/ws/sessions/{id}`, `/assets`
- 내부: `/internal/sessions/{id}` 아래 토론·자료·관찰·평가·리포트 인터페이스
- 토론 그래프: `app/agent/debate`; 어시스턴트: `app/agent/assistant`
- 환경: 저장소 `infra/.env.local` → `infra/.env` 순서. `AGENT_RUNNER=real`로 실제 에이전트를 실행한다.

전체 실행·초대 링크 생성은 루트 `README.md`, 계약은 `docs/common/contracts.md`를 참조한다.
