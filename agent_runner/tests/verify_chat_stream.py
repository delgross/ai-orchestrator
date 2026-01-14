
import asyncio
import json
import logging
from unittest.mock import MagicMock, AsyncMock
from typing import List, Dict, Any, Optional

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_chat_stream")

# Mock classes to avoid full dependencies
class MockState:
    def __init__(self):
        self.config = {}
        self.internet_available = True
        self.agent_model = "test-model"
        self.fallback_model = "fallback-model"
        self.fallback_enabled = True
        self.max_tool_steps = 3
        self.max_tool_count = 10
        self.context_prune_limit = 20
        self.tool_consecutive_failures = 0
        self.is_high_tier_model = lambda x: False
        self.is_local_model = lambda x: True
        
        # Mocks for properties referenced
        self.router_auth_token = "mock_token"
        self.gateway_base = "http://mock_gateway"
        self.http_timeout = 10.0
        self.mcp_circuit_breaker = MagicMock()
        self.mcp_circuit_breaker.is_allowed.return_value = True

# Import AgentEngine but we'll override methods
from agent_runner.engine import AgentEngine

class TestEngine(AgentEngine):
    def __init__(self, state):
        self.state = state
        self.executor = MagicMock()
        self.executor.get_all_tools = AsyncMock(return_value=[
            {"function": {"name": "get_current_time", "description": "Get time"}}
        ])
        self.executor.tool_definitions = []
        self.executor.execute_tool_call = AsyncMock(return_value={"result": "12:00 PM"})
        self.memory = MagicMock() # Mock memory server
        self.memory.store_episode = AsyncMock() # Fix: must be awaitable for create_task
        self.hallucination_detector = MagicMock()

        # We don't init Nexus since we're testing engine directly
        # self.nexus = ... 

    async def get_system_prompt(self, messages, skip_refinement=False):
        return "System Prompt"

    async def call_gateway_streaming(self, messages, model=None, tools=None):
        """Mocked generator to simulate LLM responses"""
        yielded_content = False
        
        # Determine scenario based on user message content
        last_msg = messages[-1]["content"] if messages else ""
        
        if "hello" in last_msg.lower():
            # Scenario 1: Basic Chat
            tokens = ["Hello", " there", "!"]
            for t in tokens:
                yield {
                    "choices": [{
                        "delta": {"content": t},
                        "finish_reason": None
                    }]
                }
                await asyncio.sleep(0.01)
            yield {
                "choices": [{
                    "delta": {},
                    "finish_reason": "stop"
                }]
            }
            yield {"type": "usage", "usage": {"total_tokens": 10}}
            yield {"type": "done_signal"} # Simulation of whatever ends the stream

        elif "time" in last_msg.lower():
            # Scenario 2: Hallucinated JSON
            # Llama 3 style: Text that looks like JSON
            hallucination_text = '{"name": "get_time", "parameters": {}}'
            
            # Streaming the text
            chunk_size = 5
            for i in range(0, len(hallucination_text), chunk_size):
                chunk = hallucination_text[i:i+chunk_size]
                yield {
                    "choices": [{
                        "delta": {"content": chunk},
                        "finish_reason": None
                    }]
                }
                await asyncio.sleep(0.01)
            
            yield {
                "choices": [{
                    "delta": {},
                    "finish_reason": "stop"
                }]
            }

async def run_tests():
    state = MockState()
    engine = TestEngine(state)
    
    print("\n\n=== TEST 1: Basic Chat ===")
    messages = [{"role": "user", "content": "Hello world"}]
    
    events = []
    async for event in engine.agent_stream(messages, request_id="req-1"):
        events.append(event)
        # print(f"Event: {event.get('type')} - {event.get('content') or event.get('tool')}")
    
    # Validation
    tokens = "".join([e["content"] for e in events if e["type"] == "token"])
    print(f"Captured: {tokens}")
    if "Hello there!" in tokens:
        print("✅ Basic Chat Test Passed")
    else:
        print(f"❌ Basic Chat Failed. Got: {tokens}")

    print("\n\n=== TEST 2: Hallucination Converter (get_time) ===")
    messages = [{"role": "user", "content": "What time is it?"}]
    
    events = []
    tool_executed = False
    
    async for event in engine.agent_stream(messages, request_id="req-2"):
        events.append(event)
        if event["type"] == "tool_start":
            print(f"Tool Started: {event.get('tool')}")
            if event.get("tool") == "get_current_time":
                tool_executed = True
    
    if tool_executed:
        print("✅ Hallucination Converter Test Passed (get_time -> get_current_time)")
    else:
        print("❌ Hallucination Converter Failed. No tool execution detected.")
        for e in events:
            print(e)

if __name__ == "__main__":
    asyncio.run(run_tests())
