from InfluxDB import SpeedTestData, InfluxDBConnection
import speedtest
from typing import Dict


def speedtestdata_from_dict(results: Dict) -> SpeedTestData:
    return SpeedTestData(
        download_mbps=round(results['download'] / (1024 * 1024), 3), # bps to Mbps
        upload_mbps=round(results['upload'] / (1024 * 1024), 3),
        ping_ms=round(results['ping'], 3),
        server_lat=results['server']['lat'],
        server_long=results['server']['lon'],
        server_city=results['server']['name'],
        server_country=results['server']['country'],
        server_vendor=results['server']['sponsor'],
        client_lat=results['client']['lat'],
        client_long=results['client']['lon'],
    )


def run_speedtest() -> Dict:
    print("Starting download test")
    test = speedtest.Speedtest()
    test.get_servers()
    print("Finding the best server... ", end='')
    test.get_best_server()
    print("Done")
    print("Downloading...", end='')
    test.download()
    print("Done")
    print("Uploading... ", end='')
    test.upload()
    print("Done")
    return test.results.dict()


def run_speedtest_and_push_results():
    conn = InfluxDBConnection()
    if not conn.has_good_connection():
        # usually requests throws an exception before this - this is a failsafe
        raise ConnectionError(f"There was a problem reaching influxdb server {conn.url}. Could not reach /ping!")
    speedtest_results = run_speedtest()
    download_mbps = speedtest_results['download']/(1024*1024) # bps to Mbps
    upload_mbps = speedtest_results['upload']/(1024*1024)
    ping_ms = speedtest_results['ping']
    print(f"Download: {download_mbps:.2f} Mbps,")
    print(f"Upload: {upload_mbps:.2f} Mbps,")
    print(f"Ping: {ping_ms:.2f} ms")
    print(speedtest_results)
    conn.write_speedtest_data(speedtestdata_from_dict(speedtest_results))