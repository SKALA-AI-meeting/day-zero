# 공통 타깃. 서비스 목록은 docs/worker-infra/design.md "Docker Compose"(8개 서비스)와 같다.
COMPOSE     = docker compose -f infra/docker-compose.yml --env-file infra/.env
COMPOSE_DEV = $(COMPOSE) -f infra/docker-compose.dev.yml
SERVICES    = services/api services/debate-mcp services/rag-mcp services/assessment-mcp services/report-worker
# 저장소 루트에서 도는 검사: 계약 픽스처(G-C)와 미션 카탈로그 정합성
ROOT_TESTS  = tests/test_contract_fixtures.py scenarios/missions/debate/tests
XFAIL       = tests/expected-failures.txt

# 기대 실패 목록에서 접두어(셸 변수 p) 아래 줄을 그 폴더 기준 경로로 꺼내 건너뛰기 인자로 만든다.
# 노드 id(::)는 FLAG_NODE, 파일·디렉터리는 FLAG_PATH. 주석·빈 줄은 무시한다.
XFAIL_ARGS = awk -F'|' -v p="$$p" -v fn="$$fn" -v fp="$$fp" '!/^[[:space:]]*(\#|$$)/ { \
	gsub(/[[:space:]]+/, "", $$1); if (index($$1, p) != 1) next; x = substr($$1, length(p) + 1); \
	if (index(x, "::")) { if (fn != "") print fn " " x } else print fp " " x }' $(XFAIL)

infra-up:        ## 개발용 인프라만, 로컬 포트 바인딩: postgres 5432, rabbitmq 5672, rag-mcp 9102
	$(COMPOSE_DEV) up -d postgres rabbitmq rag-mcp

infra-down:
	$(COMPOSE_DEV) down

up:              ## 전체 compose 8개 서비스(G-F 확인, 통합)
	$(COMPOSE) up -d --build --wait

down:
	$(COMPOSE) down

seed:            ## 전체 compose 실행 뒤 자료·데모 채용 건·RAG 색인 준비
	$(COMPOSE) exec api python /scripts/seed.py --api http://localhost:8000 --rag http://rag-mcp:9102/mcp --minutes 15

seed-local:      ## make infra-up과 로컬 API 실행 뒤 자료·채용 건·색인 준비
	uv run --project services/api python scripts/seed.py --minutes 15

build:          ## 서비스 이미지와 프론트 프로덕션 빌드
	$(COMPOSE) build


test:            ## 단위 테스트 전부(LLM mock, live 제외). 기대 실패 목록(tests/expected-failures.txt)의 테스트는 건너뛴다
	@p=""; fn=--deselect; fp=--ignore; skips=$$($(XFAIL_ARGS)); \
	  echo "== root $(ROOT_TESTS)"; uv run pytest -q -p no:cacheprovider $$skips $(ROOT_TESTS) || exit 1
	@for s in $(SERVICES); do \
	  if [ -f $$s/pyproject.toml ]; then \
	    p="$$s/"; fn=--deselect; fp=--ignore; skips=$$($(XFAIL_ARGS)); \
	    echo "== $$s $$skips"; \
	    (cd $$s && uv run pytest -q -m "not live" $$skips) || exit 1; \
	  fi; \
	done
	@if [ -f apps/web/package.json ]; then \
	  p="apps/web/"; fn=""; fp=--exclude; skips=$$($(XFAIL_ARGS)); \
	  echo "== apps/web $$skips"; (cd apps/web && pnpm test --silent $$skips) || exit 1; \
	fi

test-live:       ## 실제 LLM 호출 테스트만
	cd services/api && uv run pytest -q -m live

lint:
	uv run ruff check . && uv run ruff format --check .
	@if [ -f apps/web/package.json ]; then (cd apps/web && pnpm lint) || exit 1; fi

.PHONY: infra-up infra-down up down seed seed-local build test test-live lint
