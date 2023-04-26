import yaml
from dataclasses import dataclass
import logging


@dataclass(frozen=True)
class InfluxSettings:
    token: str
    server: str
    bucket: str
    org: str


@dataclass(frozen=True)
class SpeedtestSettings:
    measurement: str
    monitor_rate: str


@dataclass(frozen=True)
class CPUTestSettings:
    measurement: str
    monitor_rate: str


@dataclass(frozen=True)
class MemoryTestSettings:
    ram_measurement: str
    swap_measurement: str
    monitor_rate: str


# todo: rename this
class SettingsObj:
    influxdb: InfluxSettings
    network_speed_test: SpeedtestSettings
    cpu_monitor: CPUTestSettings
    memory_monitor: MemoryTestSettings

    def load_settings(self):
        logging.debug("Loading settings from yaml file")
        with open('settings.yaml', 'r') as f:
            settings = yaml.safe_load(f)
        self.influxdb = InfluxSettings(
            token=settings['influxdb']['token'],
            server=settings['influxdb']['server'],
            bucket=settings['influxdb']['bucket'],
            org=settings['influxdb']['org'],

        )
        self.network_speed_test = SpeedtestSettings(
            measurement=settings['network_speedtest']['measurement'],
            monitor_rate=settings['network_speedtest']['monitor_rate'],
        )
        self.cpu_monitor = CPUTestSettings(
            measurement=settings['cpu_monitor']['measurement'],
            monitor_rate=settings['cpu_monitor']['monitor_rate'],
        )
        self.memory_monitor = MemoryTestSettings(
            ram_measurement=settings['memory_monitor']['ram_measurement'],
            swap_measurement=settings['memory_monitor']['swap_measurement'],
            monitor_rate=settings['memory_monitor']['monitor_rate'],
        )


Settings = SettingsObj()
