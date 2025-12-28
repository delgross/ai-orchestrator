---
timestamp: 1766921288.009173
datetime: '2025-12-28T06:28:08.009173'
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
  anomaly_id: avg_response_time_1min_1766921288.009173
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 702.1270291558627
    baseline_value: 31.54548130605774
    deviation: 11.886777088710554
    severity: critical
    percentage_change: 2125.761028477419
  system_state:
    active_requests: 1
    completed_requests_1min: 58
    error_rate_1min: 0.0
    avg_response_time_1min: 702.1270291558627
  metadata: {}
  efficiency:
    requests_per_second: 0.9666666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 702.13
- **Baseline Value**: 31.55
- **Deviation**: 11.89 standard deviations
- **Change**: +2125.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 58
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 702.13ms

### Efficiency Metrics

- **Requests/sec**: 0.97
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
    "current_value": 702.1270291558627,
    "baseline_value": 31.54548130605774,
    "deviation": 11.886777088710554,
    "severity": "critical",
    "percentage_change": 2125.761028477419
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 58,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 702.1270291558627
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.9666666666666667,
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
