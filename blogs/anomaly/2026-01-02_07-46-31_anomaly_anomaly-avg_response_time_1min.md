---
timestamp: 1767357991.210054
datetime: '2026-01-02T07:46:31.210054'
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
  anomaly_id: avg_response_time_1min_1767357991.210054
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 247.26484607717845
    baseline_value: 673.4584024244118
    deviation: 3.0183884709307383
    severity: critical
    percentage_change: -63.284317904856614
  system_state:
    active_requests: 0
    completed_requests_1min: 179
    error_rate_1min: 0.0
    avg_response_time_1min: 247.26484607717845
  metadata: {}
  efficiency:
    requests_per_second: 2.9833333333333334
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 247.26
- **Baseline Value**: 673.46
- **Deviation**: 3.02 standard deviations
- **Change**: -63.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 179
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 247.26ms

### Efficiency Metrics

- **Requests/sec**: 2.98
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 247.26484607717845,
    "baseline_value": 673.4584024244118,
    "deviation": 3.0183884709307383,
    "severity": "critical",
    "percentage_change": -63.284317904856614
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 179,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 247.26484607717845
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.9833333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
