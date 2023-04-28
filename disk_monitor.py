import logging
from os.path import basename, dirname, exists, ismount
from typing import Optional, Tuple

import psutil

from influx_db import DiskIOStats, DiskTestData, TestResult
from monitored_stat import MonitoredStat
from settings import Settings


def get_mount_point_from_directory(d: str):
    mount_point = d
    while not ismount(mount_point):
        mount_point = dirname(mount_point)
    return mount_point


class DiskMonitor(MonitoredStat):
    def _measure(self) -> Tuple[bool, Optional[TestResult]]:
        disk_stats = []
        parts = psutil.disk_partitions(all=True)
        disk_io = psutil.disk_io_counters(perdisk=True, nowrap=True)
        for d in Settings.disk_monitor.directories:
            mount_point = get_mount_point_from_directory(d)
            for device in parts:
                if device.mountpoint == mount_point:
                    disk_util = disk_io[basename(device.device)]
                    disk_usage = psutil.disk_usage(d)
                    disk_stats.append(
                        DiskIOStats(
                            device=device.device,
                            directory=d,
                            total_bytes=disk_usage.total,
                            used_bytes=disk_usage.used,
                            free_bytes=disk_usage.free,
                            percent_used=disk_usage.percent,
                            read_count=disk_util.read_count,
                            write_count=disk_util.write_count,
                            read_bytes=disk_util.read_bytes,
                            write_bytes=disk_util.write_bytes,
                            read_time_ms=disk_util.read_time,
                            write_time_ms=disk_util.write_time,
                            busy_time_ms=disk_util.busy_time,
                            read_merged_count=disk_util.read_merged_count,
                            write_merged_count=disk_util.write_merged_count,
                        )
                    )
                    break
        result = DiskTestData(
            disk_stats=disk_stats,
        )
        return True, result

