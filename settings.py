import yaml
from dataclasses import dataclass
import logging


@dataclass(frozen=True)
class InfluxSettings:
    token: str
    server: str


@dataclass(frozen=True)
class SpeedtestSettings:
    influxdb_bucket: str
    influxdb_org: str
    monitor_rate: str


# todo: rename this
class SettingsObj:
    influxdb: InfluxSettings
    network_speed_test: SpeedtestSettings

    def load_settings(self):
        logging.debug("Loading settings from yaml file")
        with open('settings.yaml', 'r') as f:
            settings = yaml.safe_load(f)
        self.influxdb = InfluxSettings(
            token=settings['influxdb']['token'],
            server=settings['influxdb']['server'],

        )
        self.network_speed_test = SpeedtestSettings(
            influxdb_org=settings['network_speedtest']['influxdb_org'],
            influxdb_bucket=settings['network_speedtest']['influxdb_bucket'],
            monitor_rate=settings['network_speedtest']['monitor_rate'],
        )


Settings = SettingsObj()
