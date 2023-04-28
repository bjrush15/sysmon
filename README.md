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
    
network:
    speedtest:
        measurement: net-speed # measurement name in bucket
        refresh_rate: 1h (s, m, h, d are accepted units)
    io:
        interfaces:
          - eth0
          - wlan0
        measurement: net-updown
        monitor_rate: 30s
    
cpu_monitor:
    measurement: cpu-stats
    refresh_rate 5s

memory_monitor:
    ram_measurement: ram-stats
    swap_measurement: swawp-stats
    monitor_rate: 5s
    
disk_monitor:
    directories:
      - /
      - /mnt
    measurement: disk-stats
    monitor_rate 5s
```
