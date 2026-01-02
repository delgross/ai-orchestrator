---
timestamp: 1767291762.9640472
datetime: '2026-01-01T13:22:42.964047'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions:
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
metadata:
  anomaly_id: avg_response_time_1min_1767291762.9640472
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 4905.4139494895935
    baseline_value: 2010.170721745753
    deviation: 1.8914191298150105
    severity: warning
    percentage_change: 144.02971829325207
  system_state:
    active_requests: 1
    completed_requests_1min: 80
    error_rate_1min: 0.0
    avg_response_time_1min: 4905.4139494895935
  metadata: {}
  efficiency:
    requests_per_second: 1.3333333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 4905.41
- **Baseline Value**: 2010.17
- **Deviation**: 1.89 standard deviations
- **Change**: +144.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 80
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 4905.41ms

### Efficiency Metrics

- **Requests/sec**: 1.33
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 4905.4139494895935,
    "baseline_value": 2010.170721745753,
    "deviation": 1.8914191298150105,
    "severity": "warning",
    "percentage_change": 144.02971829325207
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 80,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 4905.4139494895935
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.3333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
