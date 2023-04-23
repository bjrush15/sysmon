import yaml
from dataclasses import dataclass


@dataclass(frozen=True)
class InfluxSettings:
    token: str
    server: str


@dataclass(frozen=True)
class SpeedtestSettings:
    influxdb_bucket: str
    influxdb_org: str


# todo: rename this
@dataclass(frozen=True)
class SettingsObj:
    influxdb: InfluxSettings
    speedtest: SpeedtestSettings


def load_settings() -> SettingsObj:
    print("Loading settings from yaml file")
    with open('settings.yaml', 'r') as f:
        settings = yaml.safe_load(f)
    return SettingsObj(
        InfluxSettings(
            token=settings['influxdb']['token'],
            server=settings['influxdb']['server'],

        ),
        SpeedtestSettings(
            influxdb_org=settings['network_speedtest']['influxdb_org'],
            influxdb_bucket=settings['network_speedtest']['influxdb_bucket'],
        ),
    )


Settings = load_settings()
