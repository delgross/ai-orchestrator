---
timestamp: 1767298542.503347
datetime: '2026-01-01T15:15:42.503347'
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
  anomaly_id: avg_response_time_1min_1767298542.503347
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 15295.419248667631
    baseline_value: 1100.940085690597
    deviation: 22.748229198632266
    severity: critical
    percentage_change: 1289.3053261906737
  system_state:
    active_requests: 1
    completed_requests_1min: 22
    error_rate_1min: 0.0
    avg_response_time_1min: 15295.419248667631
  metadata: {}
  efficiency:
    requests_per_second: 0.36666666666666664
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 15295.42
- **Baseline Value**: 1100.94
- **Deviation**: 22.75 standard deviations
- **Change**: +1289.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 22
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 15295.42ms

### Efficiency Metrics

- **Requests/sec**: 0.37
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

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
    "current_value": 15295.419248667631,
    "baseline_value": 1100.940085690597,
    "deviation": 22.748229198632266,
    "severity": "critical",
    "percentage_change": 1289.3053261906737
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 22,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 15295.419248667631
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.36666666666666664,
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
3. Investigate immediately - critical system issue detected
