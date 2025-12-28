"""
Logging utilities for structured JSON event logging.

Provides consistent JSON event logging across all system components.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger("logging_utils")


def log_json_event(event: str, request_id: Optional[str] = None, **fields: Any) -> None:
    """
    Emit a JSON_EVENT line for machine parsing.
    
    Args:
        event: Event name/type
        request_id: Optional request ID for request tracking
        **fields: Additional fields to include in the event
    """
    try:
        payload = {"event": event, **fields}
        if request_id:
            payload["request_id"] = request_id
        logger.info("JSON_EVENT: %s", json.dumps(payload, ensure_ascii=False))
    except Exception:
        logger.debug("failed to log JSON_EVENT for %s", event)





