import logging
import time
from dataclasses import dataclass
from typing import Iterable, Optional
from influxdb_client import InfluxDBClient, WriteApi
from influxdb_client.client.write_api import SYNCHRONOUS, Point
from settings import Settings
import requests


@dataclass(frozen=True)
class TestResult:
    def to_points(self) -> Iterable[Point]:
        raise NotImplementedError("All test data must implement to_point()")


@dataclass(frozen=True)
class MemoryTestData(TestResult):
    ram_total_bytes: int
    ram_available_bytes: int
    ram_available_percent: float
    ram_used_bytes: int
    ram_free_bytes: int
    ram_active_bytes: int
    ram_inactive_bytes: int
    ram_buffers_bytes: int
    ram_cached_bytes: int
    ram_shared_bytes: int
    ram_slab_bytes: int
    swap_total_bytes: int
    swap_used_bytes: int
    swap_free_bytes: int
    swap_used_percent: float
    swap_in_total_bytes: int
    swap_out_total_bytes: int

    def to_points(self) -> Iterable[Point]:
        # TODO: don't send alllll of these to db. Choose better. Config?
        p = []
        memp = Point(Settings.memory_monitor.ram_measurement)
        memp.field('ram_total_bytes', self.ram_total_bytes)
        memp.field('ram_available_bytes', self.ram_available_bytes)
        memp.field('ram_available_percent', self.ram_available_percent)
        memp.field('ram_used_bytes', self.ram_used_bytes)
        memp.field('ram_free_bytes', self.ram_free_bytes)
        memp.field('ram_active_bytes', self.ram_active_bytes)
        memp.field('ram_inactive_bytes', self.ram_inactive_bytes)
        memp.field('ram_buffers_bytes', self.ram_buffers_bytes)
        memp.field('ram_cached_bytes', self.ram_cached_bytes)
        memp.field('ram_shared_bytes', self.ram_shared_bytes)
        memp.field('ram_slab_bytes', self.ram_slab_bytes)
        p.append(memp)
        if self.swap_total_bytes != 0:
            swapp = Point(Settings.memory_monitor.swap_measurement)
            swapp.field('swap_total_bytes', self.swap_total_bytes)
            swapp.field('swap_used_bytes', self.swap_used_bytes)
            swapp.field('swap_free_bytes', self.swap_free_bytes)
            swapp.field('swap_used_percent', self.swap_used_percent)
            swapp.field('swap_in_total_bytes', self.swap_in_total_bytes)
            swapp.field('swap_out_total_bytes', self.swap_out_total_bytes)
            p.append(swapp)
        return p


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
        p = Point(Settings.network_speed_test.measurement)
        p.tag("server_city", self.server_city)
        p.tag("server_country", self.server_country)
        p.tag("server_vendor", self.server_vendor)
        p.tag("server_lat", self.server_lat)
        p.tag("server_long", self.server_long)
        p.tag("client_lat", self.client_lat)
        p.tag("client_long", self.client_long)
        p.field("download-mbps", self.download_mbps)
        p.field('upload-mbps', self.upload_mbps)
        p.field('ping-ms', self.ping_ms)
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
        try:
            result = requests.get(f'http://{self.url}/ping')
        except requests.exceptions.ConnectionError as e:
            reason = ''.join(e.args[0].reason.args[-1].split(':')[1:]).strip()
            logging.debug(f'Could not establish a connection to InfluxDB at {self.url}', exc_info=True)
            logging.error(f'Failed to connect to InfluxDB at {self.url}: {reason}')
            return False
        if result.status_code != 204:
            logging.error(f"Unexpected response from InfluxDB ping - Got response {result.status_code}, expected 204")
            return False
        return True

    def wait_for_good_connection(self):
        while not self.has_good_connection():
            time.sleep(3)

    def _write(self, record: Iterable[Point]):
        self.writer.write(bucket=self.bucket, org=self.org, record=record)

    def record_measurement(self, data: TestResult):
        self._write(record=data.to_points())
