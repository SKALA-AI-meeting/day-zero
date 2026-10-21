# Day Zero 제출본 개발 계획

최종 갱신: 2026-10-21 19:23 KST. 제출 마감: 오늘 21:00 KST.

## 목표와 작업 원칙

- `SKALA-AI-meeting/day-zero`에 최종 개발 결과를 별도 저장소로 제출한다.
- 작업 위치: 원본 저장소의 `submission/day-zero/`. 원본 main 및 기존 트랙은 수정하지 않는다.
- 기준 코드: 원본 `origin/track/debate`의 `7e64a02`. 기존 트랙 분리·서브에이전트·리뷰·병합 게이트는 사용자 지시로 생략하고 직접 개발한다.
- 개발 완료 우선. 전체 테스트·15분 E2E는 제출을 막는 선행 조건으로 두지 않는다. 사용자 추가 지시: 테스트 코드 작성·테스트 실행 없이 최종 빌드만 확인한다. 확인하지 못한 실행 범위는 명시한다.
- 키 값은 출력하거나 커밋하지 않는다. 기존 `infra/.env`·`.env.local`은 원본에 있으며 제출본에 복사하지 않았다.
- **작업 하나를 끝낼 때마다 이 파일을 최신화한다.** 완료 항목, 변경 파일, 검증 결과, 남은 항목과 다음 시작점을 기록한다.

## 완료

1. [x] 핸드오프와 실제 Git 상태 대조: WIP 브랜치와 달리 통합 커밋에 API·에이전트·워커 구현이 이미 포함되어 있음.
2. [x] 제출 폴더 분리: 코드·시나리오·실행 설정·테스트 복사. 기획서·보고서·핸드오프·이전 캡처·기존 git 이력 제외.
3. [x] 기준 코드 프론트 프로덕션 빌드 성공(`pnpm build`), API 앱 조립 성공.
4. [x] 실행 연결 보완: report-worker 시나리오 읽기 전용 마운트, Compose web 빌드 인자, CORS 멱등 헤더, API 상대 이미지 주소 처리, env example 실제 에이전트 기본값, 화면 문구 정리.
   - 파일: `infra/docker-compose.yml`, `infra/.env.example`, `services/api/app/main.py`, `services/api/app/routers/candidate.py`, `apps/web/components/ui/avatar.tsx`, 웹 데모 fixture.
5. [x] 개발용 확인 DB `dayzero_submission` 생성 및 현재 스키마 적용. 기존 DB는 수정하지 않음.
   - 실행 중 인프라: Docker `infra-postgres-1`, `infra-rabbitmq-1`, `infra-rag-mcp-1`.
   - 원본 API·워커·웹은 새로 띄우지 않음.

## 핵심 구현 연결 확인 기록(추가 테스트 중단)

- 개발용 임시 스크립트 `/tmp/dayzero-submission-smoke.py`(제출 제외)로 실제 격리 DB에 HTTP 요청을 연결함. LLM은 fake, 큐는 메모리.
- 관리자 가입 → 카탈로그 → 15분 채용 건 → 초대 → 동의 → 세션 시작 → 세 단계 확정 → 기획안 진입까지 HTTP 200 확인.
- 발견: 기획안 자동 채움에서 마지막 solution 값이 비어 있음. `services/api/app/services/debate.py`의 `_confirm()`이 `synchronize_session=False`로 Slot을 갱신해, 같은 트랜잭션의 ORM Slot 캐시가 이전 값을 반환하는 것으로 보임. `synchronize_session="fetch"`로 수정 완료. 추가 요청 실행 없이 최종 빌드로 확인한다.
- 임시 확인 스크립트의 기획안 필드도 실제 계약과 달랐음. 사용자 지시로 추가 확인은 중단했고 이 스크립트는 제출하지 않는다.
- 빠른 단계 전환 중 FakeAgentRunner의 오래된 generation 충돌이 로그에 남음. 실 그래프는 generation 비교 및 MCP 충돌 처리 경로를 갖는다. fake 전용 로그의 품질 개선은 제출 범위에서 제외한다.

## 남은 순서

