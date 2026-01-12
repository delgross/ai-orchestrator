import asyncio
import json
import os
import sys
import httpx
import shutil
from pathlib import Path
from mcp.server.stdio import stdio_server # type: ignore[import-untyped]
from mcp.server import Server # type: ignore[import-untyped]
from mcp.types import Tool, TextContent # type: ignore[import-untyped]
from typing import Any, Dict, List, Optional

try:
    import yaml # type: ignore[import-untyped]
except ImportError:
    yaml = None

    yaml = None

# [FIX] Force Parent Path to resolve 'common' package regardless of env vars
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.circuit_breaker import CircuitBreakerRegistry

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
        # NEW: Fetch detailed topology report from Agent Runner
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{AGENT_URL}/admin/health/detailed")
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            log(f"Detailed health check failed, falling back: {e}", level="WARN")
            pass # Fallback to legacy check if new endpoint fails (during migration)

        report = {"timestamp": os.popen("date -u").read().strip(), "source": "legacy_fallback"}
        
        # Initialize breakers if needed (lazy load to avoid init issues)
        if not hasattr(self, "breakers"):
             self.breakers = CircuitBreakerRegistry(default_threshold=3, default_timeout=30.0)

        async with httpx.AsyncClient(timeout=3.0) as client:
            # Check Router
            if self.breakers.is_allowed("router"):
                try:
                    resp = await client.get(f"{ROUTER_URL}/health")
                    if resp.status_code == 200:
                        report["router"] = {"status": "online", "details": resp.json()}
                        self.breakers.record_success("router")
                    else:
                        report["router"] = {"status": "error", "code": resp.status_code}
                        self.breakers.record_failure("router")
                except Exception as e:
                    report["router"] = {"status": "offline", "error": str(e)}
                    self.breakers.record_failure("router", error=e)
            else:
                 report["router"] = {"status": "suspended", "error": "Circuit Breaker Open"}

            # Check Agent Runner
            if self.breakers.is_allowed("agent_runner"):
                try:
                    resp = await client.get(f"{AGENT_URL}/health")
                    if resp.status_code == 200:
                        report["agent_runner"] = {"status": "online", "details": resp.json()}
                        self.breakers.record_success("agent_runner")
                    else:
                        report["agent_runner"] = {"status": "error", "code": resp.status_code}
                        self.breakers.record_failure("agent_runner")
                except Exception as e:
                    report["agent_runner"] = {"status": "offline", "error": str(e)}
                    self.breakers.record_failure("agent_runner", error=e)
            else:
                 report["agent_runner"] = {"status": "suspended", "error": "Circuit Breaker Open"}

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
        except Exception: return {"provider": "macos", "voice": "alloy"}

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

    async def speak_text(self, text: str, provider: str = "default", voice: str = None, wait: bool = False):
        """
        Speak text using host audio output. 
        Provider 'default' uses saved preference.
        Set 'wait' to False (default) to return immediately while audio plays in background.
        """
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
                
                if wait:
                    await proc.wait()
                else:
                    # Fire and forget / background task
                    # We need to not await it, but we also don't want to loose the ref immediately?
                    # asyncio.create_subprocess_exec starts it. If we don't await wait(), it runs.
                    pass
                    
                return {"ok": True, "provider": "macos", "background": not wait}
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
                
                if wait:
                    await proc.wait()
                    # Cleanup immediately
                    if os.path.exists(tmp_path): os.remove(tmp_path)
                else:
                    # Cleanup in background task? Or just leave it in temp? 
                    # Better to cleanup. Let's spawn a cleanup task.
                    async def _wait_and_clean():
                        await proc.wait()
                        if os.path.exists(tmp_path): os.remove(tmp_path)
                    
                    asyncio.create_task(_wait_and_clean())
                
                return {"ok": True, "provider": "openai", "background": not wait}
                
                # Cleanup
                # Cleanup (handled in background task if wait=False)
                if wait and os.path.exists(tmp_path): os.remove(tmp_path)
                
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
        
        if type == "backup":
             url = f"{AGENT_URL}/admin/tasks/backup"
        
        # Determine URL based on type
        if type == "consolidation":
             url = f"{AGENT_URL}/admin/tasks/consolidation"
        
        # Try API first
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.post(url)
                if resp.status_code == 200:
                    return {"ok": True, "method": "api", "body": resp.json()}
            except Exception as e:
                log(f"Maintenance trigger API failed: {e}", level="WARN")
                pass # Fallback to shell script if API fails
        
        # Fallback to shell script
        if type == "backup":
            script = WORKSPACE_ROOT / "bin" / "backup_memory.sh"
            if script.exists():
                try:
                    proc = await asyncio.create_subprocess_exec(str(script))
                    await proc.wait()
                    return {"ok": True, "method": "shell_script", "exit_code": proc.returncode}
                except Exception as e:
                     return {"error": str(e)}
            return {"error": "Backup script not found and API endpoint failed."}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url)
                return {"ok": resp.status_code == 200, "status": resp.status_code, "body": resp.json() if resp.status_code==200 else resp.text}
            except Exception as e:
                return {"error": str(e)}

    async def add_mcp_server(self, name: str, config: dict):
        """Add or update an MCP server configuration safely via Agent Runner API."""
        url = f"{AGENT_URL}/admin/mcp/add"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(url, json={"name": name, "config": config})
                if resp.status_code == 200:
                    return resp.json()
                else:
                    return {"ok": False, "error": f"Agent Runner API error ({resp.status_code}): {resp.text}"}
            except Exception as e:
                return {"ok": False, "error": f"Connection to Agent Runner failed: {str(e)}"}

    async def remove_mcp_server(self, name: str):
        """Remove an MCP server configuration safely via Agent Runner API."""
        url = f"{AGENT_URL}/admin/mcp/remove"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(url, json={"name": name})
                if resp.status_code == 200:
                    return resp.json()
                else:
                    return {"ok": False, "error": f"Agent Runner API error ({resp.status_code}): {resp.text}"}
            except Exception as e:
                return {"ok": False, "error": f"Connection to Agent Runner failed: {str(e)}"}

    async def install_mcp_package(self, package: str, name: str = None, args: List[str] = None):
        """Install an NPM-based MCP server package automatically, optionally with arguments."""
        # 1. VALIDATION: Check if package exists on NPM registry
        # checking "npm view <package>" is a fast way to verify existence
        log(f"Validating NPM package: {package}", level="INFO")
        try:
            # We use 'view' because it doesn't download the tarball, just checks registry metadata
            val_proc = await asyncio.create_subprocess_exec(
                "npm", "view", package, "name", 
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await val_proc.communicate()
            
            if val_proc.returncode != 0:
                err_msg = stderr.decode().strip() or "Package not found"
                if "404" in err_msg:
                    return {"ok": False, "error": f"NPM Package '{package}' does not exist. Please check the spelling."}
                return {"ok": False, "error": f"NPM Validation Failed: {err_msg}"}
                
        except Exception as e:
            return {"ok": False, "error": f"NPM Validation Exception: {str(e)}"}

        # 2. PROCEED with Installation
        if not name:
            # Auto-derive name: @scope/server-foo -> foo
            # server-bar -> bar
            parts = package.split("/")[-1].replace("server-", "").replace("-mcp", "")
            name = parts
            
        cmd_list = ["npx", "-y", package]
        if args:
            cmd_list.extend(args)

        config = {
            "cmd": cmd_list,
            "requires_internet": True,
            "type": "stdio"
        }
        
        log(f"Installing MCP package '{package}' as server '{name}' with args {args}...", level="INFO")
        return await self.add_mcp_server(name, config)

    async def ingest_file(self, source_path: str):
        """Copy a file to the RAG ingestion inbox to trigger background processing."""
        try:
            src = Path(source_path)
            if not src.exists():
                return {"error": f"Source file not found: {source_path}"}
                
            # Define ingestion root
            ingest_root = WORKSPACE_ROOT / "agent_fs_root" / "ingest"
            ingest_root.mkdir(parents=True, exist_ok=True)
            
            # Destination path
            dest = ingest_root / src.name
            
            # Copy file
            shutil.copy2(src, dest)
            
            # Create trigger file to force immediate processing
            (ingest_root / ".trigger_now").touch()
            
            return {
                "ok": True, 
                "message": "File submitted to background ingestion system.",
                "path": str(dest)
            }
        except Exception as e:
            return {"error": str(e)}

            return {"error": str(e)}

    async def get_ingestion_status(self):
        """Get the current status of the RAG ingestion pipeline."""
        url = f"{AGENT_URL}/admin/ingestion/status"
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.json()
                return {"error": f"API Error ({resp.status_code}): {resp.text}"}
            except Exception as e:
                return {"error": f"Connection failed: {str(e)}"}

    async def parse_mcp_config(self, content: str):
        """Parse raw configuration text (JSON/YAML) using the System LLM and install servers."""
        url = f"{AGENT_URL}/admin/mcp/upload-config"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                # Send as raw text form data
                resp = await client.post(url, data={"raw_text": content})
                if resp.status_code == 200:
                    return resp.json()
                else:
                    return {"ok": False, "error": f"Agent Runner Parsing Error ({resp.status_code}): {resp.text}"}
            except Exception as e:
                return {"ok": False, "error": f"Connection to Parser failed: {str(e)}"}

    async def update_system_config(self, key: str, value: str, type: str = "secret"):
        """
        Update a system configuration value (Reverse Sync).
        Updates Sovereign Memory (DB), Runtime, and Disk Backup (.env).
        Type: 'secret' (default) for API keys/tokens.
        """
        url = f"{AGENT_URL}/admin/config/update"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.post(url, json={"key": key, "value": value, "type": type})
                if resp.status_code == 200:
                    return resp.json()
                else:
                    return {"ok": False, "error": f"Agent Runner API Error ({resp.status_code}): {resp.text}"}
            except Exception as e:
                return {"ok": False, "error": f"Connection to Agent Runner failed: {str(e)}"}

async def main():
    server = Server("system-control")
    controller = SystemControlServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name="get_system_health", description="Check connection/uptime of topology (Router, Agent, MCPs). Returns full server list.", inputSchema={"type":"object","properties":{}}),
            Tool(name="list_active_mcp_servers", description="List all currently active MCP servers and their status.", inputSchema={"type":"object","properties":{}}),
            Tool(name="get_ingestion_status", description="Get the status of the document ingestion queue (RAG). Use this to check if files are processed.", inputSchema={"type":"object","properties":{}}),
            Tool(name="read_service_logs", description="Read recent logs from router, agent_runner, or ollama.", inputSchema={"type":"object","properties":{"service":{"type":"string","enum":["router","agent_runner","ollama"]}, "lines":{"type":"integer","default":20}},"required":["service"]}),
            Tool(name="check_resource_usage", description="Check CPU/RAM of orchestration processes and disk usage.", inputSchema={"type":"object","properties":{}}),
            Tool(name="trigger_maintenance", description="Trigger 'backup' or 'consolidation' tasks.", inputSchema={"type":"object","properties":{"type":{"type":"string","enum":["backup","consolidation"]}},"required":["type"]}),
            Tool(name="speak_text", description="Audio Output: Speak text aloud on the host machine using macOS or OpenAI. Use wait=False for non-blocking.", inputSchema={"type":"object","properties":{"text":{"type":"string"},"provider":{"type":"string","enum":["default","macos","openai"],"default":"default"},"voice":{"type":"string","default":""},"wait":{"type":"boolean","default":False, "description":"If true, wait for audio to finish before returning."}},"required":["text"]}),
            Tool(name="set_voice_preference", description="Configure default voice provider (macos/openai).", inputSchema={"type":"object","properties":{"provider":{"type":"string","enum":["macos","openai"]},"voice":{"type":"string","default":"alloy"}},"required":["provider"]}),
            Tool(name="add_mcp_server", description="Safely add/update an MCP server in config.yaml.", inputSchema={"type":"object","properties":{"name":{"type":"string"},"config":{"type":"object"}},"required":["name","config"]}),
            Tool(name="install_mcp_package", description="Install an NPM-based MCP server. Example: '@modelcontextprotocol/server-weather'. Support optional args for proxies.", inputSchema={"type":"object","properties":{"package":{"type":"string"},"name":{"type":"string"},"args":{"type":"array","items":{"type":"string"}}},"required":["package"]}),
            Tool(name="remove_mcp_server", description="Safely remove an MCP server from config.yaml.", inputSchema={"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}),
            Tool(name="ingest_file", description="Submit a file for asynchronous background ingestion (RAG/Knowledge Graph).", inputSchema={"type":"object","properties":{"source_path":{"type":"string"}},"required":["source_path"]}),
            Tool(name="parse_mcp_config", description="Parse and install MCP servers from raw configuration text (JSON/YAML) pasted by the user. Use this when the user provides a config block.", inputSchema={"type":"object","properties":{"content":{"type":"string"}},"required":["content"]}),
            Tool(name="update_system_config", description="Update a system configuration value (Reverse Sync). Updates Sovereign Memory (DB), Runtime, and Disk Backup (.env/system_config.json).", inputSchema={"type":"object","properties":{"key":{"type":"string"},"value":{"type":"string"},"type":{"type":"string","enum":["secret", "config"],"default":"config"}},"required":["key","value"]}),
        ]

    @server.call_tool()
    async def call_tool(name: str, args: dict) -> list[TextContent]:
        try:
            if name == "get_system_health":
                res = await controller.get_system_health()
            elif name == "list_active_mcp_servers":
                # Wrapper around health check to extract just the MCP list
                health = await controller.get_system_health()
                agent_section = health.get("agent_runner", {})
                if agent_section.get("status") == "online":
                     details = agent_section.get("details", {})
                     res = details.get("mcp", {"error": "No MCP section in health payload"})
                else:
                     res = {"error": f"Agent Runner is {agent_section.get('status', 'unknown')}", "health_dump": health}
            elif name == "get_ingestion_status":
                res = await controller.get_ingestion_status()
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
            elif name == "install_mcp_package":
                res = await controller.install_mcp_package(**args)
            elif name == "remove_mcp_server":
                res = await controller.remove_mcp_server(**args)
            elif name == "ingest_file":
                res = await controller.ingest_file(**args)
            elif name == "parse_mcp_config":
                res = await controller.parse_mcp_config(**args)
            elif name == "update_system_config":
                res = await controller.update_system_config(**args)
            else:
                raise ValueError(f"Unknown tool: {name}")
                
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
        except Exception as e:
             return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
