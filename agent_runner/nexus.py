
import logging
import re
import json
import asyncio
import time
from typing import AsyncGenerator, Dict, Any, Optional

from agent_runner.state import AgentState
from common.sovereign import get_sovereign_triggers

logger = logging.getLogger("agent_runner.nexus")

class Nexus:
    """
    The Regulator (The Box).
    Arbitrates all I/O for the Chat Interface.
    
    Roles:
    1. Input Regulator: Intercepts User Input -> Trigger Check -> Agent Engine.
    2. Output Regulator: Yields unified stream (System Events + LLM Tokens).
    """
    def __init__(self, state: AgentState, engine: Any):
        self.state = state
        self.engine = engine # Reference to AgentEngine
        
        # [FEATURE] Window Manager Registry
        # Tracks the state of all UI Layers.
        self.layers = {
            "chat": {"active": True, "opacity": 1.0, "visible": True},
            "system": {"active": True, "opacity": 1.0, "visible": True},
            "emoji": {"active": True, "opacity": 1.0, "visible": True},
            "ui_control": {"active": True, "opacity": 1.0, "visible": False}
        }

    async def dispatch(self, user_message: str, request_id: str, context: Optional[list] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        The Only Gate for User Input.
        
        Flow:
        1. Trigger Check (Is this a command?)
        2. Execution (If trigger matches)
        3. LLM Handover (With context)
        """
        logger.info(f"Nexus Dispatch: [{request_id}] '{user_message[:50]}...'")
        
        # Check for system events (not sent to LLM) - existing mechanism
        if hasattr(self.state, 'system_event_queue') and self.state.system_event_queue:
            try:
                # Non-blocking check for queued system events
                while not self.state.system_event_queue.empty():
                    sys_event_data = self.state.system_event_queue.get_nowait()
                    # Only inject if request_id matches or is None (broadcast)
                    if sys_event_data.get("request_id") is None or sys_event_data.get("request_id") == request_id:
                        sys_event = sys_event_data.get("event", {})
                        event_type = sys_event.get("type", "system_status")
                        
                        # Handle control_ui events (e.g., clear_chat)
                        if event_type == "control_ui":
                            yield {
                                "type": "control_ui",
                                "action": sys_event.get("action"),
                                "target": sys_event.get("target")
                            }
                        else:
                            # Yield as system_status (NOT system_message - goes to frontend, not LLM)
                            yield {
                                "type": "system_status",
                                "content": sys_event.get("content"),
                                "severity": sys_event.get("severity", "info"),
                                "timestamp": sys_event_data.get("timestamp")
                            }
            except asyncio.QueueEmpty:
                pass
        
        # 1. Trigger Check
        trigger_result = await self._check_and_execute_trigger(user_message)
        
        # 2. Additive Context Construction
        # Use provided context (history) or start fresh
        messages = context if context else []
        messages.append({"role": "user", "content": user_message})
        
        if trigger_result:
            # [FEATURE] Decoupled Layer Handling
            if trigger_result.get("action") == "ui_layer":
                 # Yield a dedicated Layer Event
                 yield {
                     "type": "layer_update",
                     "layer": trigger_result.get("target_layer", "unknown"),
                     "content": trigger_result.get("output")
                 }
                 # STOP execution immediately. Do not involve LLM. Do not log to chat history.
                 return

            if trigger_result.get("action") == "diagnostic":
                 # Diagnostic actions (Prompt, Help) act as blocking answers.
                 # We treat them as part of the "system" layer but render them as output.
                 yield {
                     "type": "tool_end",
                     "tool": "nexus_trigger",
                     "output": trigger_result["output"]
                 }
                 return

            # Yield Event: Trigger Activated (Legacy Tool Call Simulation)
            yield {
                "type": "tool_start", 
                "tool": "nexus_trigger", 
                "input": {"trigger": trigger_result["name"], "action": trigger_result["action"]}
            }
            
            # Inject System Result into Conversation
            # This allows the LLM to see what just happened.
            sys_note = f"[System Action: Triggered '{trigger_result['name']}']\nResult: {trigger_result['output']}"
            messages.append({"role": "system", "content": sys_note})
            
            yield {
                "type": "tool_end",
                "tool": "nexus_trigger",
                "output": trigger_result["output"]
            }

            # Special Event: UI Control
            if trigger_result.get("action") == "control_ui":
                 # We assume action_data has 'target'
                 # We yield a custom event type that the frontend must handle
                 yield {
                     "type": "control_ui",
                     "target": trigger_result.get("action_data", {}).get("target"),
                 }
            
            # If the trigger was "BLOCKING" (e.g. complete takeover), we might stop here.
            # But the requirement is "Additive" -> Send to LLM.
            
        # 3. Gateway to Agent Engine (LLM)
        # We wrap the engine's stream
        # 3. Gateway to Agent Engine (LLM) - With System Event Multiplexing
        # We wrap the engine's stream AND monitor the system event queue concurrently.
        # This allows deep-system events (like Healer warnings) to interrupt/augment the stream.
        try:
            stream_iterator = self.engine._protected_agent_stream(messages, request_id=request_id).__aiter__()
            
            # Tasks
            task_stream = asyncio.create_task(stream_iterator.__anext__())
            task_queue = asyncio.create_task(
                self.state.system_event_queue.get() 
                if hasattr(self.state, 'system_event_queue') and self.state.system_event_queue 
                else asyncio.Future()
            ) # Future that never completes if no queue
            
            # If no queue, task_queue needs to be a dummy that waits forever
            if not (hasattr(self.state, 'system_event_queue') and self.state.system_event_queue):
                 task_queue = asyncio.create_task(asyncio.sleep(3600)) # Dummy wait
            
            stream_active = True
            
            while stream_active or not task_queue.done():
                # If stream is done and queue is empty (or we don't care about queue after stream?), 
                # strictly speaking we stop when stream stops? 
                # Ideally we drain queue for a bit? No, just stop when stream stops to avoid hanging.
                if not stream_active:
                    break

                done, pending = await asyncio.wait(
                    [task_stream, task_queue], 
                    return_when=asyncio.FIRST_COMPLETED
                )

                if task_stream in done:
                    try:
                        event = task_stream.result()
                        yield event
                        # Schedule next stream item
                        task_stream = asyncio.create_task(stream_iterator.__anext__())
                    except StopAsyncIteration:
                        stream_active = False
                    except Exception as e:
                        logger.error(f"Stream Error: {e}")
                        yield {"type": "error", "error": str(e)}
                        stream_active = False
                
                if task_queue in done:
                    try:
                        sys_event_data = task_queue.result()
                        # Process Event
                        if sys_event_data.get("request_id") is None or sys_event_data.get("request_id") == request_id:
                            sys_event = sys_event_data.get("event", {})
                            logger.info(f"🚨 NEXUS YIELDING SYSTEM EVENT: {sys_event}")
                            yield {
                                "type": "system_status", # Standardize
                                "content": sys_event.get("content"),
                                "severity": sys_event.get("severity", "info"),
                                "timestamp": sys_event_data.get("timestamp")
                            }
                        
                        # Schedule next queue item
                        task_queue = asyncio.create_task(self.state.system_event_queue.get())
                    except Exception as e:
                        logger.warning(f"Queue Error: {e}")
                        # Recreate task to avoid loop death
                        task_queue = asyncio.create_task(self.state.system_event_queue.get())

            # Cleanup pending tasks
            if not task_stream.done(): task_stream.cancel()
            if not task_queue.done(): task_queue.cancel()

        except Exception as e:
            logger.error(f"Nexus Proxy Error: {e}")
            yield {"type": "error", "error": str(e)}

    async def _check_and_execute_trigger(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Scans Sovereign Registry for generic string matches.
        Returns result dict if matched and executed.
        """
        try:
            triggers = get_sovereign_triggers()
            
            # [FIX] Handle Multi-modal Content (List of blocks)
            if isinstance(text, list):
                # Extract first text block
                text_content = ""
                for block in text:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_content += block.get("text", "") + " "
                lower_text = text_content.strip().lower()
            elif isinstance(text, str):
                lower_text = text.lower().strip()
            else:
                lower_text = str(text).lower().strip()

            
            # [FEATURE] Maître d' Integration for Natural Language Commands
            # Use Local LLM to classify intent before proceeding to Agent.
            # This enables "Show me prompt" to be handled locally.
            try:
                # We need to call engine's classifier, but it might depend on state being ready.
                # Assuming Nexus runs after startup.
                if hasattr(self.engine, "_classify_search_intent"):
                    intent = await self.engine._classify_search_intent(text)
                    
                    # [FIX] Handle List Return from Maître d' (Multi-intent support)
                    if isinstance(intent, list) and len(intent) > 0:
                        intent = intent[0] # Take primary intent
                    
                    sys_action = intent.get("system_action")

                    
                    if sys_action:
                        logger.info(f"Nexus: Maître d' selected system action '{sys_action}'")
                        
                        if sys_action == "prompt":
                             prompt_content = await self.engine.get_system_prompt()
                             return {
                                 "name": "View System Prompt",
                                 "action": "diagnostic",
                                 "output": f"### Current System Prompt\n```\n{prompt_content}\n```"
                             }
                        elif sys_action == "help":
                             return {
                                 "name": "Help",
                                 "action": "diagnostic",
                                 "output": "### Available Commands\n- **Prompt**: 'Show me the system prompt'\n- **Restart**: 'Restart the system'\n- **Help**: 'Help me'"
                             }
                        elif sys_action == "restart":
                             # We'll let the trigger logic handle restart or do it here
                             from agent_runner.tools.system import tool_restart_agent
                             res = await tool_restart_agent(self.state)
                             return {
                                 "name": "Restart",
                                 "action": "diagnostic",
                                 "output": "System Restart Initiated."
                             }
                        elif sys_action == "emoji":
                             # [GUARD] Check if Layer is Active
                             if not self.layers.get("emoji", {}).get("active", True):
                                 logger.info("Nexus: Emoji layer inactive. Ignoring request.")
                                 return {
                                     "name": "Layer Inactive",
                                     "action": "diagnostic",
                                     "output": "Emoji Layer is currently disabled."
                                 }

                             # [FEATURE] Decoupled Logic Layer
                             # This returns a specific 'ui_layer' action that can be routed separately.
                             return {
                                 "name": "Emoji Injection",
                                 "action": "ui_layer",
                                 "target_layer": "emoji",
                                 "output": "🐝✨🚀"
                             }
                        
                        # [FEATURE] Layer Control
                        elif sys_action.startswith("disable_") or sys_action.startswith("enable_"):
                            target = sys_action.split("_")[1] # e.g. "emoji"
                            is_enable = sys_action.startswith("enable_")
                            
                            if target in self.layers:
                                self.layers[target]["active"] = is_enable
                                status = "Enabled" if is_enable else "Disabled"
                                return {
                                    "name": f"Layer Control ({target})",
                                    "action": "control_ui", # Or new type
                                    "output": f"Layer '{target}' is now {status}.",
                                    "action_data": {
                                        "target": target,
                                        "active": is_enable
                                    }
                                }
            except Exception as e:
                logger.warning(f"Nexus intent check failed: {e}")

            for trig_def in triggers:
                # In Sovereign YAML, triggers are a list of dicts with 'pattern' key
                name = trig_def.get("pattern", "unknown") # Name is the pattern for now, or we infer it
                pattern = trig_def.get("pattern")
                
                if lower_text == pattern.lower() or lower_text.startswith(f"{pattern.lower()} "):
                    logger.info(f"Nexus: Trigger Matched '{name}'")
                    
                    # Execute
                    # Logic: Triggers usually map to a Tool Call logic
                    # We need a robust way to execute. Ideally reuse ToolExecutor?
                    # Or simple mapping for now.
                    
                    action_type = trig_def.get("action_type")
                    action_data = trig_def.get("action_data", {})
                    
                    output = f"Trigger '{name}' executed."
                    
                    # A. Tool Call Action
                    if action_type == "tool_call":
                        tool_name = action_data.get("tool")
                        args = action_data.get("args", {})
                        
                        if tool_name and hasattr(self.engine, "executor"):
                             # Construct generic tool call
                             # We use a special request_id to indicate system origin
                             tool_tuple = {
                                 "function": {
                                     "name": tool_name,
                                     "arguments": json.dumps(args) 
                                 }
                             }
                             try:
                                 res = await self.engine.executor.execute_tool_call(tool_tuple, request_id=f"trigger-{name}", user_query="")
                                 output = json.dumps(res, indent=2)
                             except Exception as e:
                                 output = f"Trigger Error: {e}"

                    # B. System Prompt Injection (e.g. debug_mode)
                    elif action_type == "system_prompt":
                        # This effectively just sets a preference in config?
                        # Or do we inject a one-off system message?
                        # sovereign.yaml definition: key/value. 
                        # This implies updating state.config
                        key = action_data.get("key")
                        val = action_data.get("value")
                        if key:
                             # Use ConfigManager if available
                             if hasattr(self.state, "config_manager"):
                                 # We'll treat this as a runtime config update
                                 # (Need to resolve key mapping if complex)
                                 pass 
                             output = f"Preference '{key}' set to {val} (Simulated)"
                    
                    # C. Menu / UI Control
                    elif action_type == "menu":
                        output = "## System Menu\n- **restart**: Reboot Agent\n- **status**: Health Report\n- **restore_chat**: Reset Mode"
                    
                    # D. UI/Navigation Control (New)
                    elif action_type == "control_ui":
                        # This tells the frontend to open a URL/Window
                        # Returns a special result that the Dispatcher will wrap in a tool_start/end equivalent
                        # or we can yield a custom event type from dispatch?
                        # For now, let's keep it simple: The Output contains the instruction, 
                        # but we really need a specific event type for the frontend to react.
                        # We will modify dispatch to check for this action type.
                        output = f"Opening UI: {action_data.get('target', 'Unknown')}"

                    
                    # D. Legacy Hardcoded (Fallback)
                    elif name == "restart":
                        from agent_runner.tools.system import tool_restart_agent
                        res = await tool_restart_agent(self.state)
                        output = "System Restart Initiated."

                    return {"name": name, "action": action_type, "output": output}
        except Exception as e:
            logger.error(f"Trigger Check Failed: {e}", exc_info=True)
            return None

    async def inject_system_message(self, message: str, level: str = "INFO"):
        """
        Allows System Components to speak to the Chat Interface.
        (Future Feature: Pushing to connected WebSocket clients)
        """
        # Currently, the Chat is Request/Response (HTTP).
        # We cannot 'push' to a closed HTTP connection.
        # This function acts as a placeholder for WebSocket/Queue injection.
        logger.info(f"Nexus System Message ({level}): {message}")
    
    async def inject_stream_event(self, event: Dict[str, Any], request_id: Optional[str] = None) -> bool:
        """
        Inject a system event into the active chat stream.
        
        This allows system components (startup, health checks, etc.) to inject
        messages directly into the chat stream without requiring a user request.
        
        Args:
            event: Event dictionary with 'type', 'content', etc.
            request_id: Optional request ID to target a specific stream
            
        Returns:
            True if event was queued, False if no active stream
        """
        # Store events in a queue that the stream generator checks
        if not hasattr(self.state, 'system_event_queue'):
            self.state.system_event_queue = asyncio.Queue()
        
        await self.state.system_event_queue.put({
            "event": event,
            "request_id": request_id,
            "timestamp": time.time()
        })
        
        logger.debug(f"Injected system event into stream: {event.get('type')}")
        return True