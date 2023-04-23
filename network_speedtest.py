import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import speedtest
from typing import Dict
from dataclasses import dataclass
from settings import Settings

@dataclass
class SpeedTestData:
    download_mbps: float
    upload_mbps: float
    ping_ms: float
    server_lat: float
    server_long: float
    server_city: str
    server_country: str
    server_vendor: str
    client_lat: float
    client_long: float


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


def write_data_to_influx(data: SpeedTestData):
    token = Settings.speedtest.influxdb_token
    org = Settings.speedtest.influxdb_org
    bucket = Settings.speedtest.influxdb_bucket
    url = Settings.speedtest.influxdb_server

    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    client_write = client.write_api(write_options=SYNCHRONOUS)
    p = influxdb_client.Point("net-updown").\
        tag("server_city", data.server_city).\
        tag("server_country", data.server_country).\
        tag("server_vendor", data.server_vendor).\
        tag("server_lat", data.server_lat).\
        tag("server_long", data.server_long).\
        tag("client_lat", data.client_lat).\
        tag("client_long", data.client_long).\
        field("download-mbps", data.download_mbps).\
        field('upload-mbps', data.upload_mbps).\
        field('ping-ms', data.ping_ms)
    client_write.write(bucket=bucket, org=org, record=p)


def run_speedtest_and_push_results():
    speedtest_results = run_speedtest()
    download_mbps = speedtest_results['download']/(1024*1024) # bps to Mbps
    upload_mbps = speedtest_results['upload']/(1024*1024)
    ping_ms = speedtest_results['ping']
    print(f"Download: {download_mbps:.2f} Mbps,")
    print(f"Upload: {upload_mbps:.2f} Mbps,")
    print(f"Ping: {ping_ms:.2f} ms")
    print(speedtest_results)
    write_data_to_influx(speedtestdata_from_dict(speedtest_results))