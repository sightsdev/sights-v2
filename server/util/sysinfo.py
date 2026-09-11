import time
from typing import cast

import psutil
from pydantic.main import BaseModel


class SystemInfoConfig(BaseModel):
    enabled: bool = True
    cpu: bool = True
    memory: bool = True
    temp: bool = True
    disk: bool = True
    uptime: bool = True


class SystemInfo:
    def __init__(self, config: SystemInfoConfig):
        self.config: SystemInfoConfig = config

    def _get_cpu_temperature(self) -> float | None:
        try:
            temp_data = psutil.sensors_temperatures()
        except (AttributeError, OSError):
            return None

        if not temp_data:
            return None

        # Some common Linux CPU sensor names
        sensor_names = [
            "coretemp",  # Intel CPUs
            "k10temp",  # AMD Ryzen/Threadripper
            "zenpower",  # AMD Zen (alternative driver)
            "cpu_thermal",  # Raspberry Pi 4+
            "cpu-thermal",  # Raspberry Pi 3/older
            "thermal-fan-est",  # Nvidia Jetson
            "soc_thermal",  # Some ARM SoCs
        ]

        for sensor_name in sensor_names:
            if sensor_name in temp_data:
                max_temp = max(entry.current for entry in temp_data[sensor_name])
                return round(max_temp, 1)

        return None

    def read(self):
        if not self.config.enabled:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "memory_used_gb": 0,
                "memory_total_gb": 0,
                "temperature": 0,
                "disk_percent": 0,
                "disk_used_gb": 0,
                "disk_total_gb": 0,
                "uptime_seconds": 0,
            }

        # CPU temperature
        temperature = self._get_cpu_temperature()

        # Memory info
        memory = psutil.virtual_memory()
        memory_used_gb: float = round(cast(float, memory.used) / (1000**3), 1)
        memory_total_gb: float = round(cast(float, memory.total) / (1000**3), 1)
        memory_percent: float = round(cast(float, memory.percent), 1)

        # Disk info
        disk_usage = psutil.disk_usage("/")
        disk_used_gb = round(disk_usage.used / (1000**3), 1)
        disk_total_gb = round(disk_usage.total / (1000**3), 1)
        disk_percent = round((disk_usage.used / disk_usage.total) * 100, 1)

        # Uptime
        uptime_seconds = int(time.time() - psutil.boot_time())

        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": memory_percent,
            "memory_used_gb": memory_used_gb,
            "memory_total_gb": memory_total_gb,
            "temperature": temperature,
            "disk_percent": disk_percent,
            "disk_used_gb": disk_used_gb,
            "disk_total_gb": disk_total_gb,
            "uptime_seconds": uptime_seconds,
        }
