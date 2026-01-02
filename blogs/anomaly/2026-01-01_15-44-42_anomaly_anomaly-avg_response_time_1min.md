---
timestamp: 1767300282.6995368
datetime: '2026-01-01T15:44:42.699537'
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
  anomaly_id: avg_response_time_1min_1767300282.6995368
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 6527.397960424423
    baseline_value: 1329.5190998765288
    deviation: 6.20520107749567
    severity: critical
    percentage_change: 390.9593221361481
  system_state:
    active_requests: 3
    completed_requests_1min: 24
    error_rate_1min: 0.0
    avg_response_time_1min: 6527.397960424423
  metadata: {}
  efficiency:
    requests_per_second: 0.4
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 6527.40
- **Baseline Value**: 1329.52
- **Deviation**: 6.21 standard deviations
- **Change**: +391.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 24
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 6527.40ms

### Efficiency Metrics

- **Requests/sec**: 0.40
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

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
    "current_value": 6527.397960424423,
    "baseline_value": 1329.5190998765288,
    "deviation": 6.20520107749567,
    "severity": "critical",
    "percentage_change": 390.9593221361481
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 24,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 6527.397960424423
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.4,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
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
