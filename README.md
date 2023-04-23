Python system monitor backed by InfluxDB.

### Setup

Example `settings.yaml` file:
```
# settings.yaml
---
influxdb:
    influxdb_server: <influxdb url>
    influxdb_token: <influxdb token>
    
network_speedtest:
    influxdb_bucket: network-speedtest
    influxdb_org: system-monitor
```
