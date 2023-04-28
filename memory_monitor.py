from typing import Optional, Tuple

import psutil

from influx_db import MemoryTestData, TestResult
from monitored_stat import MonitoredStat


class MemoryUsageMonitor(MonitoredStat):
    def _measure(self) -> Tuple[bool, Optional[TestResult]]:
        vmem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        d = MemoryTestData(
            ram_total_bytes=vmem.total,
            ram_available_bytes=vmem.available,
            ram_available_percent=vmem.percent,
            ram_used_bytes=vmem.used,
            ram_free_bytes=vmem.free,
            ram_active_bytes=vmem.active,
            ram_inactive_bytes=vmem.inactive,
            ram_buffers_bytes=vmem.buffers,
            ram_cached_bytes=vmem.cached,
            ram_shared_bytes=vmem.shared,
            ram_slab_bytes=vmem.slab,
            swap_total_bytes=swap.total,
            swap_used_bytes=swap.used,
            swap_free_bytes=swap.free,
            swap_used_percent=swap.percent,
            swap_in_total_bytes=swap.sin,
            swap_out_total_bytes=swap.sout,
        )
        return True, d
