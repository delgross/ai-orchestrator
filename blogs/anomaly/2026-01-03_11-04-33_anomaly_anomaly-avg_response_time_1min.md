---
timestamp: 1767456273.387501
datetime: '2026-01-03T11:04:33.387501'
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
  anomaly_id: avg_response_time_1min_1767456273.387501
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1008.3723465601603
    baseline_value: 494.0652422880003
    deviation: 3.3814769585529483
    severity: critical
    percentage_change: 104.09700182316412
  system_state:
    active_requests: 1
    completed_requests_1min: 6
    error_rate_1min: 0.0
    avg_response_time_1min: 1008.3723465601603
  metadata: {}
  efficiency:
    requests_per_second: 0.1
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1008.37
- **Baseline Value**: 494.07
- **Deviation**: 3.38 standard deviations
- **Change**: +104.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 6
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1008.37ms

### Efficiency Metrics

- **Requests/sec**: 0.10
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
    "current_value": 1008.3723465601603,
    "baseline_value": 494.0652422880003,
    "deviation": 3.3814769585529483,
    "severity": "critical",
    "percentage_change": 104.09700182316412
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 6,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1008.3723465601603
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.1,
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
