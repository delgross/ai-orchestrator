---
timestamp: 1767461256.1246898
datetime: '2026-01-03T12:27:36.124690'
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
  anomaly_id: avg_response_time_1min_1767461256.1246898
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2343.250632286072
    baseline_value: 649.6078681945801
    deviation: 5.242027563366043
    severity: critical
    percentage_change: 260.7177109474584
  system_state:
    active_requests: 0
    completed_requests_1min: 2
    error_rate_1min: 0.0
    avg_response_time_1min: 2343.250632286072
  metadata: {}
  efficiency:
    requests_per_second: 0.03333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2343.25
- **Baseline Value**: 649.61
- **Deviation**: 5.24 standard deviations
- **Change**: +260.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 2
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2343.25ms

### Efficiency Metrics

- **Requests/sec**: 0.03
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
    "current_value": 2343.250632286072,
    "baseline_value": 649.6078681945801,
    "deviation": 5.242027563366043,
    "severity": "critical",
    "percentage_change": 260.7177109474584
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 2,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2343.250632286072
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.03333333333333333,
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
