"""어시스턴트 사용 사실에 요청·응답 원문 발췌가 남는지 확인한다."""

from report_worker.report import ai_usage


def test_ai_usage_uses_assistant_call_quotes():
    calls = [
        {
            "id": "call-1",
            "request_message_id": "request-1",
            "response_message_id": "response-1",
            "request_quote": "물 관련 자료를 찾아줘",
            "response_quote": "자료의 핵심은 물 사용량입니다.",
            "cited_material_ids": ["water_stats"],
            "created_at": "2026-10-21T09:10:00Z",
        }
    ]
    result = ai_usage(calls, [], {"assistant_calls": [{"call_id": "call-1", "t_min": 10}]}, None)
    assert result["events"][0]["request_quote"] == "물 관련 자료를 찾아줘"
    assert result["events"][0]["response_quote"] == "자료의 핵심은 물 사용량입니다."
