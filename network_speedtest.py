from influx_db import SpeedTestData, InfluxDBConnection
import speedtest
from typing import Dict
from monitored_stat import MonitoredStat
import logging

BITS_PER_S_TO_M_BITS_PER_S = 1024 * 1024


class NetworkSpeedTest(MonitoredStat):
    def _measure(self):
        conn = InfluxDBConnection()
        if not conn.has_good_connection():
            # usually requests throws an exception before this - this is a failsafe
            raise ConnectionError(f"There was a problem reaching influxdb server {conn.url}. Could not reach /ping!")
        speed_test_results = self._speed_test_data_from_dict(self._run_speed_test())
        logging.info(f"Download: {speed_test_results.download_mbps} Mbps,")
        logging.info(f"Upload: {speed_test_results.upload_mbps} Mbps,")
        logging.info(f"Ping: {speed_test_results.ping_ms} ms")
        logging.debug(speed_test_results)
        conn.write_speedtest_data(speed_test_results)

    def _run_speed_test(self) -> Dict:
        logging.debug("Starting net speed test")
        test = speedtest.Speedtest()
        test.get_servers()
        logging.debug("Finding the best server... ")
        test.get_best_server()
        logging.debug("Downloading...")
        test.download()
        logging.debug("Uploading... ")
        test.upload()
        logging.debug("Finished net speed test")
        return test.results.dict()

    def _speed_test_data_from_dict(self, results: Dict) -> SpeedTestData:
        return SpeedTestData(
            download_mbps=round(results['download'] / BITS_PER_S_TO_M_BITS_PER_S, 3),  # bps to Mbps
            upload_mbps=round(results['upload'] / BITS_PER_S_TO_M_BITS_PER_S, 3),
            ping_ms=round(results['ping'], 3),
            server_lat=results['server']['lat'],
            server_long=results['server']['lon'],
            server_city=results['server']['name'],
            server_country=results['server']['country'],
            server_vendor=results['server']['sponsor'],
            client_lat=results['client']['lat'],
            client_long=results['client']['lon'],
        )


