"""
API Integration Tools

Provides utilities for making HTTP requests, handling webhooks, and integrating with external APIs.
"""

import httpx
import json
import logging
from typing import Dict, Any, Optional, List
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.api_integration")

async def tool_http_request(state: AgentState, method: str, url: str, headers: Optional[Dict[str, str]] = None,
                          body: Optional[Any] = None, params: Optional[Dict[str, Any]] = None,
                          timeout: int = 30) -> Dict[str, Any]:
    """Make an HTTP request to an external API.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: The URL to request
        headers: Optional headers dictionary
        body: Optional request body (will be JSON-encoded if dict)
        params: Optional query parameters
        timeout: Request timeout in seconds

    Returns:
        Dict containing response data and metadata
    """
    try:
        # Prepare headers
        request_headers = headers or {}
        if not any(k.lower() == 'user-agent' for k in request_headers):
            request_headers['User-Agent'] = 'Antigravity-AI-Agent/1.0'

        # Prepare body
        request_body = None
        if body is not None:
            if isinstance(body, dict):
                request_body = json.dumps(body)
                request_headers['Content-Type'] = 'application/json'
            else:
                request_body = str(body)

        # Make request
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method.upper(),
                url,
                headers=request_headers,
                content=request_body,
                params=params
            )

            # Parse response
            response_data = None
            content_type = response.headers.get('content-type', '')

            try:
                if 'application/json' in content_type:
                    response_data = response.json()
                else:
                    response_data = response.text
            except:
                response_data = response.text

            return {
                "ok": True,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response_data,
                "url": str(response.url),
                "method": method.upper(),
                "content_type": content_type,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }

    except httpx.TimeoutException:
        return {
            "ok": False,
            "error": f"Request timed out after {timeout} seconds",
            "error_type": "timeout"
        }
    except httpx.ConnectError as e:
        return {
            "ok": False,
            "error": f"Connection failed: {str(e)}",
            "error_type": "connection_error"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"HTTP request failed: {str(e)}",
            "error_type": "request_error"
        }

async def tool_create_webhook(state: AgentState, endpoint: str, secret: Optional[str] = None,
                            method: str = "POST", headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Create a webhook configuration for receiving HTTP callbacks.

    Args:
        endpoint: The webhook endpoint URL
        secret: Optional secret for webhook verification
        method: HTTP method for webhook calls (default: POST)
        headers: Optional headers to include in webhook requests

    Returns:
        Dict containing webhook configuration
    """
    try:
        import uuid

        webhook_id = str(uuid.uuid4())
        webhook_config = {
            "id": webhook_id,
            "endpoint": endpoint,
            "method": method.upper(),
            "headers": headers or {},
            "secret": secret,
            "created_at": "now",  # Would use proper timestamp in production
            "active": True
        }

        # In a real implementation, this would be stored in a database
        # For now, we'll just return the configuration
        logger.info(f"Created webhook {webhook_id} for endpoint {endpoint}")

        return {
            "ok": True,
            "webhook": webhook_config,
            "message": "Webhook configuration created. Note: This is a demonstration - actual webhook storage would require database integration."
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Webhook creation failed: {str(e)}",
            "error_type": "creation_error"
        }

async def tool_call_webhook(state: AgentState, url: str, payload: Any,
                          headers: Optional[Dict[str, str]] = None, method: str = "POST") -> Dict[str, Any]:
    """Call a webhook endpoint with data.

    Args:
        url: The webhook URL to call
        payload: The data to send (will be JSON-encoded)
        headers: Optional headers
        method: HTTP method (default: POST)

    Returns:
        Dict containing the webhook call result
    """
    try:
        # Use the existing http_request tool functionality
        result = await tool_http_request(state, method, url, headers, payload)

        if result["ok"]:
            return {
                "ok": True,
                "webhook_called": True,
                "response": result,
                "message": f"Webhook called successfully with status {result['status_code']}"
            }
        else:
            return {
                "ok": False,
                "webhook_called": False,
                "error": result["error"],
                "error_type": result.get("error_type", "webhook_error")
            }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Webhook call failed: {str(e)}",
            "error_type": "webhook_call_error"
        }

async def tool_parse_api_response(state: AgentState, response_data: Any, expected_format: str = "auto") -> Dict[str, Any]:
    """Parse and analyze API response data.

    Args:
        response_data: The API response data to parse
        expected_format: Expected format ("json", "xml", "text", "auto")

    Returns:
        Dict containing parsed and analyzed response
    """
    try:
        parsed_data = response_data
        format_detected = "unknown"
        analysis = {}

        # Auto-detect format
        if expected_format == "auto":
            if isinstance(response_data, str):
                try:
                    parsed_data = json.loads(response_data)
                    format_detected = "json"
                except json.JSONDecodeError:
                    # Check if it looks like XML
                    if response_data.strip().startswith('<') and ('<' in response_data):
                        format_detected = "xml"
                        analysis["xml_detected"] = True
                    else:
                        format_detected = "text"
            elif isinstance(response_data, dict):
                format_detected = "json"
            elif isinstance(response_data, list):
                format_detected = "json_array"
            else:
                format_detected = "other"
        else:
            format_detected = expected_format

        # Analyze structure
        if isinstance(parsed_data, dict):
            analysis["keys_count"] = len(parsed_data)
            analysis["top_level_keys"] = list(parsed_data.keys())[:10]  # First 10 keys
            analysis["has_nested_objects"] = any(isinstance(v, (dict, list)) for v in parsed_data.values())

        elif isinstance(parsed_data, list):
            analysis["items_count"] = len(parsed_data)
            if parsed_data and isinstance(parsed_data[0], dict):
                analysis["item_keys"] = list(parsed_data[0].keys())
                analysis["consistent_structure"] = all(isinstance(item, dict) and set(item.keys()) == set(parsed_data[0].keys()) for item in parsed_data)

        return {
            "ok": True,
            "parsed_data": parsed_data,
            "detected_format": format_detected,
            "analysis": analysis,
            "original_type": type(response_data).__name__
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Response parsing failed: {str(e)}",
            "error_type": "parsing_error",
            "original_data": str(response_data)[:500]  # Truncate for safety
        }

async def tool_api_health_check(state: AgentState, url: str, expected_status: int = 200,
                              timeout: int = 10) -> Dict[str, Any]:
    """Perform a health check on an API endpoint.

    Args:
        url: The API endpoint to check
        expected_status: Expected HTTP status code
        timeout: Request timeout in seconds

    Returns:
        Dict containing health check results
    """
    try:
        # Make a simple GET request
        result = await tool_http_request(state, "GET", url, timeout=timeout)

        if not result["ok"]:
            return {
                "ok": False,
                "healthy": False,
                "error": result["error"],
                "error_type": "connection_failed"
            }

        status_code = result["status_code"]
        healthy = status_code == expected_status

        health_info = {
            "ok": True,
            "healthy": healthy,
            "status_code": status_code,
            "expected_status": expected_status,
            "response_time_ms": result.get("response_time_ms", 0),
            "url": url
        }

        if not healthy:
            health_info["issues"] = [f"Unexpected status code: {status_code} (expected {expected_status})"]

        # Additional checks
        if result.get("response_time_ms", 0) > 5000:  # Over 5 seconds
            health_info["issues"] = health_info.get("issues", [])
            health_info["issues"].append(".2f")

        return health_info

    except Exception as e:
        return {
            "ok": False,
            "healthy": False,
            "error": f"Health check failed: {str(e)}",
            "error_type": "health_check_error"
        }