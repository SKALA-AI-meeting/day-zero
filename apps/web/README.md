# Web

Next.js App Router·React·Tailwind v4 프론트. 지원자 토론·관리자 채용 관리·리포트 화면을 제공한다.

```sh
pnpm install --frozen-lockfile
pnpm dev
pnpm build
```

`NEXT_PUBLIC_API_URL`(기본 `http://localhost:8000`)과 `NEXT_PUBLIC_WS_URL`(기본 `ws://localhost:8000`)로 실제 API에 연결한다. `NEXT_PUBLIC_MOCK=1 pnpm dev`는 백엔드 없이 데모 데이터를 사용한다.

화면: `components/debate/`, `components/admin/`. 공용 UI: `components/ui/`. 디자인 토큰: `app/globals.css`.

전체 실행 방법은 루트 `README.md`를 참조한다.