1. [x] 기획안 자동 채움 문제 수정: 마지막 확정 Slot을 같은 트랜잭션의 기획안 채움에서 읽도록 ORM 캐시 동기화.
2. [x] 실제 에이전트 기본 설정·웹 API/이미지 연결·워커 시나리오 마운트·시드 실행 경로 보완. API 및 워커 README를 실제 토론형 구현에 맞게 교체. 실 LLM/전체 E2E는 미실행.
3. [x] 이전 업무 시뮬레이션용 E2E·평가 러너·캡처 도구 제외. `scripts/make_session.py`를 현재 공개 API 기반 초대 생성 CLI로 교체. `make seed`는 컨테이너 내부 실행, `seed-local`은 로컬 실행으로 연결.
4. [x] 실행용 README·스크립트 안내·기술 문서 색인 작성. 진행 계획은 이 문서 하나로 유지. 기획서·보고서·옛 핸드오프 제외.
5. [x] 프론트 프로덕션 빌드·Python 문법/실 에이전트 앱 조립·Compose 설정 확인 성공. Docker 서비스 이미지 6개(api·debate-mcp·rag-mcp·assessment-mcp·report-worker·web) 빌드 성공. 마지막 UI 문구 변경 후 web 이미지 재빌드도 성공. 새 테스트·전체 테스트·실 LLM 실행 없음.
6. [ ] 비밀값·불필요 파일 제외 확인 → 새 git 초기화 → 한국어 커밋 → 조직 `SKALA-AI-meeting`, 이름 `day-zero`로 새 저장소 생성·push → 제출 링크 전달.
   - GitHub CLI `gh` 로그인됨. 해당 조직은 원본 remote에서 확인.
   - 19:11 확인 시 `SKALA-AI-meeting/day-zero` 저장소는 없었음.
   - 사용자가 공개 저장소로 확정함. 추가 승인 없이 생성·push 진행.

## 다음 에이전트 시작점

1. 이 파일을 읽고 남은 순서를 이어간다. 기준 코드 재복사 금지. 테스트 추가·실행 금지.
2. 빌드 후 `services/api/.venv`, `apps/web/node_modules`, `.next`는 제출 폴더 정리를 위해 제거했다. 개발을 재개하면 설치부터 진행한다. uv 캐시는 권한 때문에 `UV_CACHE_DIR=/tmp/dayzero-uv-cache`를 사용한다.
3. 실제 키는 원본 env 파일에서 필요한 프로세스에만 로드한다. 제출 폴더에 키를 넣지 않는다.
4. 개발 확인용 DB `dayzero_submission`은 정리했다. 기존 공용 DB와 실행 중 인프라는 유지했다.
5. 원본 main은 깨끗했으며, 현재 미추적 `submission/`만 추가된 상태가 예상된다. 제출본에서 자체 git 초기화 완료. 최초 코드 커밋·공개 저장소 push 진행 중이다.

## 최종 빌드 상태

- 웹 최종 `pnpm build` 성공. Python 전체 서비스·스크립트 문법 컴파일 성공. 실제 에이전트·어시스턴트와 공개·내부 API 조립 성공(자리표시 키로 생성만, LLM 미호출).
- 전체 Compose 이미지 6개 빌드 성공. 마지막 UI 문구 변경 후 web 이미지 재빌드도 성공. Docker buildx 메타데이터의 로컬 쓰기 권한 때문에 `BUILDX_CONFIG=/tmp/dayzero-buildx` 사용.
- 빌드 설정 확인용 `infra/.env` 예시 사본은 삭제했다. 사용자는 README에 따라 직접 `.env`를 준비한다.

- UI 마무리: 디브리핑 첫 문장을 실제 시나리오·목업·설계·기존 카탈로그 기대값에 동일하게 적용. 리포트의 안 이름 누락 시 내부 option id 대신 중립 문구를 표시.

- 비밀값 점검: 원본 env의 API 키·토큰·시크릿과 일치하는 제출 파일 0개. `.env`, `.venv`, `node_modules`, `.next`, 기존 `.git` 이력은 추적 대상에서 제외. Git 최초 커밋 준비 중.
