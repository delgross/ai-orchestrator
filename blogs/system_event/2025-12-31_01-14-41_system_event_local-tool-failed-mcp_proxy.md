---
timestamp: 1767161681.660718
datetime: '2025-12-31T01:14:41.660718'
category: system_event
severity: warning
title: 'Local tool failed: mcp_proxy'
source: executor
tags: []
resolution_status: open
suggested_actions: []
metadata:
  tool_name: mcp_proxy
  error_type: TypeError
  error_message: 'tool_mcp_proxy() missing 1 required positional argument: ''arguments'''
  error_traceback: "Traceback (most recent call last):\n  File \"/Users/bee/Sync/Antigravity/ai/agent_runner/executor.py\"\
    , line 414, in execute_tool_call\n    result = await impl(self.state, **args)\n\
    \                   ~~~~^^^^^^^^^^^^^^^^^^^^\nTypeError: tool_mcp_proxy() missing\
    \ 1 required positional argument: 'arguments'\n"
structured_data: {}
---

# Local tool failed: mcp_proxy

Event: tool_error

Local tool failed: mcp_proxy

Metadata: {'tool_name': 'mcp_proxy', 'error_type': 'TypeError', 'error_message': "tool_mcp_proxy() missing 1 required positional argument: 'arguments'", 'error_traceback': 'Traceback (most recent call last):\n  File "/Users/bee/Sync/Antigravity/ai/agent_runner/executor.py", line 414, in execute_tool_call\n    result = await impl(self.state, **args)\n                   ~~~~^^^^^^^^^^^^^^^^^^^^\nTypeError: tool_mcp_proxy() missing 1 required positional argument: \'arguments\'\n'}
