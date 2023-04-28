from datetime import datetime, timedelta
from typing import Optional, Tuple

from influx_db import TestResult

UNIT_TO_S = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}


def parse_refresh_rate(rate: str) -> float:
    rate = rate.lower().strip()
    unit = rate[-1]
    if unit not in UNIT_TO_S.keys():
        raise KeyError(f"Invalid refresh rate unit on stat. Found {unit}, expected one of {UNIT_TO_S.keys()}")
    refresh_rate = float(rate[:-1]) * UNIT_TO_S[unit]
    return refresh_rate


class MonitoredStat:
    def __init__(self, name: str, refresh_rate: str):
        self.name = name
        self.refresh_rate_s = parse_refresh_rate(refresh_rate)
        self.last_measurement_timestamp = datetime.fromtimestamp(0)

    def take_measurement(self) -> Tuple[bool, Optional[TestResult]]:
        self.last_measurement_timestamp = datetime.now()
        return self._measure()

    def _measure(self) -> Tuple[bool, Optional[TestResult]]:
        raise NotImplementedError("All stats must implement _measure()")

    def is_ready_for_measurement(self) -> bool:
        now = datetime.now()
        return (now - self.last_measurement_timestamp).total_seconds() > self.refresh_rate_s

    def get_time_to_next_measurement_s(self) -> float:
        return (self.last_measurement_timestamp + timedelta(0, self.refresh_rate_s) - datetime.now()).total_seconds()

