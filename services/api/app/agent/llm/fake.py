"""테스트용 LLM. 스크립트의 응답을 차례로 돌려주고 받은 입력을 기록한다.

스크립트 한 단계: 문자열(본문), dict(JSON 본문으로 직렬화), AIMessage(도구 호출 등),
예외(그 시도를 실패시킴), 또는 입력 메시지를 받아 그중 하나를 돌려주는 함수.
스크립트가 끝나면 default를 돌려준다.
"""

import json
import uuid
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage

from app.agent.llm.base import BaseLLM

Step = (
    str
    | dict
    | AIMessage
    | BaseException
    | Callable[[list[BaseMessage]], "str | dict | AIMessage | BaseException"]
)


@dataclass
class FakeCall:
    messages: list[BaseMessage]
    tools: list[dict[str, Any]] | None
    json_mode: bool
    config: dict[str, Any]
    temperature: float = 0.0
    schema: dict[str, Any] | None = None

    @property
    def text(self) -> str:
        """입력 전체를 한 문자열로(검사용)."""
        return "\n".join(str(m.content) for m in self.messages)


def tool_call(name: str, **args: Any) -> AIMessage:
    """도구 하나를 부르는 모델 응답."""
    call = {"name": name, "args": args, "id": f"call_{uuid.uuid4().hex[:8]}", "type": "tool_call"}
    return AIMessage(content="", tool_calls=[call])


class FakeLLM(BaseLLM):
    model = "fake"

    def __init__(
        self,
        script: Iterable[Step] = (),
        default: str | dict = "네, 확인했어요.",
        temperature: float = 0.7,
    ) -> None:
        self.script: list[Step] = list(script)
        self.default = default
        self.retry_delays = (0.0, 0.0)
        self.temperature = temperature
        self.calls: list[FakeCall] = []

    async def _call(
        self,
        messages: list[BaseMessage],
        *,
        tools: list[dict[str, Any]] | None,
        json_mode: bool,
        temperature: float,
        config: dict[str, Any],
        schema: dict[str, Any] | None = None,
    ) -> AIMessage:
        self.calls.append(FakeCall(messages, tools, json_mode, config, temperature, schema))
        step = self.script.pop(0) if self.script else self.default
        if callable(step) and not isinstance(step, BaseException):
            step = step(messages)
        if isinstance(step, BaseException):
            raise step
        if isinstance(step, dict):
            step = json.dumps(step, ensure_ascii=False)
        message = AIMessage(content=step) if isinstance(step, str) else step
        tokens_in = sum(len(str(m.content)) for m in messages) // 2
        message.usage_metadata = {
            "input_tokens": tokens_in,
            "output_tokens": len(str(message.content)) // 2,
            "total_tokens": tokens_in + len(str(message.content)) // 2,
        }
        return message
