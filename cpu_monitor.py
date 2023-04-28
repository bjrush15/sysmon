import logging
from typing import Optional, Tuple

import psutil

from influx_db import CPUCoreData, CPUTestData, TestResult
from monitored_stat import MonitoredStat


class CPUMonitor(MonitoredStat):
    def _measure(self) -> Tuple[bool, Optional[TestResult]]:
        load_avg_1m_percent, load_avg_5m_percent, load_avg_15m_percent = [x/psutil.cpu_count() * 100 for x in psutil.getloadavg()]
        freq_mhzs = [current for current, _, _ in psutil.cpu_freq(True)]
        utilization_percents = psutil.cpu_percent(0.5, True)
        stats = psutil.cpu_stats()
        core_data = []
        for utilization_percent, freq_mhz in zip(utilization_percents, freq_mhzs):
            core_data.append(
                CPUCoreData(
                    utilization_percent=utilization_percent,
                    freq_mhz=freq_mhz
                )
            )
        test_data = CPUTestData(
            cpu_core_data=core_data,
            load_avg_1m_percent=load_avg_1m_percent,
            load_avg_5m_percent=load_avg_5m_percent,
            load_avg_15m_percent=load_avg_15m_percent,
            num_interrupts=stats.interrupts,
            num_context_switches=stats.ctx_switches,
            num_software_interrupts=stats.soft_interrupts,
        )
        logging.debug(test_data)
        return True, test_data
