# ~/ai/agent_runner/agent_runner.py
from __future__ import annotations

import asyncio
import json
import os
import shlex
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import logging
from logging.handlers import RotatingFileHandler

import httpx
try:
    import websockets  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    websockets = None  # type: ignore
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


# ============================================================================
# CONFIGURATION
# ============================================================================

# Base URL of your AI gateway (the FastAPI service in router/router.py).
# All LLM calls from the agent-runner go through this gateway.
GATEWAY_BASE = os.getenv("GATEWAY_BASE", "http://127.0.0.1:5455").rstrip("/")

# The *real* model that does reasoning + tool-calling.
# This is a gateway model ID, e.g.:
#   "openai:gpt-4.1-mini"
#   "openrouter:meta-llama/llama-3.1-8b-instruct"
#   "llama3:8b"              (Ollama)
AGENT_MODEL = os.getenv("AGENT_MODEL", "openai:gpt-4.1-mini")

# Root directory for the agent's file sandbox.
# All file operations are forced to live under this directory.
AGENT_FS_ROOT = os.getenv(
    "AGENT_FS_ROOT",
    os.path.expanduser("~/ai/agent_fs_root"),
)

# Optional MCP server list: comma-separated entries name=url (e.g., "local=ws://127.0.0.1:7000,remote=wss://mcp.example.com").
# We treat these as generic HTTP/WS endpoints and use a simple proxy tool.
MCP_SERVERS_RAW = os.getenv("MCP_SERVERS", "")

# Limits for file and tool behavior.
MAX_READ_BYTES = int(os.getenv("AGENT_MAX_READ_BYTES", "200_000"))
MAX_LIST_ENTRIES = int(os.getenv("AGENT_MAX_LIST_ENTRIES", "500"))
MAX_TOOL_STEPS = int(os.getenv("AGENT_MAX_TOOL_STEPS", "8"))

# Timeout for HTTP calls from the agent-runner to the gateway.
HTTP_TIMEOUT_S = float(os.getenv("AGENT_HTTP_TIMEOUT_S", "120.0"))

# System prompt injected as the first message in the agent's tool loop.
# This tells the LLM how to behave and how to use tools.
AGENT_SYSTEM_PROMPT = """
You are a local automation agent with access to workspace file tools.

Workspace rules:
- Your workspace root is a sandbox directory, not the real filesystem.
- Treat all file paths as relative to the workspace root.
- Never assume files or folders exist: check with tools first.

Tool usage:
- When the user asks to view, create, modify, move, or delete files or folders,
  you MUST use the available tools (list_dir, path_info, read_text, write_text,
  append_text, make_dir, remove_file, move_path).
- Do NOT answer such requests by giving shell commands or generic advice.
  Instead, actually carry out the operations with tools and then describe what you did.
- Use list_dir / path_info to understand the workspace before acting.
- Use write_text / append_text for creating or editing files.
- Use make_dir to create directories.
- Use remove_file and move_path for destructive or renaming operations.

Conversation style:
- Keep answers concise and focused on results.
- If a tool call fails, report the error and suggest a reasonable next step.
- Only show file contents when explicitly requested or when the file is very small and directly relevant.
""".strip()


# ============================================================================
# LOGGING SETUP
# ============================================================================

# Configure logging to write to logs directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Dedicated logger for the agent-runner.
logger = logging.getLogger("agent_runner")

if not logger.handlers:
    # Only configure once to avoid duplicate handlers on reload.
    # File handler with rotation (10MB max, keep 5 backups)
    log_file = os.path.join(LOG_DIR, "agent_runner.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s agent_runner %(message)s")
    )
    logger.addHandler(file_handler)
    
    # Also log to console (stdout) for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s agent_runner %(message)s")
    )
    logger.addHandler(console_handler)

# Default log level. You can change this with an env var or here directly.
logger.setLevel(logging.INFO)
logger.propagate = False


