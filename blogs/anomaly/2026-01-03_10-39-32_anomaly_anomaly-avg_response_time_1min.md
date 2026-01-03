---
timestamp: 1767454772.522871
datetime: '2026-01-03T10:39:32.522871'
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
  anomaly_id: avg_response_time_1min_1767454772.522871
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 3932.5347542762756
    baseline_value: 489.48270711467495
    deviation: 24.140903133435046
    severity: critical
    percentage_change: 703.4062689276926
  system_state:
    active_requests: 0
    completed_requests_1min: 12
    error_rate_1min: 0.0
    avg_response_time_1min: 3932.5347542762756
  metadata: {}
  efficiency:
    requests_per_second: 0.2
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 3932.53
- **Baseline Value**: 489.48
- **Deviation**: 24.14 standard deviations
- **Change**: +703.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 12
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 3932.53ms

### Efficiency Metrics

- **Requests/sec**: 0.20
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
    "current_value": 3932.5347542762756,
    "baseline_value": 489.48270711467495,
    "deviation": 24.140903133435046,
    "severity": "critical",
    "percentage_change": 703.4062689276926
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 12,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 3932.5347542762756
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.2,
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
