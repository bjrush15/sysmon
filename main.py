import time
import logging
import urllib3.exceptions
from monitored_stat import MonitoredStat
from typing import Iterable
from network_speed_monitor import NetworkSpeedMonitor
from cpu_monitor import CPUMonitor
from settings import Settings
from influx_db import InfluxDBConnection


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
        NetworkSpeedMonitor('network-speedtest', conn, Settings.network_speed_test.monitor_rate),
        CPUMonitor('cpu-stat', conn, Settings.cpu_monitor.monitor_rate),
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
