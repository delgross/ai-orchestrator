import logging
from typing import Dict, Any
from fastapi import APIRouter, Body, HTTPException, File, UploadFile, Form

from agent_runner.agent_runner import get_shared_state, get_shared_engine
from agent_runner.config import load_mcp_servers

router = APIRouter()
logger = logging.getLogger("agent_runner.mcp")

@router.post("/admin/mcp/reload-mcp")
async def reload_mcp():
    state = get_shared_state()
    engine = get_shared_engine()
    
    # [NEW] Stop all existing MCP processes so we pick up new env/configs
    try:
        await state.cleanup_all_stdio_processes()
    except Exception as e:
        logger.warning(f"Error cleaning up processes during reload: {e}")
        
    await load_mcp_servers(state)
    await engine.discover_mcp_tools()
    return {"ok": True, "message": "MCP servers and tools reloaded"}

@router.post("/admin/mcp/add")
async def add_mcp_server_endpoint(name: str = Body(...), config: Dict[str, Any] = Body(...)):
    """Dynamically add or update an MCP server and discover its tools."""
    state = get_shared_state()
    engine = get_shared_engine()
    try:
        # 1. Update In-Memory and Config.yaml
        await state.add_mcp_server(name, config)
        
        # 2. Discover Tools for the new server
        await engine.discover_mcp_tools()
        
        return {
            "ok": True, 
            "message": f"Successfully added/updated server '{name}'",
            "server": name,
            "tool_count": len(engine.executor.mcp_tool_cache.get(name, []))
        }
    except Exception as e:
        logger.error(f"Failed to dynamically add MCP server '{name}': {e}")
    except Exception as e:
        logger.error(f"Failed to dynamically add MCP server '{name}': {e}")
        return {"ok": False, "error": str(e)}

@router.post("/admin/mcp/install")
async def install_mcp_package_endpoint(package: str = Body(..., embed=True), name: str = Body(None, embed=True), args: list[str] = Body(None, embed=True)):
    """Install an NPM-based MCP server package automatically."""
    state = get_shared_state()
    engine = get_shared_engine()
    
    # 1. Validation (Same as system_control_server)
    import asyncio
    try:
        val_proc = await asyncio.create_subprocess_exec(
            "npm", "view", package, "name", 
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await val_proc.communicate()
        if val_proc.returncode != 0:
            return {"ok": False, "error": f"NPM Package '{package}' not found."}
    except Exception as e:
        return {"ok": False, "error": f"NPM Validation Error: {e}"}

    # 2. Derive Name
    if not name:
        parts = package.split("/")[-1].replace("server-", "").replace("-mcp", "")
        name = parts
    
    # 3. Construct Config
    cmd_list = ["npx", "-y", package]
    if args:
        cmd_list.extend(args)
        
    config = {
        "cmd": cmd_list,
        "requires_internet": True,
        "type": "stdio"
    }
    
    # 4. Install
    try:
        await state.add_mcp_server(name, config)
        await engine.discover_mcp_tools()
        return {
            "ok": True, 
            "message": f"Installed '{package}' as '{name}'",
            "server": name
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/admin/mcp/remove")
async def remove_mcp_server_endpoint(name: str = Body(..., embed=True)):
    """Dynamically remove an MCP server, terminate its process, and clear tool cache."""
    state = get_shared_state()
    engine = get_shared_engine()
    try:
        # 1. Update State (handles process termination and config persistence)
        success = await state.remove_mcp_server(name)
        
        if success:
            # 2. Clear Tool Cache
            if name in engine.executor.mcp_tool_cache:
                del engine.executor.mcp_tool_cache[name]
                logger.info(f"Cleared tool cache for removed MCP server '{name}'")
            
            return {"ok": True, "message": f"Successfully removed server '{name}'"}
        else:
            return {"ok": False, "error": f"Server '{name}' not found"}
    except Exception as e:
        logger.error(f"Failed to dynamically remove MCP server '{name}': {e}")
        return {"ok": False, "error": str(e)}


@router.post("/admin/mcp/toggle")
async def toggle_mcp_endpoint(name: str = Body(..., embed=True), enabled: bool = Body(..., embed=True)):
    """Dynamically enable or disable an MCP server."""
    state = get_shared_state()
    engine = get_shared_engine()
    
    success = await state.toggle_mcp_server(name, enabled)
    if not success:
        return {"ok": False, "error": "Server not found"}
        
    if not enabled:
         if name in engine.executor.mcp_tool_cache:
             del engine.executor.mcp_tool_cache[name]
    else:
        # Re-discover tools (will re-spawn process if stdio)
        await engine.discover_mcp_tools()
        
    return {"ok": True, "message": f"Server {name} {'enabled' if enabled else 'disabled'}"}

@router.post("/admin/mcp/upload-config")
async def upload_mcp_config(
    file: UploadFile = File(None),
    raw_text: str = Form(None)
):
    """LLM-powered endpoint to parse and add MCP servers from raw text/files."""
    state = get_shared_state()
    content = ""
    if file:
        content = (await file.read()).decode("utf-8")
    elif raw_text:
        content = raw_text
    else:
        raise HTTPException(status_code=400, detail="No file or text provided")

    # Parse with LLM
    from agent_runner.mcp_parser import parse_mcp_config_with_llm
    parsed_servers = await parse_mcp_config_with_llm(state, content)
    
    if not parsed_servers:
        return {"ok": False, "error": "Failed to parse any valid MCP server configurations."}
        
    # Save to config
    from agent_runner.config import save_mcp_to_config
    success = await save_mcp_to_config(parsed_servers)
    
    if success:
        # Reload
        await reload_mcp()
        return {
            "ok": True, 
            "message": f"Successfully processed {len(parsed_servers)} server(s)",
            "added": list(parsed_servers.keys()),
            "total_servers": len(state.mcp_servers)
        }
    else:
        return {"ok": False, "error": "Failed to save configuration to disk."}

@router.get("/admin/mcp/tools")
async def get_all_mcp_tools(server: str = None):
    """Return discovered MCP tools, optionally filtered by server."""
    engine = get_shared_engine()
    cache = engine.executor.mcp_tool_cache
    if server:
        if server in cache:
            return {"ok": True, "server": server, "tools": cache[server]}
        else:
            return {"ok": False, "error": "Server not found in cache", "server": server}
    
    # Return all
    state = get_shared_state()
    # Simple summary of all known servers and their enabled state
    server_meta = {
        name: {"enabled": cfg.get("enabled", True), "type": cfg.get("type", "stdio")} 
        for name, cfg in state.mcp_servers.items()
    }
    
    return {"ok": True, "tools": cache, "servers": server_meta}

@router.post("/admin/mcp/debug/call")
async def debug_mcp_call(
    server: str = Body(..., embed=True),
    tool: str = Body(..., embed=True),
    arguments: Dict[str, Any] = Body({}, embed=True)
):
    """Directly execute an MCP tool via the proxy for debugging."""
    state = get_shared_state()
    from agent_runner.tools.mcp import tool_mcp_proxy
    
    try:
        result = await tool_mcp_proxy(state, server, tool, arguments, bypass_circuit_breaker=True)
        return result
    except Exception as e:
        logger.error(f"Debug MCP call failed: {e}")
        return {"ok": False, "error": str(e)}
