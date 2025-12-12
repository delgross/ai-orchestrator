# ~/ai/agent_runner/agent_runner.py
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
GATEWAY_BASE = os.getenv("GATEWAY_BASE", "http://127.0.0.1:5455").rstrip("/")
# Underlying LLM actually doing the reasoning + tool calling
AGENT_MODEL = os.getenv("AGENT_MODEL", "openai:gpt-4.1-mini")

# Sandbox root for file tools
AGENT_FS_ROOT = os.getenv(
    "AGENT_FS_ROOT",
    os.path.expanduser("~/ai/agent_fs_root"),
)

# Max size / limits
MAX_READ_BYTES = int(os.getenv("AGENT_MAX_READ_BYTES", "200000"))
MAX_LIST_ENTRIES = int(os.getenv("AGENT_MAX_LIST_ENTRIES", "500"))
MAX_TOOL_STEPS = int(os.getenv("AGENT_MAX_TOOL_STEPS", "8"))

HTTP_TIMEOUT_S = float(os.getenv("AGENT_HTTP_TIMEOUT_S", "120.0"))

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

app = FastAPI(title="Agent Runner", version="0.2.0")


# ---------------------------------------------------------------------
# Helper: sandbox paths
# ---------------------------------------------------------------------
def _ensure_fs_root() -> Path:
    root = Path(AGENT_FS_ROOT).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _safe_path(user_path: str) -> Path:
    """
    Map a user-specified path into the sandbox root.
    Everything is treated as relative to AGENT_FS_ROOT.
    """
    root = _ensure_fs_root()

    if not user_path:
        rel = Path(".")
    else:
        # Strip leading slashes to prevent absolute paths escaping the root
        user_path = user_path.lstrip("/")
        rel = Path(user_path)

    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        raise ValueError("Path escapes sandbox root")

    return candidate


# ---------------------------------------------------------------------
# File tools implementations
# ---------------------------------------------------------------------
def tool_list_dir(
    path: str = ".",
    recursive: bool = False,
    max_depth: int = 2,
) -> Dict[str, Any]:
    root = _ensure_fs_root()
    base = _safe_path(path)

    if not base.exists():
        return {"path": str(base), "exists": False, "entries": []}

    entries: List[Dict[str, Any]] = []

    if not recursive:
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


# Map tool name -> callable
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


# ---------------------------------------------------------------------
# OpenAI-style tool definitions
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# Core LLM call through your gateway (with tools)
# ---------------------------------------------------------------------
async def _call_gateway_with_tools(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Call your AI gateway with tools enabled.
    """
    url = f"{GATEWAY_BASE}/v1/chat/completions"
    payload = {
        "model": AGENT_MODEL,
        "messages": messages,
        "tools": FILE_TOOLS,
        "tool_choice": "auto",
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_S) as client:
        resp = await client.post(url, json=payload)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise HTTPException(
                status_code=resp.status_code,
                detail={"upstream_error": str(e), "body": detail},
            )
        return resp.json()


def _execute_tool_call(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single tool_call from the LLM.
    """
    fn = tool_call.get("function") or {}
    name = fn.get("name")
    args_str = fn.get("arguments") or "{}"

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
        result = impl(**args)
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": f"Exception in tool '{name}': {e}"}


async def _agent_loop(user_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tool-using agent loop:
      messages -> LLM -> (maybe tool_calls) -> execute -> add tool outputs -> LLM -> ... -> final answer
    """
    # Start conversation with system prompt
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
    ]
    messages.extend(user_messages)

    for _ in range(MAX_TOOL_STEPS):
        completion = await _call_gateway_with_tools(messages)

        choices = completion.get("choices") or []
        if not choices:
            completion["model"] = "agent:mcp"
            return completion

        choice = choices[0]
        msg = choice.get("message") or {}

        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            # final answer
            completion["model"] = "agent:mcp"
            return completion

        # Add the assistant message with tool_calls to the conversation
        messages.append(
            {
                "role": "assistant",
                "content": msg.get("content"),
                "tool_calls": tool_calls,
            }
        )

        # For each tool_call, execute and add tool responses
        for tc in tool_calls:
            tc_id = tc.get("id") or ""
            fn = tc.get("function") or {}
            name = fn.get("name") or "unknown"

            result = _execute_tool_call(tc)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "name": name,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    # Max steps exceeded; one last call to summarize
    completion = await _call_gateway_with_tools(messages)
    completion["model"] = "agent:mcp"
    return completion


# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "name": "agent-runner",
        "ok": True,
        "gateway_base": GATEWAY_BASE,
        "agent_model": AGENT_MODEL,
        "fs_root": str(Path(AGENT_FS_ROOT).expanduser().resolve()),
        "tools": [t["function"]["name"] for t in FILE_TOOLS],
        "max_tool_steps": MAX_TOOL_STEPS,
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """
    OpenAI-style entrypoint.

    We ignore the incoming 'model' value and always use AGENT_MODEL
    under the hood, but we set 'model'='agent:mcp' in the response so
    callers (gateway, LibreChat, etc.) see a stable model id.
    """
    body = await request.json()
    messages = body.get("messages") or []
    if not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="messages must be a list")

    # normalize messages to dicts with 'role' and 'content'
    norm_msgs: List[Dict[str, Any]] = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        role = m.get("role")
        content = m.get("content")
        if not role:
            continue
        norm_msgs.append({"role": role, "content": content})

    completion = await _agent_loop(norm_msgs)

    # force outward model id to "agent:mcp"
    completion["model"] = body.get("model", "agent:mcp")
    completion.setdefault("created", int(time.time()))
    completion.setdefault("object", "chat.completion")
    completion.setdefault("id", completion.get("id") or f"chatcmpl-{int(time.time()*1000)}")

    return JSONResponse(completion)