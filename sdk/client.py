import os
import time
import json
import logging
import httpx
import sys
import argparse
from typing import Optional, Dict, Any, Generator, Union
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sdk")

class AntigravityClient:
    """
    Universal Client SDK for Antigravity Gateway (Port 5455).
    Handles Authentication, Connection, Streaming, and Debugging.
    """
    def __init__(self, base_url: str = "http://localhost:5455", token: Optional[str] = None, debug: bool = False):
        self.base_url = base_url.rstrip("/")
        self.token = token or os.getenv("ROUTER_AUTH_TOKEN")
        self.debug = debug
        
        # Core HTTP client
        self.client = httpx.Client(base_url=self.base_url, timeout=60.0, follow_redirects=True)
        
    def _headers(self, content_type: str = "application/json") -> Dict[str, str]:
        h = {"Content-Type": content_type}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _log_debug(self, method: str, url: str, headers: dict, data: Any = None):
        """Print CURL command for reproduction."""
        if not self.debug: return
        
        cmd = f"curl -X {method} '{self.base_url}{url}'"
        for k, v in headers.items():
            cmd += f" -H '{k}: {v}'"
        
        if data:
            if isinstance(data, dict):
                cmd += f" -d '{json.dumps(data)}'"
            else:
                cmd += " -d [BINARY_DATA]"
                
        print(f"\n[DEBUG] {cmd}\n")

    def wait_for_ready(self, timeout: int = 30) -> bool:
        """Poll /health endpoint until system is online."""
        start = time.time()
        print(f"Waiting for Gateway ({self.base_url}) to be ready...", end="", flush=True)
        
        while time.time() - start < timeout:
            try:
                resp = self.client.get("/health")
                if resp.status_code == 200:
                    print(" Online!")
                    return True
            except Exception:
                pass
            print(".", end="", flush=True)
            time.sleep(1.0)
            
        print(" Timeout.")
        return False

    def health(self) -> Dict[str, Any]:
        resp = self.client.get("/health")
        resp.raise_for_status()
        return resp.json()

    def chat(self, message: str, model: str = "router", history: list = None) -> str:
        """Simple synchronous chat."""
        messages = history or []
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        self._log_debug("POST", "/v1/chat/completions", self._headers(), data)
        
        start = time.time()
        resp = self.client.post("/v1/chat/completions", json=data, headers=self._headers())
        
        if self.debug:
            latency = time.time() - start
            server_time = resp.headers.get("X-Process-Time", "N/A")
            print(f"[DEBUG] Latency: {latency:.4f}s (Server: {server_time}s)")
            
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def chat_stream(self, message: str, model: str = "router", history: list = None) -> Generator[str, None, None]:
        """Generator that yields text chunks from SSE stream."""
        messages = history or []
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        self._log_debug("POST", "/v1/chat/completions", self._headers(), data)
        
        with self.client.stream("POST", "/v1/chat/completions", json=data, headers=self._headers()) as response:
            for line in response.iter_lines():
                if line.startswith("data: "):
                    content = line[6:]
                    if content == "[DONE]": break
                    try:
                        chunk = json.loads(content)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta: yield delta
                    except:
                        pass

    # ingest_file() removed from public API - use ingest_direct() or 'ingest_file' tool instead
    # The Gateway (port 5455) does not currently expose an /ingest endpoint.
    # Use ingest_direct() to target RAG server (port 5555) directly,
    # or use the 'ingest_file' tool via the agent.

    def ingest_direct(self, file_path: str, url: str = "http://localhost:5555") -> Dict[str, Any]:
        """Legacy direct ingest to RAG server (Port 5555)."""
        import requests # Fallback or use httpx
        path = Path(file_path)
        with open(path, "r") as f:
             content = f.read()
             
        # rag_server.py expects JSON body {content: ...}
        data = {
            "content": content,
            "filename": path.name,
            "kb_id": "default"
        }
        resp = httpx.post(f"{url.rstrip('/')}/ingest", json=data, timeout=30.0)
        return resp.json()

# --- CLI Implementation ---
def main():
    parser = argparse.ArgumentParser(description="Antigravity Universal SDK CLI")
    parser.add_argument("--url", default="http://localhost:5455", help="Gateway URL")
    parser.add_argument("--key", help="Auth Token")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Health
    subparsers.add_parser("health", help="Check system health")
    
    # Chat
    chat_parser = subparsers.add_parser("chat", help="Send chat message")
    chat_parser.add_argument("message", type=str, help="Message to send")
    chat_parser.add_argument("--stream", action="store_true", help="Use streaming")
    
    # Ingest
    ingest_parser = subparsers.add_parser("ingest", help="Ingest file (Direct to 5555 for now)")
    ingest_parser.add_argument("file", help="Path to file")
    
    args = parser.parse_args()
    
    client = AntigravityClient(base_url=args.url, token=args.key, debug=args.debug)
    
    try:
        if args.command == "health":
            if client.wait_for_ready(timeout=5):
                print(json.dumps(client.health(), indent=2))
            else:
                sys.exit(1)
                
        elif args.command == "chat":
            if args.stream:
                print("Streaming response: ", end="", flush=True)
                for chunk in client.chat_stream(args.message):
                    print(chunk, end="", flush=True)
                print()
            else:
                print(client.chat(args.message))
                
        elif args.command == "ingest":
            # Using Direct Ingest for now
            print(f"Ingesting {args.file}...", end="")
            res = client.ingest_direct(args.file)
            print(f" Done. Result: {res}")
            
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        if args.debug:
            import traceback
            traceback.print_exc()

class AsyncAntigravityClient:
    """Async version of the Client for high-performance applications."""
    def __init__(self, base_url: str = "http://localhost:5455", token: Optional[str] = None, debug: bool = False):
        self.base_url = base_url.rstrip("/")
        self.token = token or os.getenv("ROUTER_AUTH_TOKEN")
        self.debug = debug
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)

    def _headers(self, content_type: str = "application/json") -> Dict[str, str]:
        h = {"Content-Type": content_type}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def health(self) -> Dict[str, Any]:
        resp = await self.client.get("/health")
        resp.raise_for_status()
        return resp.json()

    async def ingest_direct(self, file_path: str, url: str = "http://localhost:5555") -> Dict[str, Any]:
        """Async Direct Ingest."""
        path = Path(file_path)
        # Note: File I/O is blocking, for true async use aiofiles or offload
        with open(path, "r") as f:
             content = f.read()
        
        data = {
            "content": content,
            "filename": path.name,
            "kb_id": "default"
        }
        # Create a new temporal client for the RAG URL, or just use absolute URL if self.client allowed it (it has base_url set)
        # httpx client with base_url won't like absolute URL override easily? Actually it does.
        # But let's be safe and use a one-off async request
        async with httpx.AsyncClient() as c:
            resp = await c.post(f"{url.rstrip('/')}/ingest", json=data, timeout=30.0)
        return resp.json()

    async def chat(self, message: str, model: str = "router", history: list = None) -> str:
        messages = history or []
        messages.append({"role": "user", "content": message})
        data = {"model": model, "messages": messages, "stream": False}
        resp = await self.client.post("/v1/chat/completions", json=data, headers=self._headers())
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

if __name__ == "__main__":
    main()
