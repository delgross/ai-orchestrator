---
timestamp: 1766983854.428402
datetime: '2025-12-28T23:50:54.428402'
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
  anomaly_id: avg_response_time_1min_1766983854.428402
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 253.8682692641512
    baseline_value: 152.0336408487562
    deviation: 7.188863692655592
    severity: critical
    percentage_change: 66.98164159385
  system_state:
    active_requests: 0
    completed_requests_1min: 109
    error_rate_1min: 0.0
    avg_response_time_1min: 253.8682692641512
  metadata: {}
  efficiency:
    requests_per_second: 1.8166666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 253.87
- **Baseline Value**: 152.03
- **Deviation**: 7.19 standard deviations
- **Change**: +67.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 109
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 253.87ms

### Efficiency Metrics

- **Requests/sec**: 1.82
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
    "current_value": 253.8682692641512,
    "baseline_value": 152.0336408487562,
    "deviation": 7.188863692655592,
    "severity": "critical",
    "percentage_change": 66.98164159385
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 109,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 253.8682692641512
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.8166666666666667,
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
