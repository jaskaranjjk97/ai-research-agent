import pytest

from app.tools.execution import (
    ToolExecutionController,
    ToolExecutionLimitError,
)


def test_controller_starts_with_zero_tool_calls():
    controller = ToolExecutionController(
        max_tool_calls=3,
    )

    assert controller.tool_calls == 0


def test_controller_records_tool_calls():
    controller = ToolExecutionController(
        max_tool_calls=3,
    )

    controller.check_and_record()

    assert controller.tool_calls == 1


def test_controller_allows_calls_until_limit():
    controller = ToolExecutionController(
        max_tool_calls=3,
    )

    controller.check_and_record()
    controller.check_and_record()
    controller.check_and_record()

    assert controller.tool_calls == 3


def test_controller_rejects_call_after_limit():
    controller = ToolExecutionController(
        max_tool_calls=2,
    )

    controller.check_and_record()
    controller.check_and_record()

    with pytest.raises(
        ToolExecutionLimitError,
        match=f"Tool execution limit of {controller.max_tool_calls} exceeded.",
    ):
        controller.check_and_record()

    assert controller.tool_calls == 2


def test_controller_rejects_invalid_limit():
    with pytest.raises(
        ValueError,
        match="max_tool_calls must be atleast 1.",
    ):
        ToolExecutionController(max_tool_calls=0)
