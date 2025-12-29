---
timestamp: 1767023251.371739
datetime: '2025-12-29T10:47:31.371739'
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
  anomaly_id: avg_response_time_1min_1767023251.371739
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 426.3462837803307
    baseline_value: 165.22155065120893
    deviation: 4.9953746279476166
    severity: warning
    percentage_change: 158.04520179112066
  system_state:
    active_requests: 2
    completed_requests_1min: 209
    error_rate_1min: 0.0
    avg_response_time_1min: 426.3462837803307
  metadata: {}
  efficiency:
    requests_per_second: 3.4833333333333334
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 426.35
- **Baseline Value**: 165.22
- **Deviation**: 5.00 standard deviations
- **Change**: +158.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 209
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 426.35ms

### Efficiency Metrics

- **Requests/sec**: 3.48
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 426.3462837803307,
    "baseline_value": 165.22155065120893,
    "deviation": 4.9953746279476166,
    "severity": "warning",
    "percentage_change": 158.04520179112066
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 209,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 426.3462837803307
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.4833333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
