from monitored_stat import MonitoredStat
from influx_db import CPUTestData, TestResult
import psutil
import logging


class CPUMonitor(MonitoredStat):
    def _measure(self) -> TestResult:
        cpu_load_avg_1m_percent, cpu_load_avg_5m_percent, cpu_load_avg_15m_percent = [x/psutil.cpu_count() * 100 for x in psutil.getloadavg()]
        cpu_freq_mhz = [current for current, _, _ in psutil.cpu_freq(True)]
        cpu_utilization_percents = psutil.cpu_percent(0.5, True)
        cpu_test_data = CPUTestData(
            name='cpu-test',
            cpu_utilization_percents=cpu_utilization_percents,
            cpu_freq_mhz=cpu_freq_mhz,
            cpu_load_avg_1m_percent=cpu_load_avg_1m_percent,
            cpu_load_avg_5m_percent=cpu_load_avg_5m_percent,
            cpu_load_avg_15m_percent=cpu_load_avg_15m_percent,
        )
        logging.debug(cpu_test_data)
        return cpu_test_data
