---
timestamp: 1767371924.869709
datetime: '2026-01-02T11:38:44.869709'
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
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767371924.869709
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 821.8127034151539
    baseline_value: 529.7369693454943
    deviation: 9.726590958262186
    severity: critical
    percentage_change: 55.135992194489994
  system_state:
    active_requests: 9
    completed_requests_1min: 773
    error_rate_1min: 0.0
    avg_response_time_1min: 821.8127034151539
  metadata: {}
  efficiency:
    requests_per_second: 12.883333333333333
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 821.81
- **Baseline Value**: 529.74
- **Deviation**: 9.73 standard deviations
- **Change**: +55.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 773
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 821.81ms

### Efficiency Metrics

- **Requests/sec**: 12.88
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 821.8127034151539,
    "baseline_value": 529.7369693454943,
    "deviation": 9.726590958262186,
    "severity": "critical",
    "percentage_change": 55.135992194489994
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 773,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 821.8127034151539
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.883333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 9
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
