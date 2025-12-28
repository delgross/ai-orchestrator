---
timestamp: 1766921948.0472178
datetime: '2025-12-28T06:39:08.047218'
category: anomaly
severity: critical
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- critical
resolution_status: open
suggested_actions:
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1766921948.0472178
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 599.1638260228293
    baseline_value: 35.84503800223195
    deviation: 7.046508633358006
    severity: critical
    percentage_change: 1571.5391011317142
  system_state:
    active_requests: 0
    completed_requests_1min: 56
    error_rate_1min: 0.0
    avg_response_time_1min: 599.1638260228293
  metadata: {}
  efficiency:
    requests_per_second: 0.9333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 599.16
- **Baseline Value**: 35.85
- **Deviation**: 7.05 standard deviations
- **Change**: +1571.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 56
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 599.16ms

### Efficiency Metrics

- **Requests/sec**: 0.93
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 599.1638260228293,
    "baseline_value": 35.84503800223195,
    "deviation": 7.046508633358006,
    "severity": "critical",
    "percentage_change": 1571.5391011317142
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 56,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 599.1638260228293
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.9333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Investigate immediately - critical system issue detected