def _log_json_event(event: str, **fields: Any) -> None:
    """
    Emit a single-line JSON event for machine parsing, prefixed so it's easy to grep.
    Payload is minimal and redacted/truncated where appropriate.
    """
    try:
        payload = {"event": event, **fields}
        logger.info("JSON_EVENT: %s", json.dumps(payload, ensure_ascii=False))
    except Exception:
        # Never let logging break the app.
        logger.debug("failed to log JSON_EVENT for %s", event)


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(title="Agent Runner", version="0.3.0")

# Add CORS middleware to allow dashboard to fetch from agent-runner
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (dashboard can be on any host/port)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared HTTP client for gateway calls (keeps connections alive).
_http_client: Optional[httpx.AsyncClient] = None

# MCP server registry: name -> config
# config keys:
#   - raw: original URL string from MCP_SERVERS
#   - scheme: "http" | "ws" | "unix" | "stdio"
#   - url: base URL (for http/ws)
#   - token: optional bearer token
#   - uds_path, http_path: for unix sockets
#   - cmd: list[str] for stdio commands
MCP_SERVERS: Dict[str, Dict[str, Any]] = {}


@app.on_event("startup")
async def _on_startup() -> None:
    """
    Called once when the server starts.

    Good place to log configuration so you can see what the process is using
    after a reboot or restart.
    """
    root = Path(AGENT_FS_ROOT).expanduser().resolve()
    logger.info(
        "startup agent-runner",
        extra={
            "gateway_base": GATEWAY_BASE,
            "agent_model": AGENT_MODEL,
            "fs_root": str(root),
            "max_tool_steps": MAX_TOOL_STEPS,
            "mcp_servers": list(MCP_SERVERS.keys()) if MCP_SERVERS else [],
        },
    )
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=HTTP_TIMEOUT_S, trust_env=False)
    _load_mcp_servers()


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


def _load_mcp_servers() -> None:
    """
    Parse MCP_SERVERS env like "local=http://127.0.0.1:7000,remote=https://mcp.example.com".
    Tokens can be provided via env MCP_TOKEN_<NAME> (uppercased name).
    """
    MCP_SERVERS.clear()
    raw = MCP_SERVERS_RAW.strip()
    if not raw:
        return
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry or "=" not in entry:
            continue
        name, url = entry.split("=", 1)
        name = name.strip()
        url = url.strip()
        if not name or not url:
            continue
        token_env = f"MCP_TOKEN_{name.upper()}"
        token = os.getenv(token_env)
        # Determine transport scheme and extras.
        scheme = "http"
        cfg: Dict[str, Any] = {"raw": url, "token": token}
        if url.startswith("ws://") or url.startswith("wss://"):
            scheme = "ws"
            cfg["url"] = url
        elif url.startswith("unix:"):
            # Format: unix:/path/to/socket|/http-path (path defaults to /mcp)
            scheme = "unix"
            payload = url[len("unix:") :]
            uds_path, http_path = (payload.split("|", 1) + ["/mcp"])[:2] if "|" in payload else (payload, "/mcp")
            cfg["uds_path"] = uds_path
            cfg["http_path"] = http_path or "/mcp"
        elif url.startswith("stdio:"):
            # Format: stdio:/path/to/cmd --arg
            scheme = "stdio"
            cmd_str = url[len("stdio:") :].strip()
            cfg["cmd"] = shlex.split(cmd_str) if cmd_str else []
        else:
            # Default: plain HTTP(S) base URL
            scheme = "http"
            cfg["url"] = url.rstrip("/")
        cfg["scheme"] = scheme
        MCP_SERVERS[name] = cfg
    logger.info(
        "loaded MCP servers",
        extra={"servers": list(MCP_SERVERS.keys()), "schemes": {k: v.get("scheme") for k, v in MCP_SERVERS.items()}},
    )


# ============================================================================
# SANDBOXED FILESYSTEM HELPERS
# ============================================================================

