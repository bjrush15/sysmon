import logging
import time
from typing import Iterable

import urllib3.exceptions

from cpu_monitor import CPUMonitor
from disk_monitor import DiskMonitor
from influx_db import InfluxDBConnection
from memory_monitor import MemoryUsageMonitor
from monitored_stat import MonitoredStat
from network_monitor import NetworkIOMonitor, NetworkSpeedMonitor
from settings import Settings


def start_monitoring(influx_conn: InfluxDBConnection, monitors: Iterable[MonitoredStat]):
    while True:
        time_to_next_measurement_s = []
        for monitor in monitors:
            if monitor.is_ready_for_measurement():
                logging.info(f'Taking {monitor.name} measurement')
                success, m = monitor.take_measurement()
                if not success:
                    logging.critical(f"{monitor.name} measurement failed!")
                else:
                    try:
                        influx_conn.record_measurement(m)
                    except urllib3.exceptions.ReadTimeoutError:
                        logging.critical(f'Connection timed out! Could not write data for {monitor.name} measurement!')
            time_to_next_measurement_s.append(monitor.get_time_to_next_measurement_s())
        sleep_time = max(min(time_to_next_measurement_s), 0)
        logging.debug(f"Sleeping for {sleep_time} seconds")
        time.sleep(sleep_time)


def main():
    logging.getLogger().setLevel(logging.INFO)
    Settings.load_settings()

    conn = InfluxDBConnection()
    conn.wait_for_good_connection()
    conn.connect()

    monitors = [
        DiskMonitor('disk-monitor', Settings.disk_monitor.monitor_rate),
        NetworkIOMonitor('network-io', Settings.network_io_monitor.monitor_rate),
        NetworkSpeedMonitor('network-speedtest', Settings.network_speed_test.monitor_rate),
        CPUMonitor('cpu-stat', Settings.cpu_monitor.monitor_rate),
        MemoryUsageMonitor('memory-monitor', Settings.memory_monitor.monitor_rate),
    ]

    try:
        start_monitoring(conn, monitors)
    except Exception:
        logging.exception('Critical error - shutting down')
    except KeyboardInterrupt:
        logging.info('Caught KeyboardInterrupt. Exiting')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
