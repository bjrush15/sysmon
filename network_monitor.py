import psutil
from influx_db import SpeedTestData, TestResult, NetworkIOInterfaceStats, NetworkIOData
import speedtest
from typing import Dict, Tuple, Optional, List
from monitored_stat import MonitoredStat
import logging
from settings import Settings

BITS_PER_S_TO_M_BITS_PER_S = 1024 * 1024


class NetworkSpeedMonitor(MonitoredStat):
    def _measure(self) -> Tuple[bool, Optional[TestResult]]:
        try:
            speed_test_results = self._speed_test_data_from_dict(self._run_speed_test())
        except speedtest.SpeedtestBestServerFailure:
            logging.critical("Failed to fetch the best speedtest server! Check your internet connection")
            return False, None
        logging.info(f"Download: {speed_test_results.download_mbps} Mbps,")
        logging.info(f"Upload: {speed_test_results.upload_mbps} Mbps,")
        logging.info(f"Ping: {speed_test_results.ping_ms} ms")
        logging.debug(speed_test_results)
        return True, speed_test_results

    def _run_speed_test(self) -> Dict:
        test = speedtest.Speedtest()
        test.get_servers()
        logging.info("Finding the best server... ")
        test.get_best_server()
        logging.info("Downloading...")
        test.download()
        logging.info("Uploading... ")
        test.upload()
        return test.results.dict()

    def _speed_test_data_from_dict(self, results: Dict) -> SpeedTestData:
        return SpeedTestData(
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


class NetworkIOMonitor(MonitoredStat):
    def _measure(self) -> Tuple[bool, Optional[TestResult]]:
        netstats = psutil.net_io_counters(pernic=True)
        interface_data: List[NetworkIOInterfaceStats] = []
        for iface in Settings.network_io_monitor.interfaces:
            if iface in netstats.keys():
                interface_data.append(
                    NetworkIOInterfaceStats(
                        interface=iface,
                        bytes_sent=netstats[iface].bytes_sent,
                        bytes_recv=netstats[iface].bytes_recv,
                        packets_sent=netstats[iface].packets_sent,
                        packets_recv=netstats[iface].packets_recv,
                        errin=netstats[iface].errin,
                        errout=netstats[iface].errout,
                        dropin=netstats[iface].dropin,
                        dropout=netstats[iface].dropout,
                    )
                )
            else:
                logging.warning(f"Could not find interface {iface}")
        results = NetworkIOData(
            interface_data=interface_data
        )
        return True, results