def _ensure_fs_root() -> Path:
    """
    Ensure the sandbox root directory exists and return its Path.

    This is the ONLY place we create the directory on disk.
    """
    root = Path(AGENT_FS_ROOT).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _safe_path(user_path: str) -> Path:
    """
    Map a user-specified path into the sandbox root.

    - All paths are treated as relative to AGENT_FS_ROOT.
    - Leading slashes are stripped so the user cannot pass an absolute path.
    - We call .resolve() and then check that the result is still under the root.
      This prevents ".." escape attempts.

    Raises:
        ValueError: if the final path escapes the sandbox root.
    """
    root = _ensure_fs_root()

    if not user_path:
        rel = Path(".")
    else:
        # Strip leading '/' so '/foo' becomes 'foo'.
        user_path = user_path.lstrip("/")
        rel = Path(user_path)

    candidate = (root / rel).resolve()

    # Ensure candidate is within root.
    try:
        candidate.relative_to(root)
    except ValueError:
        raise ValueError("Path escapes sandbox root")

    return candidate


# ============================================================================
# FILE TOOL IMPLEMENTATIONS
# ============================================================================

def tool_list_dir(
    path: str = ".",
    recursive: bool = False,
    max_depth: int = 2,
) -> Dict[str, Any]:
    """
    List files and directories under a path in the sandbox.

    Args:
        path: path relative to the workspace root.
        recursive: if True, recursively walk subdirectories up to max_depth.
        max_depth: depth limit when recursive is True.

    Returns:
        Dict describing the directory and entries.
    """
    root = _ensure_fs_root()
    base = _safe_path(path)

    if not base.exists():
        return {"path": str(base), "exists": False, "entries": []}

    entries: List[Dict[str, Any]] = []

    if not recursive:
        # Simple non-recursive listing.
        for child in base.iterdir():
            entries.append(
                {
                    "name": child.name,
                    "path": str(child.relative_to(root)),
                    "is_dir": child.is_dir(),
                    "size": child.stat().st_size if child.is_file() else None,
                    "modified": child.stat().st_mtime,
                }
            )
            if len(entries) >= MAX_LIST_ENTRIES:
                break
    else:
        # Depth-limited recursive listing.
        base_depth = len(base.parts)
        for child in base.rglob("*"):
            depth = len(child.parts) - base_depth
            if depth > max_depth:
                continue
            entries.append(
                {
                    "name": child.name,
                    "path": str(child.relative_to(root)),
                    "is_dir": child.is_dir(),
                    "size": child.stat().st_size if child.is_file() else None,
                    "modified": child.stat().st_mtime,
                }
            )
            if len(entries) >= MAX_LIST_ENTRIES:
                break

    return {
        "root": str(root),
        "path": str(base.relative_to(root)),
        "exists": True,
        "entries": entries,
        "truncated": len(entries) >= MAX_LIST_ENTRIES,
    }


def tool_path_info(path: str) -> Dict[str, Any]:
    """
    Return metadata about a path in the sandbox (file/dir/exists/size/etc).
    """
    root = _ensure_fs_root()
    p = _safe_path(path)
    exists = p.exists()
    info: Dict[str, Any] = {
        "root": str(root),
        "path": str(p.relative_to(root)),
        "exists": exists,
    }
    if exists:
        st = p.stat()
        info.update(
            {
                "is_file": p.is_file(),
                "is_dir": p.is_dir(),
                "size": st.st_size if p.is_file() else None,
                "modified": st.st_mtime,
            }
        )
    return info


def tool_read_text(path: str, max_bytes: Optional[int] = None) -> Dict[str, Any]:
    """
    Read text from a file in the sandbox (UTF-8, truncated if large).
    """
    root = _ensure_fs_root()
    p = _safe_path(path)
    max_b = max_bytes if max_bytes is not None else MAX_READ_BYTES

    if not p.exists() or not p.is_file():
        return {
            "root": str(root),
            "path": str(p.relative_to(root)),
            "exists": False,
            "is_file": False,
            "content": "",
            "truncated": False,
        }

    data = p.read_bytes()
    truncated = False
    if len(data) > max_b:
        data = data[:max_b]
        truncated = True

    text = data.decode("utf-8", errors="replace")

    return {
        "root": str(root),
        "path": str(p.relative_to(root)),
        "exists": True,
        "is_file": True,
        "content": text,
        "truncated": truncated,
    }


