---
timestamp: 1767458434.6370492
datetime: '2026-01-03T11:40:34.637049'
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
  anomaly_id: avg_response_time_1min_1767458434.6370492
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 3760.152220726013
    baseline_value: 511.26768445008554
    deviation: 18.41166144137381
    severity: critical
    percentage_change: 635.4566570680867
  system_state:
    active_requests: 0
    completed_requests_1min: 10
    error_rate_1min: 0.0
    avg_response_time_1min: 3760.152220726013
  metadata: {}
  efficiency:
    requests_per_second: 0.16666666666666666
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 3760.15
- **Baseline Value**: 511.27
- **Deviation**: 18.41 standard deviations
- **Change**: +635.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 10
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 3760.15ms

### Efficiency Metrics

- **Requests/sec**: 0.17
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
    "current_value": 3760.152220726013,
    "baseline_value": 511.26768445008554,
    "deviation": 18.41166144137381,
    "severity": "critical",
    "percentage_change": 635.4566570680867
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 10,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 3760.152220726013
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.16666666666666666,
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
