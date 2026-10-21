"""실행 컨텍스트가 토론 그래프와 의도 분류를 같은 설정으로 연결하는지 확인한다."""

from dataclasses import replace

import pytest
from app.agent import intent
from app.agent.assistant import AssistantGraphRunner
from app.agent.debate import DebateGraphRunner
from app.config import get_settings
from app.services.context import build_context


@pytest.mark.asyncio
async def test_real_runner_wires_intent_and_assistant(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ASSISTANT_RUNNER", "real")
    settings = replace(get_settings(), agent_runner="real")
    captured = {}

    async def classify(llm, message, **kwargs):
        captured.update(llm=llm, message=message, kwargs=kwargs)
        return intent.fallback(), True

    monkeypatch.setattr(intent, "classify", classify)
    ctx = build_context(settings)
    try:
        assert isinstance(ctx.runner, DebateGraphRunner)
        assert isinstance(ctx.assistant, AssistantGraphRunner)
        await ctx.classify("물로 정해요", phase="keyword", message_id="message-1")
        assert captured["llm"] is not None
        assert captured["kwargs"]["message_id"] == "message-1"
    finally:
        await ctx.engine.dispose()
