class ToolExecutionLimitError(RuntimeError):
    """Raised when a tool execution exceeds the allowed limit."""

    pass


class ToolExecutionController:
    """Deterministically Controls the number of tool calls."""

    def __init__(self, max_tool_calls: int) -> None:

        if max_tool_calls < 1:
            raise ValueError("max_tool_calls must be atleast 1.")

        self.tool_calls = 0
        self.max_tool_calls = max_tool_calls

    def check_and_record(self) -> None:
        """Checks if the tool call limit has been reached and records the call."""
        if self.tool_calls >= self.max_tool_calls:
            raise ToolExecutionLimitError(
                f"Tool execution limit of {self.max_tool_calls} exceeded."
            )
        self.tool_calls += 1
