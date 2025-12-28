"""
Refactored Router Entry Point.
Internal logic has been moved to:
- router/main.py (FastAPI app & routes)
- router/config.py (State & Config)
- router/providers.py (LLM logic)
- router/middleware.py (Middleware)
- router/utils.py (Helpers)
"""

from router.main import app
from router.config import state, VERSION

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5455)
