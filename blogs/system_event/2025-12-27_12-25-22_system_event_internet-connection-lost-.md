---
timestamp: 1766856322.7782881
datetime: '2025-12-27T12:25:22.778288'
category: system_event
severity: warning
title: 'Internet connection lost: '
source: internet_check
tags: []
resolution_status: open
suggested_actions: []
metadata:
  error_type: PoolTimeout
  error_message: ''
  error_traceback: "Traceback (most recent call last):\n  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_transports/default.py\"\
    , line 101, in map_httpcore_exceptions\n    yield\n  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_transports/default.py\"\
    , line 394, in handle_async_request\n    resp = await self._pool.handle_async_request(req)\n\
    \           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpcore/_async/connection_pool.py\"\
    , line 256, in handle_async_request\n    raise exc from None\n  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpcore/_async/connection_pool.py\"\
    , line 232, in handle_async_request\n    connection = await pool_request.wait_for_connection(timeout=timeout)\n\
    \                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File\
    \ \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpcore/_async/connection_pool.py\"\
    , line 35, in wait_for_connection\n    await self._connection_acquired.wait(timeout=timeout)\n\
    \  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpcore/_synchronization.py\"\
    , line 149, in wait\n    with map_exceptions(anyio_exc_map):\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\
    \  File \"/Users/bee/.local/share/uv/python/cpython-3.12.9-macos-aarch64-none/lib/python3.12/contextlib.py\"\
    , line 158, in __exit__\n    self.gen.throw(value)\n  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpcore/_exceptions.py\"\
    , line 14, in map_exceptions\n    raise to_exc(exc) from exc\nhttpcore.PoolTimeout\n\
    \nThe above exception was the direct cause of the following exception:\n\nTraceback\
    \ (most recent call last):\n  File \"/Users/bee/Sync/Antigravity/ai/agent_runner/tasks.py\"\
    , line 17, in internet_check_task\n    resp = await client.get(\"https://www.google.com\"\
    , timeout=2.0)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\
    \  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_client.py\"\
    , line 1768, in get\n    return await self.request(\n           ^^^^^^^^^^^^^^^^^^^\n\
    \  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_client.py\"\
    , line 1540, in request\n    return await self.send(request, auth=auth, follow_redirects=follow_redirects)\n\
    \           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\
    \  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_client.py\"\
    , line 1629, in send\n    response = await self._send_handling_auth(\n       \
    \        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_client.py\"\
    , line 1657, in _send_handling_auth\n    response = await self._send_handling_redirects(\n\
    \               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_client.py\"\
    , line 1694, in _send_handling_redirects\n    response = await self._send_single_request(request)\n\
    \               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_client.py\"\
    , line 1730, in _send_single_request\n    response = await transport.handle_async_request(request)\n\
    \               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_transports/default.py\"\
    , line 393, in handle_async_request\n    with map_httpcore_exceptions():\n   \
    \      ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/Users/bee/.local/share/uv/python/cpython-3.12.9-macos-aarch64-none/lib/python3.12/contextlib.py\"\
    , line 158, in __exit__\n    self.gen.throw(value)\n  File \"/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_transports/default.py\"\
    , line 118, in map_httpcore_exceptions\n    raise mapped_exc(message) from exc\n\
    httpx.PoolTimeout\n"
structured_data: {}
---

# Internet connection lost: 

Event: internet_lost_exception

Internet connection lost: 

Metadata: {'error_type': 'PoolTimeout', 'error_message': '', 'error_traceback': 'Traceback (most recent call last):\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_transports/default.py", line 101, in map_httpcore_exceptions\n    yield\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_transports/default.py", line 394, in handle_async_request\n    resp = await self._pool.handle_async_request(req)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpcore/_async/connection_pool.py", line 256, in handle_async_request\n    raise exc from None\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpcore/_async/connection_pool.py", line 232, in handle_async_request\n    connection = await pool_request.wait_for_connection(timeout=timeout)\n                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpcore/_async/connection_pool.py", line 35, in wait_for_connection\n    await self._connection_acquired.wait(timeout=timeout)\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpcore/_synchronization.py", line 149, in wait\n    with map_exceptions(anyio_exc_map):\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/Users/bee/.local/share/uv/python/cpython-3.12.9-macos-aarch64-none/lib/python3.12/contextlib.py", line 158, in __exit__\n    self.gen.throw(value)\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpcore/_exceptions.py", line 14, in map_exceptions\n    raise to_exc(exc) from exc\nhttpcore.PoolTimeout\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File "/Users/bee/Sync/Antigravity/ai/agent_runner/tasks.py", line 17, in internet_check_task\n    resp = await client.get("https://www.google.com", timeout=2.0)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_client.py", line 1768, in get\n    return await self.request(\n           ^^^^^^^^^^^^^^^^^^^\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_client.py", line 1540, in request\n    return await self.send(request, auth=auth, follow_redirects=follow_redirects)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_client.py", line 1629, in send\n    response = await self._send_handling_auth(\n               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_client.py", line 1657, in _send_handling_auth\n    response = await self._send_handling_redirects(\n               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_client.py", line 1694, in _send_handling_redirects\n    response = await self._send_single_request(request)\n               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_client.py", line 1730, in _send_single_request\n    response = await transport.handle_async_request(request)\n               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_transports/default.py", line 393, in handle_async_request\n    with map_httpcore_exceptions():\n         ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/Users/bee/.local/share/uv/python/cpython-3.12.9-macos-aarch64-none/lib/python3.12/contextlib.py", line 158, in __exit__\n    self.gen.throw(value)\n  File "/Users/bee/Sync/Antigravity/ai/.venv/lib/python3.12/site-packages/httpx/_transports/default.py", line 118, in map_httpcore_exceptions\n    raise mapped_exc(message) from exc\nhttpx.PoolTimeout\n'}
