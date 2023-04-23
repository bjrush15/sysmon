import time
import logging

import urllib3.exceptions

from network_speed_monitor import NetworkSpeedMonitor
from cpu_monitor import CPUMonitor
from settings import Settings
from influx_db import InfluxDBConnection


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    Settings.load_settings()

    conn = InfluxDBConnection()
    if not conn.has_good_connection():
        # usually requests throws an exception before this - this is a failsafe
        raise ConnectionError(f"There was a problem reaching influxdb server {conn.url}. Could not reach /ping!")
    conn.connect()

    monitors = [
        NetworkSpeedMonitor(conn, Settings.network_speed_test.monitor_rate),
        CPUMonitor(conn, Settings.cpu_monitor.monitor_rate),
    ]
    try:
        while True:
            time_to_next_measurement_s = []
            for monitor in monitors:
                if monitor.is_ready_for_measurement():
                    m = monitor.take_measurement()
                    try:
                        conn.record_measurement(m)
                    except urllib3.exceptions.ReadTimeoutError:
                        logging.critical(f'Connection timed out! Could not write data for {m.name} measurement!')
                time_to_next_measurement_s.append(monitor.get_time_to_next_measurement_s())
            sleep_time = max(min(time_to_next_measurement_s), 0)
            logging.info(f"Sleeping for {sleep_time} seconds")
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        pass
    finally:
        conn.close()


if __name__ == '__main__':
    main()
