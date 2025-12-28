---
timestamp: 1766883954.145068
datetime: '2025-12-27T20:05:54.145068'
category: system_event
severity: warning
title: 'Local tool failed: list_dir'
source: engine
tags: []
resolution_status: open
suggested_actions: []
metadata:
  tool_name: list_dir
  error_type: NameError
  error_message: name 'asyncio' is not defined
  error_traceback: "Traceback (most recent call last):\n  File \"/Users/bee/Sync/Antigravity/ai/agent_runner/engine.py\"\
    , line 266, in execute_tool_call\n    if asyncio.iscoroutinefunction(impl):\n\
    \       ^^^^^^^\nNameError: name 'asyncio' is not defined. Did you forget to import\
    \ 'asyncio'\n"
structured_data: {}
---

# Local tool failed: list_dir

Event: tool_error

Local tool failed: list_dir

Metadata: {'tool_name': 'list_dir', 'error_type': 'NameError', 'error_message': "name 'asyncio' is not defined", 'error_traceback': 'Traceback (most recent call last):\n  File "/Users/bee/Sync/Antigravity/ai/agent_runner/engine.py", line 266, in execute_tool_call\n    if asyncio.iscoroutinefunction(impl):\n       ^^^^^^^\nNameError: name \'asyncio\' is not defined. Did you forget to import \'asyncio\'\n'}
