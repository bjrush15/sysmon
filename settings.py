import yaml
from dataclasses import dataclass


@dataclass(frozen=True)
class SpeedtestSettings:
    influxdb_token: str
    influxdb_bucket: str
    influxdb_org: str
    influxdb_server: str


# todo: rename this
@dataclass(frozen=True)
class SettingsObj:
    speedtest: SpeedtestSettings


def load_settings() -> SettingsObj:
    print("Loading settings from yaml file")
    with open('settings.yaml', 'r') as f:
        settings = yaml.safe_load(f)
    return SettingsObj(
        SpeedtestSettings(
            influxdb_org=settings['network_speedtest']['influxdb_org'],
            influxdb_token=settings['network_speedtest']['influxdb_token'],
            influxdb_bucket=settings['network_speedtest']['influxdb_bucket'],
            influxdb_server=settings['network_speedtest']['influxdb_server'],
        ),
    )


Settings = load_settings()
