---
timestamp: 1766868604.3532631
datetime: '2025-12-27T15:50:04.353263'
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
  anomaly_id: avg_response_time_1min_1766868604.3532631
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 8399.514841422057
    baseline_value: 119.2388253812242
    deviation: 210.90563632724667
    severity: critical
    percentage_change: 6944.278417342306
  system_state:
    active_requests: 0
    completed_requests_1min: 195
    error_rate_1min: 0.3128205128205128
    avg_response_time_1min: 8399.514841422057
  metadata: {}
  efficiency:
    requests_per_second: 3.25
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 8399.51
- **Baseline Value**: 119.24
- **Deviation**: 210.91 standard deviations
- **Change**: +6944.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 195
- **Error Rate (1min)**: 31.28%
- **Avg Response Time (1min)**: 8399.51ms

### Efficiency Metrics

- **Requests/sec**: 3.25
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
    "current_value": 8399.514841422057,
    "baseline_value": 119.2388253812242,
    "deviation": 210.90563632724667,
    "severity": "critical",
    "percentage_change": 6944.278417342306
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 195,
    "error_rate_1min": 0.3128205128205128,
    "avg_response_time_1min": 8399.514841422057
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.25,
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