def tool_write_text(path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
    """
    Write text to a file in the sandbox.

    - If overwrite=False and the file exists, returns an error.
    """
    root = _ensure_fs_root()
    p = _safe_path(path)

    if p.exists() and not overwrite:
        return {
            "root": str(root),
            "path": str(p.relative_to(root)),
            "ok": False,
            "error": "File exists and overwrite=False",
        }

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

    return {
        "root": str(root),
        "path": str(p.relative_to(root)),
        "ok": True,
        "bytes_written": len(content.encode("utf-8")),
    }


def tool_append_text(path: str, content: str, create_if_missing: bool = True) -> Dict[str, Any]:
    """
    Append text to a file in the sandbox.

    - If create_if_missing=True and file doesn't exist, it is created.
    """
    root = _ensure_fs_root()
    p = _safe_path(path)

    if not p.exists():
        if not create_if_missing:
            return {
                "root": str(root),
                "path": str(p.relative_to(root)),
                "ok": False,
                "error": "File does not exist and create_if_missing=False",
            }
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "w"
    else:
        mode = "a"

    with p.open(mode, encoding="utf-8") as f:
        f.write(content)

    return {
        "root": str(root),
        "path": str(p.relative_to(root)),
        "ok": True,
        "appended_bytes": len(content.encode("utf-8")),
    }


def tool_make_dir(path: str, parents: bool = True, exist_ok: bool = True) -> Dict[str, Any]:
    """
    Create a directory in the sandbox.
    """
    root = _ensure_fs_root()
    p = _safe_path(path)
    p.mkdir(parents=parents, exist_ok=exist_ok)
    return {
        "root": str(root),
        "path": str(p.relative_to(root)),
        "ok": True,
        "exists": True,
        "is_dir": True,
    }


def tool_remove_file(path: str) -> Dict[str, Any]:
    """
    Delete a file in the sandbox.
    """
    root = _ensure_fs_root()
    p = _safe_path(path)
    if not p.exists():
        return {
            "root": str(root),
            "path": str(p.relative_to(root)),
            "ok": False,
            "error": "Path does not exist",
        }
    if not p.is_file():
        return {
            "root": str(root),
            "path": str(p.relative_to(root)),
            "ok": False,
            "error": "Path is not a file",
        }
    p.unlink()
    return {
        "root": str(root),
        "path": str(p.relative_to(root)),
        "ok": True,
        "deleted": True,
    }


def tool_move_path(src: str, dest: str, overwrite: bool = False) -> Dict[str, Any]:
    """
    Move or rename a file or directory inside the sandbox.
    """
    root = _ensure_fs_root()
    p_src = _safe_path(src)
    p_dest = _safe_path(dest)

    if not p_src.exists():
        return {
            "root": str(root),
            "src": str(p_src.relative_to(root)),
            "dest": str(p_dest.relative_to(root)),
            "ok": False,
            "error": "Source does not exist",
        }

    if p_dest.exists() and not overwrite:
        return {
            "root": str(root),
            "src": str(p_src.relative_to(root)),
            "dest": str(p_dest.relative_to(root)),
            "ok": False,
            "error": "Destination exists and overwrite=False",
        }

    p_dest.parent.mkdir(parents=True, exist_ok=True)
    p_src.rename(p_dest)

    return {
        "root": str(root),
        "src": str(p_src.relative_to(root)),
        "dest": str(p_dest.relative_to(root)),
        "ok": True,
        "moved": True,
    }


async def tool_mcp_proxy(server: str, tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Proxy a tool call to a configured MCP server over HTTP using JSON-RPC 2.0.
    Assumes:
      - POST {base} with body:
          {"jsonrpc":"2.0","method":"tools/call",
           "params":{"name": <tool>,"arguments": {...}},
           "id": <int>}
      - Response is standard JSON-RPC with either "result" or "error".
    """
    if not MCP_SERVERS:
        return {"ok": False, "error": "No MCP servers configured"}
    cfg = MCP_SERVERS.get(server)
    if not cfg:
        return {"ok": False, "error": f"Unknown MCP server '{server}'"}
    scheme = cfg.get("scheme", "http")
    headers = {"Content-Type": "application/json"}
    if cfg.get("token"):
        headers["Authorization"] = f"Bearer {cfg['token']}"
    # Build JSON-RPC request
    rpc_body = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool,
            "arguments": arguments,
        },
        "id": int(time.time() * 1000),
    }
    # HTTP / HTTPS transport
    if scheme == "http":
        if _http_client is None:
            return {"ok": False, "error": "HTTP client not initialized"}
        url = cfg.get("url")
        if not url:
            return {"ok": False, "error": "MCP server missing URL"}
        try:
            resp = await _http_client.post(url, json=rpc_body, headers=headers)
        except Exception as e:
            return {"ok": False, "error": f"Failed to reach MCP server: {e}"}
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            _log_json_event(
                "mcp_http_error",
                server=server,
                scheme=scheme,
                status_code=resp.status_code,
            )
            return {"ok": False, "status": resp.status_code, "error": detail}
        try:
            data = resp.json()
        except Exception:
            return {"ok": False, "error": "MCP server returned non-JSON response"}

    # Unix domain socket over HTTP
    elif scheme == "unix":
        uds_path = cfg.get("uds_path")
        http_path = cfg.get("http_path", "/mcp")
        if not uds_path:
            return {"ok": False, "error": "MCP unix server missing uds_path"}
        transport = httpx.AsyncHTTPTransport(uds=uds_path)
        async with httpx.AsyncClient(transport=transport, timeout=HTTP_TIMEOUT_S) as client:
            try:
                resp = await client.post(f"http://mcp{http_path}", json=rpc_body, headers=headers)
            except Exception as e:
                _log_json_event("mcp_unix_error", server=server, scheme=scheme, error=str(e))
                return {"ok": False, "error": f"Failed to reach MCP unix server: {e}"}
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            _log_json_event(
                "mcp_unix_http_error",
                server=server,
                scheme=scheme,
                status_code=resp.status_code,
            )
            return {"ok": False, "status": resp.status_code, "error": detail}
        try:
            data = resp.json()
        except Exception:
            return {"ok": False, "error": "MCP unix server returned non-JSON response"}

    # WebSocket transport
    elif scheme == "ws":
        if websockets is None:
            return {"ok": False, "error": "websockets library not available for ws transport"}
        url = cfg.get("url")
        if not url:
            return {"ok": False, "error": "MCP ws server missing URL"}
        # Convert headers dict to list of (name, value) for websockets
        extra_headers = [(k, v) for k, v in headers.items()]
        try:
            async with websockets.connect(url, extra_headers=extra_headers) as ws:  # type: ignore
                await ws.send(json.dumps(rpc_body))
                resp_text = await ws.recv()
        except Exception as e:
            _log_json_event("mcp_ws_error", server=server, scheme=scheme, error=str(e))
            return {"ok": False, "error": f"Failed to reach MCP ws server: {e}"}
        try:
            data = json.loads(resp_text)
        except Exception:
            _log_json_event("mcp_ws_bad_json", server=server, scheme=scheme)
            return {"ok": False, "error": "MCP ws server returned non-JSON response"}

    # Stdio transport (spawn a process and speak JSON-RPC over stdin/stdout)
    elif scheme == "stdio":
        cmd = cfg.get("cmd") or []
        if not cmd:
            return {"ok": False, "error": "MCP stdio server missing command"}
        # Pass token via environment if present.
        env = os.environ.copy()
        if cfg.get("token"):
            env[f"MCP_TOKEN_{server.upper()}"] = cfg["token"]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
        except Exception as e:
            _log_json_event("mcp_stdio_start_error", server=server, scheme=scheme, error=str(e))
            return {"ok": False, "error": f"Failed to start MCP stdio server: {e}"}
        try:
            assert proc.stdin is not None and proc.stdout is not None
            line = json.dumps(rpc_body) + "\n"
            proc.stdin.write(line.encode("utf-8"))
            await proc.stdin.drain()
            resp_line = await proc.stdout.readline()
            if not resp_line:
                stderr = await proc.stderr.read() if proc.stderr else b""
                _log_json_event("mcp_stdio_no_data", server=server, scheme=scheme)
                return {"ok": False, "error": f"MCP stdio server returned no data", "stderr": stderr.decode("utf-8", errors="replace")}
            data = json.loads(resp_line.decode("utf-8", errors="replace"))
        except Exception as e:
            _log_json_event("mcp_stdio_io_error", server=server, scheme=scheme, error=str(e))
            return {"ok": False, "error": f"MCP stdio interaction failed: {e}"}
        finally:
            try:
                proc.kill()
            except Exception:
                pass

    else:
        _log_json_event("mcp_unsupported_scheme", server=server, scheme=scheme)
        return {"ok": False, "error": f"Unsupported MCP scheme '{scheme}'"}

    # JSON-RPC success or error handling (shared)
    if isinstance(data, dict) and "error" in data:
        _log_json_event("mcp_rpc_error", server=server, scheme=scheme)
        return {"ok": False, "rpc_error": data["error"]}
    result = data.get("result") if isinstance(data, dict) else None
    return {"ok": True, "result": result if result is not None else data}


# Map tool name -> Python implementation.
TOOL_IMPLS = {
    "list_dir": tool_list_dir,
    "path_info": tool_path_info,
    "read_text": tool_read_text,
    "write_text": tool_write_text,
    "append_text": tool_append_text,
    "make_dir": tool_make_dir,
    "remove_file": tool_remove_file,
    "move_path": tool_move_path,
}
if MCP_SERVERS_RAW.strip():
    TOOL_IMPLS["mcp_proxy"] = tool_mcp_proxy


# ============================================================================
# OPENAI-STYLE TOOL DEFINITIONS (for the LLM)
# ============================================================================

# These definitions are sent to the LLM via the gateway.
# The "function" blocks must match OpenAI's tools/function-calling schema.
FILE_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files and directories under a path in the sandboxed workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to the workspace root. Use '.' for the root.",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to walk subdirectories.",
                        "default": False,
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum depth when recursive=true.",
                        "default": 2,
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "path_info",
            "description": "Get info (exists, type, size, modified time) about a path in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to the workspace root.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_text",
            "description": "Read text from a file in the workspace (UTF-8).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace root.",
                    },
                    "max_bytes": {
                        "type": "integer",
                        "description": "Maximum bytes to read.",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_text",
            "description": "Write text to a file in the workspace (overwriting optionally).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace root.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Text content to write.",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite if the file already exists.",
                        "default": False,
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "append_text",
            "description": "Append text to a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace root.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Text content to append.",
                    },
                    "create_if_missing": {
                        "type": "boolean",
                        "description": "Create the file if it does not exist.",
                        "default": True,
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "make_dir",
            "description": "Create a directory in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path relative to workspace root.",
                    },
                    "parents": {
                        "type": "boolean",
                        "description": "Create parent directories if needed.",
                        "default": True,
                    },
                    "exist_ok": {
                        "type": "boolean",
                        "description": "Do not error if directory already exists.",
                        "default": True,
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_file",
            "description": "Delete a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace root.",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "move_path",
            "description": "Move or rename a file or directory inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "src": {
                        "type": "string",
                        "description": "Source path relative to workspace root.",
                    },
                    "dest": {
                        "type": "string",
                        "description": "Destination path relative to workspace root.",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite existing destination.",
                        "default": False,
                    },
                },
                "required": ["src", "dest"],
            },
        },
    },
]

# Placeholder for future MCP-based tools. Stays empty for now but is reflected
# in the root() route so you can see what's wired.
MCP_TOOLS: List[Dict[str, Any]] = []
# Add a generic MCP proxy tool if servers are configured.
if MCP_SERVERS_RAW.strip():
    MCP_TOOLS.append(
        {
            "type": "function",
            "function": {
                "name": "mcp_proxy",
                "description": "Call a remote MCP server tool by name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "server": {
                            "type": "string",
                            "description": "MCP server name (from MCP_SERVERS env).",
                        },
                        "tool": {
                            "type": "string",
                            "description": "Tool name on the MCP server.",
                        },
                        "arguments": {
                            "type": "object",
                            "description": "Arguments object to pass to the MCP tool.",
                        },
                    },
                    "required": ["server", "tool", "arguments"],
                },
            },
        }
    )


# ============================================================================
# CORE: call the gateway with tools enabled
# ============================================================================

async def _call_gateway_with_tools(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Call your AI gateway with tools enabled.

    We send:
      - model:      AGENT_MODEL (the real model to use)
      - messages:   full conversation (including system prompt + tool messages)
      - tools:      FILE_TOOLS + MCP_TOOLS
      - tool_choice: "auto"
      - stream:     False (non-streaming only here)
    """
    url = f"{GATEWAY_BASE}/v1/chat/completions"
    payload = {
        "model": AGENT_MODEL,
        "messages": messages,
        "tools": FILE_TOOLS + MCP_TOOLS,
        "tool_choice": "auto",
        "stream": False,
    }

    logger.info(
        "call gateway with tools",
        extra={
            "url": url,
            "model": AGENT_MODEL,
            "num_messages": len(messages),
        },
    )

    if _http_client is None:
        # Should not happen after startup, but guard just in case.
        raise HTTPException(status_code=500, detail="HTTP client not initialized")

    resp = await _http_client.post(url, json=payload)
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        logger.error(
            "gateway error",
            extra={"status_code": resp.status_code, "error": str(e)},
        )
        _log_json_event(
            "gateway_error",
            status_code=resp.status_code,
            error=str(e),
            model=AGENT_MODEL,
        )
        raise HTTPException(
            status_code=resp.status_code,
            detail={"upstream_error": str(e), "body": detail},
        )
    data = resp.json()
    logger.info(
        "gateway response ok",
        extra={
            "model": data.get("model"),
            "choices": len(data.get("choices", [])),
        },
    )
    return data


# ============================================================================
# EXECUTE A SINGLE TOOL CALL
# ============================================================================

async def _execute_tool_call(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single tool_call from the LLM.

    The LLM sends tool_calls with structure like:
      {
        "id": "call_123",
        "type": "function",
        "function": {
          "name": "write_text",
          "arguments": "{\"path\": \"notes/plan.txt\", \"content\": \"...\"}"
        }
      }

    We:
      - Parse the JSON 'arguments' string into a dict.
      - Dispatch to TOOL_IMPLS[name].
      - Return a result dict {ok: bool, result: ..., error: ...}
    """
    fn = tool_call.get("function") or {}
    name = fn.get("name")
    args_str = fn.get("arguments") or "{}"

    logger.info("execute tool_call", extra={"tool_name": name})

    if not name or name not in TOOL_IMPLS:
        return {"ok": False, "error": f"Unknown tool '{name}'"}

    try:
        args = json.loads(args_str)
        if not isinstance(args, dict):
            raise ValueError("Tool arguments must be a JSON object")
    except Exception as e:
        return {"ok": False, "error": f"Failed to parse arguments JSON: {e}"}

    impl = TOOL_IMPLS[name]
    try:
        if asyncio.iscoroutinefunction(impl):
            result = await impl(**args)
        else:
            result = impl(**args)
        logger.info("tool execution ok", extra={"tool_name": name})
        _log_json_event("tool_ok", tool_name=name)
        return {"ok": True, "result": result}
    except Exception as e:
        logger.exception("tool execution failed", extra={"tool_name": name})
        _log_json_event("tool_error", tool_name=name, error=str(e))
        return {"ok": False, "error": f"Exception in tool '{name}': {e}"}


# ============================================================================
# TOOL-DRIVEN AGENT LOOP
# ============================================================================

async def _agent_loop(user_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tool-using agent loop:

      1. Start with system prompt + user messages.
      2. Ask the LLM (via gateway) with tools enabled.
      3. If there are tool_calls:
         - Execute each tool.
         - Append tool results as "tool" messages.
         - Go back to step 2.
      4. If there are no tool_calls:
         - Return the final LLM completion.

    We cap the number of tool steps with MAX_TOOL_STEPS to avoid infinite loops.
    """
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
    ]
    messages.extend(user_messages)

    logger.info(
        "agent_loop start",
        extra={
            "num_user_messages": len(user_messages),
            "max_tool_steps": MAX_TOOL_STEPS,
        },
    )

    for step in range(MAX_TOOL_STEPS):
        logger.info("agent_loop step", extra={"step": step})
        completion = await _call_gateway_with_tools(messages)

        choices = completion.get("choices") or []
        if not choices:
            # No choices at all – just return whatever we got.
            logger.warning("agent_loop: no choices in completion")
            completion["model"] = "agent:mcp"
            return completion

        choice = choices[0]
        msg = choice.get("message") or {}

        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            # No tool calls = final answer.
            logger.info("agent_loop: no tool_calls, returning final answer")
            completion["model"] = "agent:mcp"
            return completion

        logger.info(
            "agent_loop: received tool_calls",
            extra={"num_tool_calls": len(tool_calls)},
        )

        # Add assistant message with tool_calls.
        messages.append(
            {
                "role": "assistant",
                "content": msg.get("content"),
                "tool_calls": tool_calls,
            }
        )

        # Execute each tool call and append its result as a "tool" message.
        for tc in tool_calls:
            tc_id = tc.get("id") or ""
            fn = tc.get("function") or {}
            name = fn.get("name") or "unknown"

            result = await _execute_tool_call(tc)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "name": name,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    # If we hit this, we exceeded MAX_TOOL_STEPS.
    logger.warning("agent_loop: max tool steps exceeded, summarizing final state")
    completion = await _call_gateway_with_tools(messages)
    completion["model"] = "agent:mcp"
    return completion


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/")
async def root():
    """
    Simple health/config endpoint.

    You already use this with:
        curl -sS http://127.0.0.1:5460/ | python -m json.tool
    """
    return {
        "name": "agent-runner",
        "ok": True,
        "gateway_base": GATEWAY_BASE,
        "agent_model": AGENT_MODEL,
        "fs_root": str(Path(AGENT_FS_ROOT).expanduser().resolve()),
        "tools": [t["function"]["name"] for t in FILE_TOOLS],
        "mcp_tools": [t.get("function", {}).get("name") for t in MCP_TOOLS],
        "max_tool_steps": MAX_TOOL_STEPS,
        "mcp_servers": list(MCP_SERVERS.keys()) if MCP_SERVERS else [],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """
    OpenAI-style entrypoint.

    This is what the gateway (router.py) calls when you use model "agent:mcp".

    Important behavior:
    - We ignore the incoming 'model' field for routing; AGENT_MODEL is used
      for the actual reasoning and tool-calling.
    - We do, however, preserve the *reported* model in the response as
      whatever the caller requested (usually "agent:mcp"), so LibreChat and
      other clients see a stable model ID.
    """
    body = await request.json()
    messages = body.get("messages") or []
    if not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="messages must be a list")

    # Normalize messages -> just role/content pairs.
    norm_msgs: List[Dict[str, Any]] = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        role = m.get("role")
        content = m.get("content")
        if not role:
            continue
        norm_msgs.append({"role": role, "content": content})

    logger.info(
        "incoming chat",
        extra={
            "num_messages": len(norm_msgs),
            "reported_model": body.get("model", "agent:mcp"),
        },
    )

    completion = await _agent_loop(norm_msgs)

    # Make sure the outward model is what the caller asked for (default agent:mcp).
    completion["model"] = body.get("model", "agent:mcp")
    completion.setdefault("created", int(time.time()))
    completion.setdefault("object", "chat.completion")
    completion.setdefault("id", completion.get("id") or f"chatcmpl-{int(time.time() * 1000)}")

    return JSONResponse(completion)