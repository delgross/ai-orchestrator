---
timestamp: 1767022711.318841
datetime: '2025-12-29T10:38:31.318841'
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
  anomaly_id: avg_response_time_1min_1767022711.318841
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 370.44316582975136
    baseline_value: 153.43600100972648
    deviation: 8.811635118853133
    severity: critical
    percentage_change: 141.43171315203173
  system_state:
    active_requests: 1
    completed_requests_1min: 226
    error_rate_1min: 0.0
    avg_response_time_1min: 370.44316582975136
  metadata: {}
  efficiency:
    requests_per_second: 3.7666666666666666
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 370.44
- **Baseline Value**: 153.44
- **Deviation**: 8.81 standard deviations
- **Change**: +141.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 226
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 370.44ms

### Efficiency Metrics

- **Requests/sec**: 3.77
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
    "current_value": 370.44316582975136,
    "baseline_value": 153.43600100972648,
    "deviation": 8.811635118853133,
    "severity": "critical",
    "percentage_change": 141.43171315203173
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 226,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 370.44316582975136
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.7666666666666666,
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
