import asyncio
import json
import os
import sys
import httpx
from pathlib import Path
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configuration
ROUTER_URL = os.getenv("ROUTER_URL", "http://127.0.0.1:5455")
AGENT_URL = os.getenv("AGENT_URL", "http://127.0.0.1:5460")
# Assuming running from agent_runner directory or similar, workspace is parent of agent_runner
# Or specifically mapped. Let's assume ai root is parent of this file's dir
WORKSPACE_ROOT = Path(__file__).parent.parent.absolute()

def log(msg, level="INFO"):
    sys.stderr.write(f"[{level}] SystemControl: {msg}\n")
    sys.stderr.flush()

class SystemControlServer:
    async def get_system_health(self):
        """Check connectivity and health status of key infrastructure components."""
        report = {"timestamp": os.popen("date -u").read().strip()}
        
        async with httpx.AsyncClient(timeout=3.0) as client:
            # Check Router
            try:
                resp = await client.get(f"{ROUTER_URL}/health")
                if resp.status_code == 200:
                    report["router"] = {"status": "online", "details": resp.json()}
                else:
                    report["router"] = {"status": "error", "code": resp.status_code}
            except Exception as e:
                report["router"] = {"status": "offline", "error": str(e)}

            # Check Agent Runner
            try:
                resp = await client.get(f"{AGENT_URL}/health")
                if resp.status_code == 200:
                    report["agent_runner"] = {"status": "online", "details": resp.json()}
                else:
                    report["agent_runner"] = {"status": "error", "code": resp.status_code}
            except Exception as e:
                report["agent_runner"] = {"status": "offline", "error": str(e)}

        return report

    async def read_service_logs(self, service: str, lines: int = 20):
        """Read the last N lines of logs for a specific service."""
        valid_services = {
            "router": "router.log",
            "agent_runner": "agent_runner.log",
            "ollama": "ollama.log"
        }
        
        if service not in valid_services:
            return {"error": f"Unknown service '{service}'. Available: {list(valid_services.keys())}"}
            
        log_path = WORKSPACE_ROOT / valid_services[service]
        
        if not log_path.exists():
            return {"error": f"Log file not found at {log_path}"}
            
        try:
            # Safe execution of tail
            proc = await asyncio.create_subprocess_exec(
                "tail", "-n", str(lines), str(log_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                return {"error": f"Failed to read logs: {stderr.decode()}"}
                
            return {
                "service": service,
                "lines_requested": lines,
                "content": stdout.decode().strip()
            }
        except Exception as e:
            return {"error": str(e)}

    async def check_resource_usage(self):
        """Check CPU/Memory usage of related processes."""
        try:
            # Generic ps command to find python processes related to ai
            # This is a bit heuristics-based
            cmd = "ps aux | grep 'python' | grep -v grep | awk '{print $2, $3, $4, $11}'"
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            lines = stdout.decode().splitlines()
            processes = []
            for line in lines:
                parts = line.split(maxsplit=3)
                if len(parts) >= 4:
                    pid, cpu, mem, cmd_path = parts
                    # Simple filter for relevant scripts
                    if "router" in cmd_path or "agent_runner" in cmd_path or "memory_server" in cmd_path:
                        processes.append({
                            "pid": pid,
                            "cpu_pct": cpu,
                            "mem_pct": mem,
                            "command": cmd_path
                        })
            
            # Disk usage
            du_proc = await asyncio.create_subprocess_exec(
                "du", "-sh", str(WORKSPACE_ROOT / "agent_data"),
                stdout=asyncio.subprocess.PIPE
            )
            du_out, _ = await du_proc.communicate()
            
            return {
                "host_processes": processes,
                "storage_usage": du_out.decode().strip()
            }
        except Exception as e:
            return {"error": str(e)}

    CONFIG_PATH = WORKSPACE_ROOT / "voice_config.json"

    def _load_voice_config(self):
        if not self.CONFIG_PATH.exists(): return {"provider": "macos", "voice": "alloy"}
        try:
            with open(self.CONFIG_PATH, "r") as f: return json.load(f)
        except: return {"provider": "macos", "voice": "alloy"}

    async def set_voice_preference(self, provider: str, voice: str = "alloy"):
        """Set the default voice provider (macos/openai) and voice ID."""
        if provider not in ["macos", "openai"]: return {"error": f"Invalid provider: {provider}"}
        
        cfg = {"provider": provider, "voice": voice}
        try:
            with open(self.CONFIG_PATH, "w") as f:
                json.dump(cfg, f)
            return {"ok": True, "message": f"Voice preference saved: {provider} ({voice})"}
        except Exception as e:
            return {"error": str(e)}

    async def speak_text(self, text: str, provider: str = "default", voice: str = None):
        """Speak text using host audio output. Provider 'default' uses saved preference."""
        if not text: return {"error": "No text provided"}
        
        # Load defaults if needed
        defaults = self._load_voice_config()
        if provider == "default":
            provider = defaults.get("provider", "macos")
        if not voice:
            voice = defaults.get("voice", "alloy")
        
        if provider == "macos":
            try:
                # Limit length to prevent abundance?
                # Using 'say' command
                proc = await asyncio.create_subprocess_exec("say", text)
                # Don't wait? If we wait, it blocks the agent.
                # But if we don't, we can't report success.
                # Let's wait.
                await proc.wait()
                return {"ok": True, "provider": "macos"}
            except Exception as e:
                return {"error": str(e)}
        
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key: return {"error": "OPENAI_API_KEY not set in MCP environment"}
            
            try:
                import tempfile
                # Secure temp file usually
                tmp_path = os.path.join(tempfile.gettempdir(), f"speech_{os.getpid()}.mp3")
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                   resp = await client.post(
                       "https://api.openai.com/v1/audio/speech",
                       headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                       json={"model": "tts-1", "input": text, "voice": voice}
                   )
                   if resp.status_code != 200:
                       return {"error": f"OpenAI API Error: {resp.text}"}
                   
                   with open(tmp_path, "wb") as f:
                       f.write(resp.content)
                
                # Play with afplay (macOS default media player)
                proc = await asyncio.create_subprocess_exec("afplay", tmp_path)
                await proc.wait()
                
                # Cleanup
                if os.path.exists(tmp_path): os.remove(tmp_path)
                
                return {"ok": True, "provider": "openai"}
            except Exception as e:
                # Auto-Fallback to Local
                sys.stderr.write(f"[WARN] OpenAI TTS failed: {e}. Falling back to macOS.\n")
                return await self.speak_text(text, provider="macos")
        
        return {"error": f"Unknown provider '{provider}'"}

    async def trigger_maintenance(self, type: str):
        """Trigger maintenance tasks: 'backup' or 'consolidation'."""
        if type not in ["backup", "consolidation"]:
            return {"error": "Invalid type. Use 'backup' or 'consolidation'."}
            
        # Agent Runner Endpoints (assuming existing structure or newly added)
        # Note: I added /admin/tasks/consolidation. Do I have backup?
        # memory_tasks.py has backup. If I didn't verify an endpoint for backup, I can't call it via HTTP easily.
        # But 'process_memories' tool exists in memory_server which calls consolidation.
        
        url = f"{AGENT_URL}/admin/tasks/{type}"
        # Wait, I didn't add /admin/tasks/backup yet. 
        # I only added /admin/tasks/consolidation.
        # But let's assume I'll add it or it fails safely.
        
        if type == "consolidation":
             url = f"{AGENT_URL}/admin/tasks/consolidation"
        
        # For backup, if no endpoint, maybe fallback to shell script?
        if type == "backup":
            script = WORKSPACE_ROOT / "bin" / "backup_memory.sh"
            if script.exists():
                try:
                    proc = await asyncio.create_subprocess_exec(str(script))
                    await proc.wait()
                    return {"ok": True, "method": "shell_script", "exit_code": proc.returncode}
                except Exception as e:
                     return {"error": str(e)}
            return {"error": "Backup script not found and no API endpoint verified."}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url)
                return {"ok": resp.status_code == 200, "status": resp.status_code, "body": resp.json() if resp.status_code==200 else resp.text}
            except Exception as e:
                return {"error": str(e)}

    async def add_mcp_server(self, name: str, config: dict):
        """Add or update an MCP server configuration safely."""
        import yaml
        config_path = WORKSPACE_ROOT / "config" / "config.yaml"
        if not config_path.exists():
            return {"error": f"Config not found at {config_path}"}
            
        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}
            
            if "mcp_servers" not in data:
                data["mcp_servers"] = {}
                
            data["mcp_servers"][name] = config
            
            with open(config_path, "w") as f:
                yaml.dump(data, f, sort_keys=False, indent=2)
                
            return {"ok": True, "message": f"Added server '{name}' to config.yaml"}
        except Exception as e:
            return {"error": str(e)}

    async def remove_mcp_server(self, name: str):
        """Remove an MCP server configuration."""
        import yaml
        config_path = WORKSPACE_ROOT / "config" / "config.yaml"
        if not config_path.exists():
            return {"error": f"Config not found at {config_path}"}
            
        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}
            
            if "mcp_servers" in data and name in data["mcp_servers"]:
                del data["mcp_servers"][name]
                
                with open(config_path, "w") as f:
                    yaml.dump(data, f, sort_keys=False, indent=2)
                return {"ok": True, "message": f"Removed server '{name}'"}
            else:
                return {"error": f"Server '{name}' not found"}
        except Exception as e:
            return {"error": str(e)}

