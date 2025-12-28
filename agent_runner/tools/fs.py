import shutil
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner")

def _ensure_fs_root(state: AgentState) -> Path:
    root = Path(state.agent_fs_root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root

def _safe_path(state: AgentState, user_path: str) -> Path:
    root = _ensure_fs_root(state)
    if not user_path:
        rel = Path(".")
    else:
        user_path = user_path.lstrip("/")
        rel = Path(user_path)
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        raise ValueError("Path escapes sandbox root")
    return candidate

def tool_list_dir(state: AgentState, path: str = ".", recursive: bool = False, max_depth: int = 2) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    base = _safe_path(state, path)
    if not base.exists():
        return {"path": str(base), "exists": False, "entries": []}
    entries: List[Dict[str, Any]] = []
    if not recursive:
        for child in base.iterdir():
            entries.append({
                "name": child.name, "path": str(child.relative_to(root)),
                "is_dir": child.is_dir(), "size": child.stat().st_size if child.is_file() else None,
                "modified": child.stat().st_mtime,
            })
            if len(entries) >= state.max_list_entries: break
    else:
        base_depth = len(base.parts)
        for child in base.rglob("*"):
            depth = len(child.parts) - base_depth
            if depth > max_depth: continue
            entries.append({
                "name": child.name, "path": str(child.relative_to(root)),
                "is_dir": child.is_dir(), "size": child.stat().st_size if child.is_file() else None,
                "modified": child.stat().st_mtime,
            })
            if len(entries) >= state.max_list_entries: break
    return {
        "root": str(root), "path": str(base.relative_to(root)),
        "exists": True, "entries": entries, "truncated": len(entries) >= state.max_list_entries,
    }

def tool_path_info(state: AgentState, path: str) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    p = _safe_path(state, path)
    exists = p.exists()
    info = {"root": str(root), "path": str(p.relative_to(root)), "exists": exists}
    if exists:
        st = p.stat()
        info.update({"is_file": p.is_file(), "is_dir": p.is_dir(), "size": st.st_size if p.is_file() else None, "modified": st.st_mtime})
    return info

def tool_read_text(state: AgentState, path: str, max_bytes: Optional[int] = None) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    p = _safe_path(state, path)
    max_b = max_bytes if max_bytes is not None else state.max_read_bytes
    if not p.exists() or not p.is_file():
        return {"root": str(root), "path": str(p.relative_to(root)), "exists": False, "is_file": False, "content": "", "truncated": False}
    data = p.read_bytes()
    truncated = False
    if len(data) > max_b:
        data = data[:max_b]
        truncated = True
    return {"root": str(root), "path": str(p.relative_to(root)), "exists": True, "is_file": True, "content": data.decode("utf-8", errors="replace"), "truncated": truncated}

def tool_write_text(state: AgentState, path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    p = _safe_path(state, path)
    if p.exists() and not overwrite:
        return {"root": str(root), "path": str(p.relative_to(root)), "ok": False, "error": "File exists and overwrite=False"}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {"root": str(root), "path": str(p.relative_to(root)), "ok": True, "bytes_written": len(content.encode("utf-8"))}

def tool_append_text(state: AgentState, path: str, content: str, create_if_missing: bool = True) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    p = _safe_path(state, path)
    if not p.exists():
        if not create_if_missing:
            return {"root": str(root), "path": str(p.relative_to(root)), "ok": False, "error": "File does not exist and create_if_missing=False"}
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "w"
    else: mode = "a"
    with p.open(mode, encoding="utf-8") as f:
        f.write(content)
    return {"root": str(root), "path": str(p.relative_to(root)), "ok": True, "appended_bytes": len(content.encode("utf-8"))}

def tool_make_dir(state: AgentState, path: str, parents: bool = True, exist_ok: bool = True) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    p = _safe_path(state, path)
    p.mkdir(parents=parents, exist_ok=exist_ok)
    return {"root": str(root), "path": str(p.relative_to(root)), "ok": True, "exists": True, "is_dir": True}

def tool_remove_file(state: AgentState, path: str) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    p = _safe_path(state, path)
    if not p.exists(): return {"root": str(root), "path": str(p.relative_to(root)), "ok": False, "error": "Path does not exist"}
    if not p.is_file(): return {"root": str(root), "path": str(p.relative_to(root)), "ok": False, "error": "Path is not a file"}
    p.unlink()
    return {"root": str(root), "path": str(p.relative_to(root)), "ok": True, "deleted": True}

def tool_move_path(state: AgentState, src: str, dest: str, overwrite: bool = False) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    p_src = _safe_path(state, src)
    p_dest = _safe_path(state, dest)
    if not p_src.exists(): return {"root": str(root), "src": str(p_src.relative_to(root)), "dest": str(p_dest.relative_to(root)), "ok": False, "error": "Source does not exist"}
    if p_dest.exists() and not overwrite: return {"root": str(root), "src": str(p_src.relative_to(root)), "dest": str(p_dest.relative_to(root)), "ok": False, "error": "Destination exists and overwrite=False"}
    p_dest.parent.mkdir(parents=True, exist_ok=True)
    p_src.rename(p_dest)
    return {"root": str(root), "src": str(p_src.relative_to(root)), "dest": str(p_dest.relative_to(root)), "ok": True, "moved": True}

def tool_remove_dir(state: AgentState, path: str, recursive: bool = True) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    p = _safe_path(state, path)
    if not p.exists(): return {"root": str(root), "path": str(p.relative_to(root)), "ok": False, "error": "Path does not exist"}
    if not p.is_dir(): return {"root": str(root), "path": str(p.relative_to(root)), "ok": False, "error": "Path is not a directory"}
    if recursive: shutil.rmtree(p)
    else:
        try: p.rmdir()
        except OSError as e: return {"root": str(root), "path": str(p.relative_to(root)), "ok": False, "error": f"Directory not empty: {str(e)}"}
    return {"root": str(root), "path": str(p.relative_to(root)), "ok": True, "deleted": True}

def tool_copy_file(state: AgentState, src: str, dest: str, overwrite: bool = False) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    p_src = _safe_path(state, src)
    p_dest = _safe_path(state, dest)
    if not p_src.exists(): return {"root": str(root), "src": str(p_src.relative_to(root)), "dest": str(p_dest.relative_to(root)), "ok": False, "error": "Source does not exist"}
    if not p_src.is_file(): return {"root": str(root), "src": str(p_src.relative_to(root)), "dest": str(p_dest.relative_to(root)), "ok": False, "error": "Source is not a file"}
    if p_dest.exists() and not overwrite: return {"root": str(root), "src": str(p_src.relative_to(root)), "dest": str(p_dest.relative_to(root)), "ok": False, "error": "Destination exists and overwrite=False"}
    p_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p_src, p_dest)
    return {"root": str(root), "src": str(p_src.relative_to(root)), "dest": str(p_dest.relative_to(root)), "ok": True, "copied": True, "size": p_dest.stat().st_size}

def tool_copy_path(state: AgentState, src: str, dest: str, overwrite: bool = False) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    p_src = _safe_path(state, src)
    p_dest = _safe_path(state, dest)
    if not p_src.exists(): return {"root": str(root), "src": str(p_src.relative_to(root)), "dest": str(p_dest.relative_to(root)), "ok": False, "error": "Source does not exist"}
    if p_dest.exists() and not overwrite: return {"root": str(root), "src": str(p_src.relative_to(root)), "dest": str(p_dest.relative_to(root)), "ok": False, "error": "Destination exists and overwrite=False"}
    p_dest.parent.mkdir(parents=True, exist_ok=True)
    if p_src.is_file():
        shutil.copy2(p_src, p_dest)
        files_copied = 1
    else:
        shutil.copytree(p_src, p_dest, dirs_exist_ok=overwrite)
        files_copied = sum(1 for _ in p_dest.rglob("*") if _.is_file())
    return {"root": str(root), "src": str(p_src.relative_to(root)), "dest": str(p_dest.relative_to(root)), "ok": True, "copied": True, "files_copied": files_copied}

def tool_find_files(state: AgentState, path: str = ".", pattern: Optional[str] = None, extension: Optional[str] = None, max_results: int = 100) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    base = _safe_path(state, path)
    if not base.exists() or not base.is_dir(): return {"root": str(root), "path": str(base.relative_to(root)), "ok": False, "error": "Path does not exist", "files": []}
    files: List[Dict[str, Any]] = []
    search_pattern = pattern if pattern else (f"**/*{extension if extension.startswith('.') else f'.{extension}'}" if extension else "**/*")
    for file_path in base.glob(search_pattern):
        if file_path.is_file() and len(files) < max_results:
            files.append({"name": file_path.name, "path": str(file_path.relative_to(root)), "size": file_path.stat().st_size, "modified": file_path.stat().st_mtime})
    return {"root": str(root), "path": str(base.relative_to(root)), "ok": True, "pattern": search_pattern, "files": files, "count": len(files), "truncated": len(files) >= max_results}

def tool_batch_operations(state: AgentState, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = []
    for i, op in enumerate(operations):
        op_type = op.get("operation")
        try:
            if op_type == "write": res = tool_write_text(state, op["path"], op["content"], overwrite=op.get("overwrite", False))
            elif op_type == "append": res = tool_append_text(state, op["path"], op["content"], create_if_missing=op.get("create_if_missing", True))
            elif op_type == "copy": res = tool_copy_path(state, op["src"], op["dest"], overwrite=op.get("overwrite", False))
            elif op_type == "move": res = tool_move_path(state, op["src"], op["dest"], overwrite=op.get("overwrite", False))
            elif op_type == "remove_file": res = tool_remove_file(state, op["path"])
            elif op_type == "remove_dir": res = tool_remove_dir(state, op["path"], recursive=op.get("recursive", True))
            elif op_type == "make_dir": res = tool_make_dir(state, op["path"], parents=op.get("parents", True), exist_ok=op.get("exist_ok", True))
            else: res = {"ok": False, "error": f"Unknown operation: {op_type}"}
            results.append({"index": i, "operation": op_type, "result": res})
        except Exception as e: results.append({"index": i, "operation": op_type, "result": {"ok": False, "error": str(e)}})
    success_count = sum(1 for r in results if r["result"].get("ok", False))
    return {"root": str(state.agent_fs_root), "ok": True, "total": len(operations), "succeeded": success_count, "failed": len(operations) - success_count, "results": results}

def tool_query_static_resources(state: AgentState, query: Optional[str] = None, resource_name: Optional[str] = None, list_all: bool = False, max_content_length: int = 500000) -> Dict[str, Any]:
    root = _ensure_fs_root(state)
    static_resources_dir = root / "Static Resources"
    if not static_resources_dir.exists(): return {"ok": False, "error": "Static Resources directory does not exist", "path": str(static_resources_dir.relative_to(root))}
    supported_extensions = ('.md', '.txt', '.rst', '.adoc')
    all_resources = []
    for file_path in static_resources_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            stat = file_path.stat()
            all_resources.append({"name": file_path.name, "path": str(file_path.relative_to(root)), "relative_path": str(file_path.relative_to(static_resources_dir)), "size": stat.st_size, "modified": stat.st_mtime})
    result = {"ok": True, "resources_dir": str(static_resources_dir.relative_to(root)), "total_resources": len(all_resources)}
    if list_all: result["resources"] = all_resources; return result
    if resource_name:
        matching = [r for r in all_resources if r["name"] == resource_name or r["name"].lower() == resource_name.lower()]
        if not matching: return {"ok": False, "error": f"Resource '{resource_name}' not found", "available_resources": [r["name"] for r in all_resources]}
        resource = matching[0]
        try:
            content = (root / resource["path"]).read_text(encoding="utf-8", errors="replace")
            truncated = len(content) > max_content_length
            if truncated: content = content[:max_content_length] + f"\n\n... (truncated)"
            result.update({"resource": resource, "content": content, "content_length": len(content), "truncated": truncated})
        except Exception as e: return {"ok": False, "error": f"Failed to read resource: {str(e)}", "resource": resource}
        return result
    if query:
        ql = query.lower()
        matching_resources = []
        for r in all_resources:
            if ql in r["name"].lower(): matching_resources.append(r); continue
            try:
                content = (root / r["path"]).read_text(encoding="utf-8", errors="replace")
                if ql in content.lower():
                    idx = content.lower().find(ql)
                    snippet = content[max(0, idx - 100):min(len(content), idx + len(query) + 100)]
                    matching_resources.append({**r, "snippet": snippet})
            except: continue
        result.update({"query": query, "matching_resources": matching_resources, "match_count": len(matching_resources)})
        return result
    result["resources"] = all_resources; return result

_watch_state = {}
def tool_watch_path(state: AgentState, path: str = ".") -> Dict[str, Any]:
    # Placeholder for simple watcher
    root = _ensure_fs_root(state)
    base = _safe_path(state, path)
    return {"ok": True, "path": str(base.relative_to(root)), "watching": True}
