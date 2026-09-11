import io
import json
import logging
import tomllib as toml
from datetime import datetime
from pathlib import Path
from typing import cast
from zoneinfo import ZoneInfo

import tzlocal
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

LOG_FILE: Path = Path.home() / ".cache" / "sights-log.txt"


class ConfigManager:
    def __init__(self):
        self.metadata: Path = Path("config/metadata.json")
        self.config_dir: Path = Path("config")
        self.backup_dir: Path = Path("config/backups")
        self.max_backups: int = 10
        self.default_config: str = "default.toml"
        self.timezone: str = tzlocal.get_localzone_name()

    def get_active_config_name(self) -> str:
        try:
            data = cast(dict[str, str], json.loads(self.metadata.read_text()))
            return data.get("active_config_file", self.default_config)
        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Could not read metadata, using default: {e}")
            return self.default_config

    def get_active_config_path(self):
        return self.config_dir / self.get_active_config_name()

    def list_config_files(self) -> list[str]:
        if not self.config_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Config directory not found",
            )
        return sorted([f.name for f in self.config_dir.glob("*.toml")])

    def validate_toml(self, content: str | bytes) -> None:
        try:
            if isinstance(content, str):
                content = content.encode("utf-8")
            _ = toml.load(io.BytesIO(content))
        except toml.TOMLDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid TOML content: {e}",
            )

    def validate_filename(self, filename: str):
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename: path traversal not allowed",
            )

        if not filename.endswith(".toml"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have .toml extension",
            )

    def create_backup(self, config_path: Path):
        if not config_path.exists():
            return None

        self.backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(ZoneInfo(self.timezone)).strftime("%Y%m%d_%H%M%S")
        backup_name = f"{config_path.stem}_{timestamp}.toml"
        backup_path = self.backup_dir / backup_name

        _ = backup_path.write_bytes(config_path.read_bytes())
        logger.info(f"Created backup: {backup_path}")

        self._cleanup_old_backups(config_path.stem)

        return backup_path

    def _cleanup_old_backups(self, config_stem: str):
        pattern = f"{config_stem}_*.toml"
        backups = sorted(
            self.backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True
        )

        for old_backup in backups[self.max_backups :]:
            old_backup.unlink()
            logger.info(f"Removed old backup: {old_backup}")

    def list_backups(self):
        config_path = self.get_active_config_path()

        if not self.backup_dir.exists():
            backups = {"backups": None, "config": config_path.name}
            return backups

        pattern = f"{config_path.stem}_*.toml"
        backups = sorted(
            self.backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True
        )

        backup_list = [
            {
                "filename": backup.name,
                "timestamp": datetime.fromtimestamp(
                    backup.stat().st_mtime, tz=ZoneInfo(self.timezone)
                )
                .astimezone()
                .strftime("%Y-%m-%d %H:%M:%S"),
                "size": backup.stat().st_size,
            }
            for backup in backups
        ]

        backups = {"backups": backup_list, "config": config_path.name}

        return backups

    def get_backup_content(self, filename: str):
        self.validate_filename(filename)

        backup_path = self.backup_dir / filename

        if not backup_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Backup file not found: {filename}",
            )

        try:
            return {"content": backup_path.read_text(), "filename": filename}
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Error reading backup file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error reading backup file: {e}",
            )

    def switch_config(self, filename: str):
        self.validate_filename(filename)

        new_config_path = self.config_dir / filename

        if not new_config_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Config file not found: {filename}",
            )

        self.validate_toml(new_config_path.read_bytes())

        try:
            data: dict[str, str] = (
                json.loads(self.metadata.read_text()) if self.metadata.exists() else {}
            )
            data["active_config_file"] = filename
            _ = self.metadata.write_text(json.dumps(data, indent=2))
            logger.info(f"Switched config to {filename}")
        except OSError as e:
            logger.error(f"Error switching config: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error switching config: {e}",
            )

    def update_config(self, content: str):
        config_path = self.get_active_config_path()

        self.validate_toml(content)

        if config_path.exists():
            _ = self.create_backup(config_path)

        try:
            _ = config_path.write_text(content)
            logger.info(f"Updated config: {config_path.name}")
        except OSError as e:
            logger.error(f"Error updating config: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating config: {e}",
            )
