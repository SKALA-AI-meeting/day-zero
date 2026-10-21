"""공개·내부 API와 세션 스케줄러를 한 asyncio 루프에서 실행한다."""

import argparse
import asyncio
import logging
from pathlib import Path

import uvicorn

from app.main import create_internal_app, create_public_app
from app.scheduler import run_forever
from app.services.context import build_context

APP_DIR = Path(__file__).resolve().parent
log = logging.getLogger("app.run")


async def serve(host: str = "0.0.0.0") -> None:
    ctx = build_context()
    public = create_public_app(ctx, ctx.settings.web_origins)
    internal = create_internal_app(ctx)
    servers = [
        uvicorn.Server(uvicorn.Config(public, host=host, port=ctx.settings.public_port)),
        uvicorn.Server(uvicorn.Config(internal, host=host, port=ctx.settings.internal_port)),
    ]
    tasks = [asyncio.create_task(server.serve()) for server in servers]
    tasks.append(asyncio.create_task(run_forever(ctx)))
    try:
        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            task.result()
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await ctx.mailboxes.close()
        await ctx.publisher.close()
        if ctx.engine is not None:
            await ctx.engine.dispose()


def _serve_sync(host: str) -> None:
    asyncio.run(serve(host))


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.run")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--reload", action="store_true", help="app/ 변경 시 재시작(개발용)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if args.reload:
        import watchfiles

        watchfiles.run_process(APP_DIR, target=_serve_sync, args=(args.host,))
    else:
        _serve_sync(args.host)


if __name__ == "__main__":
    main()
