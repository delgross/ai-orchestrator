import logging
import json
import time
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.services.slash_commands")

class SlashCommandProcessor:
    """
    Handles local 'Slash Commands' that execute directly on the Agent Runner
    without going to the LLM.
    Examples: /save, /clear, /no-emoji
    """
    
    def __init__(self, state: AgentState):
        self.state = state

    async def process_messages(self, messages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Scan the LAST user message for slash commands.
        Returns:
            (filtered_messages, immediate_response)
        
        If immediate_response is present, the LLM loop should return it immediately
        and NOT call the AI.
        """
        if not messages:
            return messages, None
            
        last_msg = messages[-1]
        if last_msg.get("role") != "user":
            return messages, None
            
        content = last_msg.get("content", "").strip()
        if not content.startswith("/"):
            return messages, None
            
        # Parse Command
        parts = content.split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        logger.info(f"Processing Slash Command: {cmd} args='{args}'")
        
        response_content = None
        
        # --- DYNAMIC TRIGGER REGISTRY (The New Control Plane) ---
        from common.sovereign import get_sovereign_triggers
        triggers = get_sovereign_triggers()
        
        words_in_msg = content.split()
        
        for t in triggers:
            pattern = t.get("pattern")
            if not pattern: continue
            
            # Pattern Match Strategy
            # Use 'words check' if it's a single token, or 'in' check if complex?
            # User requirement: "Basically any word can become a way to switch modes."
            # Simplest correct approach: if the exact pattern is found as a token
            
            match_found = False
            if " " in pattern:
                # Phrase match
                if pattern in content:
                    match_found = True
            else:
                # Word match
                if pattern in words_in_msg:
                    match_found = True
            
            if match_found:
                logger.info(f"Dynamic Trigger '{pattern}' matched. Action: {t.get('action_type')}")
                
                # EXECUTE ACTION
                act_type = t.get("action_type")
                act_data = t.get("action_data", {})
                
                if act_type == "control_ui":
                    # Send signal to frontend
                    return messages, {
                        "role": "assistant",
                        "content": f"Trigger '{pattern}' activated.",
                        "function_call": {
                            "name": "control_ui",
                            "arguments": json.dumps(act_data)
                        }
                    }
                elif act_type == "menu":
                    # Render menu (would ideally be dynamic too)
                    menu_text = """### 🎛️ SYSTEM COMPOSITOR (Dynamic)
**Active Triggers**
"""
                    for tr in triggers:
                         menu_text += f"* `{tr['pattern']}`: {tr.get('description', 'No desc')}\n"
                         
                    menu_text += "\n* `;; <cmd>`: Shell Passthrough"
                    
                    return messages, {
                        "role": "assistant",
                        "content": menu_text
                    }
                elif act_type == "system_prompt":
                    # Update config
                    k = act_data.get("key")
                    v = act_data.get("value")
                    if k and v:
                        # Rudimentary nested set. Ideally use ConfigManager.
                        # Assuming 'preferences.debug' -> self.state.config['preferences']['debug']
                        parts = k.split(".")
                        top = parts[0]
                        if top not in self.state.config: self.state.config[top] = {}
                        if len(parts) > 1:
                            self.state.config[top][parts[1]] = v
                        else:
                            self.state.config[top] = v
                        
                        return messages, {
                            "role": "assistant",
                            "content": f"✅ System Config Updated: `{k} = {v}`"
                        }
                elif act_type == "tool_call":
                    # --- REPORT GENERATION (Single Tool) ---
                    # action_data: {"tool": "check_system_health", "args": {}}
                    tool_name = act_data.get("tool")
                    tool_args = act_data.get("args", {})
                    
                    if not tool_name:
                         return messages, {"role": "assistant", "content": "❌ Invalid Trigger: No tool specified."}
                         
                    # Execute
                    res_str = await self._execute_tool(tool_name, tool_args)
                    return messages, {"role": "assistant", "content": res_str}
                    
                elif act_type == "macro":
                    # --- SERIES OF ACTIONS ---
                    # action_data: {"steps": [{"type": "tool_call", "data": ...}, {"type": "system_prompt", "data": ...}]}
                    steps = act_data.get("steps", [])
                    report = f"## 🔗 Macro Execution: {pattern}\n"
                    
                    for i, step in enumerate(steps):
                        s_type = step.get("type")
                        s_data = step.get("data", {})
                        
                        report += f"**Step {i+1}** ({s_type}): "
                        
                        if s_type == "tool_call":
                            t_name = s_data.get("tool")
                            t_args = s_data.get("args", {})
                            res = await self._execute_tool(t_name, t_args)
                            report += f"\n{res}\n\n"
                        elif s_type == "system_prompt":
                            k = s_data.get("key")
                            v = s_data.get("value")
                            if k:
                                parts = k.split(".")
                                top = parts[0]
                                if top not in self.state.config: self.state.config[top] = {}
                                if len(parts) > 1:
                                    self.state.config[top][parts[1]] = v
                                else:
                                    self.state.config[top] = v
                                report += f"Config `{k}` set to `{v}`.\n"
                        elif s_type == "control_ui":
                            # Macros cannot easily return multiple UI control signals unless we batch them
                            # For now, just log it
                            report += "UI Signal Sent (Simulated in Macro)\n"
                            
                    return messages, {"role": "assistant", "content": report}
                
                elif act_type == "switch_mode":
                    # --- STATE TRANSITION ---
                    # action_data: {"mode": "coding", "clear_context": true}
                    tgt_mode = act_data.get("mode") if isinstance(act_data, dict) else str(act_data)
                    clear_context = act_data.get("clear_context", False) if isinstance(act_data, dict) else False
                    
                    if tgt_mode:
                        self.state.active_mode = tgt_mode
                        
                        # Clear context if requested
                        if clear_context:
                            messages = []  # Clear conversation history
                            logger.info(f"Context cleared for mode switch to {tgt_mode}")
                        
                        return messages, {
                            "role": "assistant",
                            "content": f"🔄 Switched to **{tgt_mode.upper()}** Mode." + (" (Context cleared)" if clear_context else "")
                        }
                    else:
                        return messages, {"role": "assistant", "content": "❌ Invalid Mode Transition: No mode specified."}
        
        # --- COMMAND DISPATCH (Legacy/Shell) ---
        
        if cmd.startswith(";;"):
            # DIRECT SHELL PASSTHROUGH
            # Trigger: ;; ls -la
            # Strip ;; and spaces
            shell_cmd = content[2:].strip()
            response_content = await self._cmd_shell_passthrough(shell_cmd)
        elif cmd == "/save":
            response_content = await self._cmd_save(messages, args)
        elif cmd == "/save-last":
            response_content = await self._cmd_save_last(messages, args)
        elif cmd == "/no-emoji":
            # We can leverage system config or state
            # For now, let's inject a system prompt modifier? 
            # Or better, set it on State so get_system_prompt picks it up.
            self.state.config.setdefault("preferences", {})["suppress_emoji"] = True
            response_content = "✅ Emojis SUPPRESSED for this session."
        elif cmd == "/emoji":
            self.state.config.setdefault("preferences", {})["suppress_emoji"] = False
            response_content = "✅ Emojis ENABLED."
        elif cmd == "/clear":
            # Return empty messages (effectively clearing context for the NEXT turn, 
            # though the current turn returns this message).
            # Actually, we can return a special signal, but returning a response is safer.
            # Ideally the caller handles filtering.
            response_content = "🧹 Context Cleared (Simulated). Start a new topic."
        elif cmd == "/registry":
            # /registry <action> <target> <value>
            # e.g. /registry list models
            # e.g. /registry get policy:internet
            # e.g. /registry set policy:internet local_only
            
            sub_parts = args.split(" ", 2)
            action = sub_parts[0] if len(sub_parts) > 0 else "list"
            target = sub_parts[1] if len(sub_parts) > 1 else None
            val = sub_parts[2] if len(sub_parts) > 2 else None
            
            from agent_runner.tools.registry_tool import tool_registry_manage
            res = await tool_registry_manage(self.state, action, target, val)
            
            if res.get("ok"):
                if action == "list":
                    # Pretty Print
                    data = res.get("data", {})
                    sec = res.get("section", "unknown")
                    count = res.get("count", 0)
                    response_content = f"### 🗂️ Registry: {sec.upper()} ({count})\n"
                    response_content += "| Key | Value |\n|---|---|\n"
                    for k, v in data.items():
                         response_content += f"| `{k}` | `{v}` |\n"
                elif action == "get":
                    response_content = f"✅ **{res.get('key')}** = `{res.get('value')}`\n*(Source: {res.get('source')})*"
                elif action == "set":
                    response_content = f"✏️ {res.get('message')}"
                else:
                    response_content = str(res)
            else:
                response_content = f"❌ Registry Error: {res.get('error')}"

        else:
            # Unknown command -> Pass through to LLM? Or Warn?
            # User expectation: If I type /foo and it's not handled, maybe I meant it for the AI?
            # But usually slash commands are meta. Let's pass through if unknown, 
            # maybe the AI knows how to handle it (e.g. /imagine).
            return messages, None
            
        # Transform into an Assistant Message to return to User
        if response_content:
            response = {
                "role": "assistant",
                "content": response_content,
                "refusal": None
            }
            # We return ONLY this response, effectively bypassing the LLM
            return messages, response
            
        return messages, None

    async def _cmd_save(self, messages: List[Dict[str, Any]], filename: str) -> str:
        """Save the full conversation to a file."""
        if not filename:
            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = f"chat_{ts}.md"
            
        if not filename.endswith(".md"):
            filename += ".md"
            
        # Sanitize path - force to uploads or logs?
        # User requested "save chat to disk". Let's put it in 'saved_chats'
        target_dir = self.state.agent_fs_root / "saved_chats"
        target_dir.mkdir(exist_ok=True)
        target_path = target_dir / filename
        
        # Format as Markdown
        md_content = f"# Chat Export - {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for m in messages:
            role = m.get("role", "unknown").upper()
            text = m.get("content", "")
            md_content += f"**{role}**: {text}\n\n"
            
        try:
            with open(target_path, "w") as f:
                f.write(md_content)
            return f"💾 Chat saved to: `saved_chats/{filename}`"
        except Exception as e:
            return f"❌ Failed to save chat: {e}"

    async def _cmd_save_last(self, messages: List[Dict[str, Any]], filename: str) -> str:
        """Save the LAST assistant response to a file."""
        # Find last assistant message
        last_assist = None
        for m in reversed(messages[:-1]): # Skip the current /command message
            if m.get("role") == "assistant":
                last_assist = m
                break
        
        if not last_assist:
            return "⚠️ No previous assistant response found to save."
            
        if not filename:
            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = f"reply_{ts}.md"
            
        if not filename.endswith(".md") and not filename.endswith(".txt"):
            filename += ".md"
            
        target_dir = self.state.agent_fs_root / "saved_chats"
        target_dir.mkdir(exist_ok=True)
        target_path = target_dir / filename
        
        try:
            with open(target_path, "w") as f:
                f.write(last_assist.get("content", ""))
            return f"💾 Last reply saved to: `saved_chats/{filename}`"
        except Exception as e:
            return f"❌ Failed to save reply: {str(e)}"

    async def _cmd_shell_passthrough(self, command: str) -> str:
        """Execute a shell command immediately via the Agent's toolset."""
        from agent_runner.tools.system import tool_run_command
        
        start_t = time.time()
        result = await tool_run_command(self.state, command)
        dur = (time.time() - start_t) * 1000
        
        if result.get("ok"):
            stdout = result.get("stdout", "").strip()
            stderr = result.get("stderr", "").strip()
            
            output = ""
            if stdout:
                output += f"{stdout}\n"
            if stderr:
                output += f"STDERR:\n{stderr}\n"
                
            if result.get("truncated"):
                output += f"\n[Output Truncated. Full log: {result.get('full_log')}]"
                
            return f"📟 **Shell Passthrough** ({dur:.0f}ms)\n```bash\n{output}\n```"
        else:
            return f"❌ **Shell Error** ({dur:.0f}ms)\nError: {result.get('error')}"

    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Dynamic dispatch for specific report-generating tools."""
        try:
            res = {}
            if tool_name == "check_system_health":
                from agent_runner.tools.system import tool_check_system_health
                res = await tool_check_system_health(self.state)
                return res.get("report", str(res))
            
            elif tool_name == "get_component_map":
                from agent_runner.tools.introspection import tool_get_component_map
                res = await tool_get_component_map(self.state)
                return f"```json\n{json.dumps(res, indent=2)}\n```"
                
            elif tool_name == "run_command":
                # Dangerous but powerful
                cmd = args.get("command")
                if cmd:
                    return await self._cmd_shell_passthrough(cmd)
                else:
                    return "❌ No command provided."
            
            elif tool_name == "query_logs":
                from agent_runner.tools.system import tool_query_logs
                res = await tool_query_logs(self.state, **args)
                logs = res.get("logs", [])
                out = "### Log Query Results\n"
                for l in logs[:10]:
                    out += f"- [{l.get('timestamp')}] {l.get('level')}: {l.get('message')}\n"
                return out

            else:
                return f"❌ Unknown or Unsupported Tool in Macro: {tool_name}"
        except Exception as e:
            return f"❌ Tool Execution Failed: {e}"
