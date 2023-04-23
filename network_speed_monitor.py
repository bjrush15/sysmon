from influx_db import SpeedTestData
from influx_db import TestResult
import speedtest
from typing import Dict
from monitored_stat import MonitoredStat
import logging

BITS_PER_S_TO_M_BITS_PER_S = 1024 * 1024


class NetworkSpeedMonitor(MonitoredStat):
    def _measure(self) -> TestResult:
        speed_test_results = self._speed_test_data_from_dict(self._run_speed_test())
        logging.info(f"Download: {speed_test_results.download_mbps} Mbps,")
        logging.info(f"Upload: {speed_test_results.upload_mbps} Mbps,")
        logging.info(f"Ping: {speed_test_results.ping_ms} ms")
        logging.debug(speed_test_results)
        return speed_test_results

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
            name="network-speedtest",
            download_mbps=round(results['download'] / BITS_PER_S_TO_M_BITS_PER_S, 3),
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


