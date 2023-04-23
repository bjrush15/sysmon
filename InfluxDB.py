from dataclasses import dataclass
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from settings import Settings
import requests

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


class InfluxDBConnection:
    def __init__(self):
        self.url = Settings.influxdb.server
        self.token = Settings.influxdb.token

    def has_good_connection(self) -> bool:
        return requests.get(f'http://{self.url}/ping').status_code == 204

    def write_speedtest_data(self, data: SpeedTestData):
        org = Settings.speedtest.influxdb_org
        bucket = Settings.speedtest.influxdb_bucket
        client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=org)
        client_write = client.write_api(write_options=SYNCHRONOUS)
        p = influxdb_client.Point("net-updown"). \
            tag("server_city", data.server_city). \
            tag("server_country", data.server_country). \
            tag("server_vendor", data.server_vendor). \
            tag("server_lat", data.server_lat). \
            tag("server_long", data.server_long). \
            tag("client_lat", data.client_lat). \
            tag("client_long", data.client_long). \
            field("download-mbps", data.download_mbps). \
            field('upload-mbps', data.upload_mbps). \
            field('ping-ms', data.ping_ms)
        client_write.write(bucket=bucket, org=org, record=p)
