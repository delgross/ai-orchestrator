import asyncio
import tempfile
from pathlib import Path

import pytest

from agent_runner import feedback


@pytest.mark.asyncio
async def test_feedback_learning_and_suggestions():
    # Use a temporary directory to isolate test data
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        path_override = tmp_path / "maitre_d_feedback.json"

        # Record a few successes
        await feedback.record_tool_success("weather in paris", "weather", path_override=path_override)
        await feedback.record_tool_success("time in london", "time", path_override=path_override)
        await feedback.record_tool_success("news about technology", "tavily-search", path_override=path_override)

        # Ensure file was written
        assert path_override.exists()

        # Query suggestions should return something
        suggestions = await feedback.get_suggested_servers(
            "what is the weather in berlin",
            state=None,
            path_override=path_override,
        )
        assert "weather" in suggestions

        # Edge case: very short query returns empty list
        suggestions_short = await feedback.get_suggested_servers(
            "hi",
            state=None,
            path_override=path_override,
        )
        assert suggestions_short == []


