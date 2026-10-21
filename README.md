# Day Zero

지원자가 AI 동료 3명과 토론하고 기획안을 제출하면, 기업 담당자가 대화의 행동 근거를 바탕으로 평가하는 채용 서비스 MVP입니다.

## 구현 범위

- 지원자: 초대 링크, 참여 동의, 표시 이름, 재접속, 실시간 채팅, 결정 사항, 참고 자료, AI 어시스턴트, 기획안 자동 저장·제출, 디브리핑
- 토론: 키워드 → 문제 상황 → 해결책 → 기획안, 60분/15분 모드, 고정 페르소나 3명, 장면 카드 6개, 합의 및 시간 초과 처리
- 관리자: 가입·로그인, 채용 건 생성, 초대 링크 발급·재발급·취소, 지원자 목록, 대화 기록, 근거 리포트, 차원별 조정·최종 검토
- 평가: 공개된 행동 기준 척도에 따른 AI 평가, 행동 근거·확신도 표시, 담당자 최종 검토. 합격·불합격·순위·총점은 생성하지 않습니다.
- 실행: 세션별 메일박스, 세 MCP의 도구 경계, 큐·워커, 재시도·DLQ, PostgreSQL 저장

## 빠른 실행: Docker Compose

Docker와 Docker Compose가 필요합니다. 웹은 `http://localhost:3000`, 공개 API는 `http://localhost:8000`에서 실행됩니다.

```sh
cp infra/.env.example infra/.env
```

`infra/.env`에서 다음 값을 설정합니다.

- `OPENAI_API_KEY`: 기본 모델 `gpt-4o-mini`용 키
- `JWT_SECRET`: 충분히 긴 임의 문자열(`openssl rand -hex 32`로 생성 가능)
- `INTERNAL_TOKEN`, `ASSESSMENT_MCP_TOKEN`: 각각 다른 임의 문자열
- `AGENT_RUNNER=real`: 실제 토론 에이전트 실행(예시 기본값)

```sh
make up
make seed
```

최초 실행 시 RAG 임베딩 모델 `BAAI/bge-m3`를 내려받으므로 시간이 걸릴 수 있습니다. 모델 캐시는 Docker 볼륨에 보관됩니다. 키는 런타임 환경변수로만 사용하며 웹 번들에는 넣지 않습니다.

1. `http://localhost:3000/admin/login`에서 데모 관리자 `admin@dayzero.example` / `dayzero-seed`로 로그인합니다. 또는 회원가입으로 별도 계정을 만듭니다.
2. 채용 건을 열고 지원자 이름·이메일을 입력해 초대 링크를 발급합니다. MVP에서는 링크를 복사해 전달합니다.
3. 별도 브라우저에서 초대 링크를 열어 동의한 뒤 토론을 시작합니다. 15분 모드는 60분 흐름을 같은 비율로 압축합니다.
4. 세션 종료 후 관리자 화면에서 생성된 리포트를 열고 검토합니다.

종료는 `make down`입니다. 데이터 볼륨은 유지됩니다.

## 화면만 살펴보기

Node.js 22 이상과 pnpm이 있으면 백엔드·API 키 없이 목업 화면을 실행할 수 있습니다.

```sh
cd apps/web
pnpm install --frozen-lockfile
NEXT_PUBLIC_MOCK=1 pnpm dev
```

`http://localhost:3000`에서 지원자 데모와 관리자 화면으로 이동합니다. 이 모드는 고정 예시 데이터와 재생 대본을 사용합니다.

## 로컬 개발

Python 3.12·uv, Node.js 22 이상·pnpm, Docker가 필요합니다. 인프라는 컨테이너로, 앱은 로컬에서 실행합니다.

```sh
make infra-up
```

`infra/.env.local`에 `.env`를 복사하고 `DATABASE_URL`, `RABBITMQ_URL`, `API_INTERNAL_URL`, `DEBATE_MCP_URL`, `RAG_MCP_URL`, `ASSESSMENT_MCP_URL`의 호스트를 `localhost`로 변경합니다. API 내부 포트는 8001입니다. 각 서비스에서 `uv sync --frozen` 후 별도 터미널로 실행합니다.

```sh
cd services/api && uv run python -m app.run --reload
cd services/debate-mcp && uv run python -m debate_mcp
cd services/assessment-mcp && uv run python -m assessment_mcp
cd services/report-worker && uv run python -m report_worker
cd apps/web && pnpm install --frozen-lockfile && pnpm dev
```

루트에서 `make seed-local`로 자료와 데모 채용 건을 준비합니다. CLI로 초대 링크를 만들려면 다음 명령을 사용합니다.

```sh
uv run --project services/api python scripts/make_session.py --minutes 15
```

다른 호스트에서 실행할 때는 `WEB_BASE_URL`, `WEB_ORIGIN`, `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_WS_URL`을 맞추고 웹 이미지를 다시 빌드합니다. `NEXT_PUBLIC_*`는 빌드 시점에 반영됩니다.

## 구성

| 경로 | 역할 |
|---|---|
| `apps/web` | Next.js·React 프론트 |
| `services/api` | FastAPI 공개/내부 API, 세션 상태, 토론·어시스턴트 그래프 |
| `services/debate-mcp` | 토론 상태·메시지·의견·합의 도구 |
| `services/rag-mcp` | 공개된 참고 자료 색인·검색·조회 |
| `services/assessment-mcp` | 별도 토큰으로 보호된 관찰·평가 도구 |
| `services/report-worker` | 큐 소비, 평가·근거 리포트·검토 후 확정 |
| `scenarios/missions/debate` | 키워드, 페르소나, 자료, 장면, 척도 데이터 |
| `infra` | PostgreSQL·RabbitMQ·서비스 Compose 및 스키마 |
| `docs` | 인터페이스·데이터·에이전트·화면 기술 설계 |
| `DEVELOPMENT.md` | 완료 상태, 남은 작업, 이어가기 정보 |

## 빌드

```sh
cd apps/web && pnpm build
# 전체 서비스 이미지 빌드: 저장소 루트에서
make build
```

제출 마감에 맞춰 개발과 빌드를 우선했습니다. 검증한 빌드 범위와 미검증 사항은 `DEVELOPMENT.md`에 기록합니다. 기존 단위 테스트는 개발 자료로 포함하지만 이번 마무리에서는 새 테스트를 작성하거나 전체 테스트·실 LLM E2E를 실행하지 않습니다.
