---
timestamp: 1767310744.405507
datetime: '2026-01-01T18:39:04.405507'
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
  anomaly_id: avg_response_time_1min_1767310744.405507
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 610.2182415296446
    baseline_value: 285.494755526058
    deviation: 3.811787951431692
    severity: critical
    percentage_change: 113.7406133451541
  system_state:
    active_requests: 2
    completed_requests_1min: 106
    error_rate_1min: 0.0
    avg_response_time_1min: 610.2182415296446
  metadata: {}
  efficiency:
    requests_per_second: 1.7666666666666666
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 610.22
- **Baseline Value**: 285.49
- **Deviation**: 3.81 standard deviations
- **Change**: +113.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 106
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 610.22ms

### Efficiency Metrics

- **Requests/sec**: 1.77
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

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
    "current_value": 610.2182415296446,
    "baseline_value": 285.494755526058,
    "deviation": 3.811787951431692,
    "severity": "critical",
    "percentage_change": 113.7406133451541
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 106,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 610.2182415296446
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.7666666666666666,
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
3. Investigate immediately - critical system issue detected
