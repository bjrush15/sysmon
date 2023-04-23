from dataclasses import dataclass
from typing import Iterable, Optional
from influxdb_client import InfluxDBClient, WriteApi
from influxdb_client.client.write_api import SYNCHRONOUS, Point
from settings import Settings
import requests


@dataclass(frozen=True)
class TestResult:
    name: str

    def to_points(self) -> Iterable[Point]:
        raise NotImplementedError("All test data must implement to_point()")


@dataclass(frozen=True)
class CPUTestData(TestResult):
    cpu_utilization_percents: Iterable[float]
    cpu_freq_mhz: Iterable[float]
    cpu_load_avg_1m_percent: float
    cpu_load_avg_5m_percent: float
    cpu_load_avg_15m_percent: float

    def to_points(self) -> Iterable[Point]:
        points = []
        for core, (utilization_percent, freq_mhz) in enumerate(zip(self.cpu_utilization_percents, self.cpu_freq_mhz)):
            p = Point(Settings.cpu_monitor.measurement)
            p.tag('core', int(core))
            p.field('utilization-percent', utilization_percent)
            p.field('freq-mhz', freq_mhz)
            points.append(p)
        return points


@dataclass(frozen=True)
class SpeedTestData(TestResult):
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

    def to_points(self) -> Iterable[Point]:
        p = Point(Settings.network_speed_test.measurement). \
            tag("server_city", self.server_city). \
            tag("server_country", self.server_country). \
            tag("server_vendor", self.server_vendor). \
            tag("server_lat", self.server_lat). \
            tag("server_long", self.server_long). \
            tag("client_lat", self.client_lat). \
            tag("client_long", self.client_long). \
            field("download-mbps", self.download_mbps). \
            field('upload-mbps', self.upload_mbps). \
            field('ping-ms', self.ping_ms)
        return [p]


class InfluxDBConnection:
    def __init__(self):
        self.url: Settings.influxdb.server = Settings.influxdb.server
        self.token: Settings.influxdb.token = Settings.influxdb.token
        self.org: Settings.influxdb.org = Settings.influxdb.org
        self.bucket: Settings.influxdb.bucket = Settings.influxdb.bucket
        self.conn: Optional[InfluxDBClient] = None
        self.writer: Optional[WriteApi] = None

    def connect(self):
        self.conn = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.writer = self.conn.write_api(write_options=SYNCHRONOUS)

    def close(self):
        self.writer.close()
        self.conn.close()

    def has_good_connection(self) -> bool:
        return requests.get(f'http://{self.url}/ping').status_code == 204

    def _write(self, record: Iterable[Point]):
        self.writer.write(bucket=self.bucket, org=self.org, record=record)

    def record_measurement(self, data: TestResult):
        self._write(record=data.to_points())
