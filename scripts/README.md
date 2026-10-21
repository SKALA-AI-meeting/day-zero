# 실행 도구

- `make seed`: 전체 Docker Compose가 실행 중일 때, API 컨테이너에서 자료·15분 채용 건·RAG 색인을 준비한다.
- `make seed-local`: 로컬 개발 API와 `make infra-up` 실행 후 동일한 준비를 한다.
- `uv run --project services/api python scripts/make_session.py --minutes 15`: 공개 API로 데모 채용 건과 지원자 초대 링크를 만든다. 출력된 링크를 브라우저에서 연다.

기본 데모 관리자: `admin@dayzero.example` / `dayzero-seed`. 실제 사용할 계정은 화면의 회원가입으로 생성한다.
