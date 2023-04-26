Python system monitor backed by InfluxDB.

### Setup

Example `settings.yaml` file:
```
# settings.yaml
---
influxdb:
    server: <influxdb url>
    token: <influxdb token>
    bucket: network-speedtest
    org: system-monitor
    
network_speedtest:
    measurement: net-updown # measurement name in bucket
    refresh_rate: 1h (s, m, h, d are accepted units)
    
cpu_monitor:
    measurement: cpu-stats
    refresh_rate 5s

memory_monitor:
    ram_measurement: ram-stats
    swap_measurement: swawp-stats
    monitor_rate: 5s
```