async def main():
    server = Server("system-control")
    controller = SystemControlServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name="get_system_health", description="Check connection/uptime of Router and Agent Runner.", inputSchema={"type":"object","properties":{}}),
            Tool(name="read_service_logs", description="Read recent logs from router, agent_runner, or ollama.", inputSchema={"type":"object","properties":{"service":{"type":"string","enum":["router","agent_runner","ollama"]}, "lines":{"type":"integer","default":20}},"required":["service"]}),
            Tool(name="check_resource_usage", description="Check CPU/RAM of orchestration processes and disk usage.", inputSchema={"type":"object","properties":{}}),
            Tool(name="trigger_maintenance", description="Trigger 'backup' or 'consolidation' tasks.", inputSchema={"type":"object","properties":{"type":{"type":"string","enum":["backup","consolidation"]}},"required":["type"]}),
            Tool(name="speak_text", description="Audio Output: Speak text aloud on the host machine using macOS or OpenAI.", inputSchema={"type":"object","properties":{"text":{"type":"string"},"provider":{"type":"string","enum":["default","macos","openai"],"default":"default"},"voice":{"type":"string","default":""}},"required":["text"]}),
            Tool(name="set_voice_preference", description="Configure default voice provider (macos/openai).", inputSchema={"type":"object","properties":{"provider":{"type":"string","enum":["macos","openai"]},"voice":{"type":"string","default":"alloy"}},"required":["provider"]}),
            Tool(name="add_mcp_server", description="Safely add/update an MCP server in config.yaml.", inputSchema={"type":"object","properties":{"name":{"type":"string"},"config":{"type":"object"}},"required":["name","config"]}),
            Tool(name="remove_mcp_server", description="Safely remove an MCP server from config.yaml.", inputSchema={"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}),
        ]

    @server.call_tool()
    async def call_tool(name: str, args: dict) -> list[TextContent]:
        try:
            if name == "get_system_health":
                res = await controller.get_system_health()
            elif name == "read_service_logs":
                res = await controller.read_service_logs(**args)
            elif name == "check_resource_usage":
                res = await controller.check_resource_usage()
            elif name == "trigger_maintenance":
                res = await controller.trigger_maintenance(**args)
            elif name == "speak_text":
                res = await controller.speak_text(**args)
            elif name == "set_voice_preference":
                res = await controller.set_voice_preference(**args)
            elif name == "add_mcp_server":
                res = await controller.add_mcp_server(**args)
            elif name == "remove_mcp_server":
                res = await controller.remove_mcp_server(**args)
            else:
                raise ValueError(f"Unknown tool: {name}")
                
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
        except Exception as e:
             return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
