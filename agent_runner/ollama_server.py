#!/usr/bin/env python3
"""
Ollama MCP Server - Manage Ollama models via MCP protocol.

Provides tools for:
- Listing models
- Pulling/downloading models
- Deleting models
- Showing model details
- Generating embeddings
- Managing model parameters
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path
import httpx
import time

# Configuration
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://127.0.0.1:11434").rstrip("/")
HTTP_TIMEOUT = float(os.getenv("OLLAMA_HTTP_TIMEOUT", "300.0"))

# Set up logging to stderr
def log(msg: str, level: str = "INFO", exc_info: bool = False):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"{timestamp} {level} ollama_server {msg}"
    if exc_info:
        import traceback
        log_msg += f"\n{traceback.format_exc()}"
    sys.stderr.write(f"{log_msg}\n")
    sys.stderr.flush()

logger = logging.getLogger("ollama_server")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s ollama_server %(message)s"))
logger.addHandler(handler)


class OllamaServer:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=HTTP_TIMEOUT)
        self.base_url = OLLAMA_BASE

    async def _call_ollama_api(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a call to Ollama API."""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                r = await self.client.get(url, **kwargs)
            elif method.upper() == "POST":
                r = await self.client.post(url, **kwargs)
            elif method.upper() == "DELETE":
                r = await self.client.delete(url, **kwargs)
            else:
                return {"ok": False, "error": f"Unsupported method: {method}"}
            
            if r.status_code >= 400:
                error_text = r.text
                try:
                    error_json = r.json()
                    error_text = error_json.get("error", error_text)
                except:
                    pass
                return {"ok": False, "error": error_text, "status_code": r.status_code}
            
            try:
                return {"ok": True, "data": r.json()}
            except:
                return {"ok": True, "data": {"text": r.text}}
        except httpx.TimeoutException as e:
            log(f"Ollama API timeout: {e}", "ERROR")
            return {"ok": False, "error": f"Request to Ollama timed out: {str(e)}", "error_type": "timeout"}
        except httpx.ConnectError as e:
            log(f"Ollama connection error: {e}", "ERROR")
            return {"ok": False, "error": f"Cannot connect to Ollama at {self.base_url}: {str(e)}", "error_type": "connection"}
        except Exception as e:
            log(f"API call failed: {e}", "ERROR")
            return {"ok": False, "error": str(e), "error_type": "unknown"}

    async def list_models(self) -> Dict[str, Any]:
        """List all available Ollama models."""
        result = await self._call_ollama_api("GET", "/api/tags")
        if not result.get("ok"):
            return result
        
        models = result["data"].get("models", [])
        model_list = []
        for m in models:
            if isinstance(m, dict):
                model_info = {
                    "name": m.get("name", ""),
                    "model": m.get("model", ""),
                    "size": m.get("size", 0),
                    "digest": m.get("digest", ""),
                    "modified_at": m.get("modified_at", ""),
                }
                model_list.append(model_info)
        
        return {"ok": True, "models": model_list, "count": len(model_list)}

    async def show_model(self, model: str) -> Dict[str, Any]:
        """Show detailed information about a model."""
        result = await self._call_ollama_api("POST", "/api/show", json={"name": model})
        if not result.get("ok"):
            return result
        
        return {"ok": True, "model_info": result["data"]}

    async def pull_model(self, model: str, stream: bool = False) -> Dict[str, Any]:
        """Pull/download a model from Ollama library."""
        payload = {"name": model}
        if stream:
            payload["stream"] = True
        
        result = await self._call_ollama_api("POST", "/api/pull", json=payload)
        return result

    async def delete_model(self, model: str) -> Dict[str, Any]:
        """Delete a model from Ollama."""
        result = await self._call_ollama_api("DELETE", "/api/delete", json={"name": model})
        return result

    async def copy_model(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy a model to a new name."""
        result = await self._call_ollama_api("POST", "/api/copy", json={"source": source, "destination": destination})
        return result

    async def generate_embeddings(self, model: str, prompt: str) -> Dict[str, Any]:
        """Generate embeddings for text using an Ollama embedding model."""
        result = await self._call_ollama_api("POST", "/api/embeddings", json={"model": model, "prompt": prompt})
        if not result.get("ok"):
            return result
        
        data = result["data"]
        embedding = data.get("embedding", [])
        return {
            "ok": True,
            "embedding": embedding,
            "dimension": len(embedding) if embedding else 0
        }

    async def generate_text(self, model: str, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate text using /api/generate (non-chat endpoint)."""
        payload = {"model": model, "prompt": prompt, "stream": False}
        if options:
            payload["options"] = options
        
        result = await self._call_ollama_api("POST", "/api/generate", json=payload)
        if not result.get("ok"):
            return result
        
        data = result["data"]
        return {
            "ok": True,
            "response": data.get("response", ""),
            "done": data.get("done", False),
            "context": data.get("context", []),
            "total_duration": data.get("total_duration", 0),
            "load_duration": data.get("load_duration", 0),
            "prompt_eval_count": data.get("prompt_eval_count", 0),
            "eval_count": data.get("eval_count", 0),
        }

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# MCP Server implementation
server = OllamaServer()

def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP JSON-RPC requests."""
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params", {})
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "ollama-server",
                    "version": "1.0.0"
                }
            }
        }
    
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "list_models",
                        "description": "List all available Ollama models with their details (name, size, digest, modified date).",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": "show_model",
                        "description": "Show detailed information about a specific model including parameters, template, and system prompt.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "model": {
                                    "type": "string",
                                    "description": "Model name (e.g., 'mistral:latest', 'llama3:8b')"
                                }
                            },
                            "required": ["model"]
                        }
                    },
                    {
                        "name": "pull_model",
                        "description": "Download/pull a model from the Ollama library. Use this to install new models.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "model": {
                                    "type": "string",
                                    "description": "Model name to pull (e.g., 'llama3.2:3b', 'qwen2.5:72b')"
                                },
                                "stream": {
                                    "type": "boolean",
                                    "description": "Whether to stream the download progress (default: false)",
                                    "default": False
                                }
                            },
                            "required": ["model"]
                        }
                    },
                    {
                        "name": "delete_model",
                        "description": "Delete a model from Ollama to free up disk space.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "model": {
                                    "type": "string",
                                    "description": "Model name to delete (e.g., 'mistral:latest')"
                                }
                            },
                            "required": ["model"]
                        }
                    },
                    {
                        "name": "copy_model",
                        "description": "Copy a model to a new name (useful for creating model variants).",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "source": {
                                    "type": "string",
                                    "description": "Source model name"
                                },
                                "destination": {
                                    "type": "string",
                                    "description": "Destination model name"
                                }
                            },
                            "required": ["source", "destination"]
                        }
                    },
                    {
                        "name": "generate_embeddings",
                        "description": "Generate embeddings for text using an Ollama embedding model.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "model": {
                                    "type": "string",
                                    "description": "Embedding model name (e.g., 'embeddinggemma:300m', 'mxbai-embed-large:latest')"
                                },
                                "prompt": {
                                    "type": "string",
                                    "description": "Text to generate embeddings for"
                                }
                            },
                            "required": ["model", "prompt"]
                        }
                    },
                    {
                        "name": "generate_text",
                        "description": "Generate text using /api/generate endpoint (non-chat, simple prompt-response).",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "model": {
                                    "type": "string",
                                    "description": "Model name"
                                },
                                "prompt": {
                                    "type": "string",
                                    "description": "Prompt text"
                                },
                                "options": {
                                    "type": "object",
                                    "description": "Optional model parameters (num_ctx, temperature, etc.)"
                                }
                            },
                            "required": ["model", "prompt"]
                        }
                    }
                ]
            }
        }
    
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        async def execute_tool():
            if tool_name == "list_models":
                return await server.list_models()
            elif tool_name == "show_model":
                return await server.show_model(arguments.get("model", ""))
            elif tool_name == "pull_model":
                return await server.pull_model(
                    arguments.get("model", ""),
                    arguments.get("stream", False)
                )
            elif tool_name == "delete_model":
                return await server.delete_model(arguments.get("model", ""))
            elif tool_name == "copy_model":
                return await server.copy_model(
                    arguments.get("source", ""),
                    arguments.get("destination", "")
                )
            elif tool_name == "generate_embeddings":
                return await server.generate_embeddings(
                    arguments.get("model", ""),
                    arguments.get("prompt", "")
                )
            elif tool_name == "generate_text":
                return await server.generate_text(
                    arguments.get("model", ""),
                    arguments.get("prompt", ""),
                    arguments.get("options")
                )
            else:
                return {"ok": False, "error": f"Unknown tool: {tool_name}"}
        
        # Execute tool asynchronously
        try:
            result = asyncio.run(execute_tool())
            # Log successful tool execution (debug level)
            if result.get("ok"):
                log(f"Tool '{tool_name}' executed successfully", "DEBUG")
            else:
                log(f"Tool '{tool_name}' returned error: {result.get('error', 'Unknown error')}", "WARNING")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        except Exception as e:
            log(f"Tool execution error for '{tool_name}': {e}", "ERROR", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": f"Tool execution failed: {str(e)}",
                    "tool": tool_name
                }
            }
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }


async def main():
    """Main MCP server loop (stdio)."""
    log("Ollama MCP server starting...")
    
    # Read from stdin, write to stdout
    while True:
        try:
            line = await asyncio.to_thread(sys.stdin.readline)
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            request = json.loads(line)
            response = handle_request(request)
            
            # Write response to stdout
            print(json.dumps(response))
            sys.stdout.flush()
            
        except json.JSONDecodeError as e:
            log(f"JSON decode error: {e}", "ERROR")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {e}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            log(f"Unexpected error: {e}", "ERROR")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
    
    await server.close()
    log("Ollama MCP server shutting down...")


if __name__ == "__main__":
    asyncio.run(main())

