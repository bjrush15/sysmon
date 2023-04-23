import time
import logging
from network_speedtest import NetworkSpeedTest
from settings import Settings


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    Settings.load_settings()
    monitors = [NetworkSpeedTest(Settings.network_speed_test.monitor_rate)]
    while True:
        time_to_next_measurement_s = []
        for monitor in monitors:
            if monitor.is_ready_for_measurement():
                monitor.take_and_record_measurement()
            time_to_next_measurement_s.append(monitor.get_time_to_next_measurement_s())
        sleep_time = max(min(time_to_next_measurement_s), 0)
        logging.info(f"Sleeping for {sleep_time} seconds")
        time.sleep(sleep_time)


if __name__ == '__main__':
    main()
