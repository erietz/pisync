from abc import ABC, abstractmethod
from typing import List
from pathlib import Path


class InvalidPath(Exception):
    pass


class _BaseConfig(ABC):
    @abstractmethod
    def __init__(
        self,
        source_dir: str,
        destination_dir: str,
        exclude_file_patterns: List[str] = None,
        log_file: str = Path.home() / ".local/share/backup/rsync-backups.log"
    ):
        """
        :raises:
            Exception: If the configuration is invalid.
        """
        pass

    @staticmethod
    @abstractmethod
    def ensure_dir_exists(path: str) -> Path:
        """
        :returns: The Path object from the input path str
        :raises:
            InvalidPath: If path does not exist or is not a directory
        """
        pass

    @abstractmethod
    def generate_new_backup_dir_path(self) -> Path:
        """
        :returns: The Path object of the directory where the new backup will be
        written.
        :raises:
            InvalidPath: If the destination directory already exists
        """
        pass

    @abstractmethod
    def get_rsync_command(self) -> List[str]:
        """
        :returns: The formatted rsync command line arguments from the Config.
        """
        pass
