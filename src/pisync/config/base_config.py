from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional


class InvalidPathError(Exception):
    pass


class BackupType(Enum):
    Complete = 1
    Incremental = 2


class BaseConfig(ABC):
    source_dir: str
    destination_dir: str
    exclude_file_patterns: Optional[List[str]]
    log_file: str
    link_dir: str

    @abstractmethod
    def is_symlink(self, path: str) -> bool:
        """returns true if path is a symbolic link"""
        pass

    @abstractmethod
    def is_empty_directory(self, path: str) -> bool:
        """returns true if path is a directory and contains no files"""
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """returns true if the file or directory exists"""
        pass

    @abstractmethod
    def unlink(self, path: str) -> None:
        """Remove this file or symbolic link."""
        pass

    @abstractmethod
    def rmtree(self, path: str) -> None:
        """Recursively delete directory tree"""
        pass

    @abstractmethod
    def symlink_to(self, symlink: str, file: str) -> None:
        """Make symlink a symbolic link to file."""
        pass

    @abstractmethod
    def resolve(self, path: str) -> str:
        """Make the path absolute, resolving any symlinks."""
        pass

    @abstractmethod
    def ensure_dir_exists(self, path: str) -> None:
        """
        :returns: The Path object from the input path str
        :raises:
            InvalidPathError: If path does not exist or is not a directory
        """
        pass

    @abstractmethod
    def generate_new_backup_dir_path(self) -> str:
        """
        :returns: The Path string of the directory where the new backup will be
        written.
        :raises:
            InvalidPathError: If the destination directory already exists
        """
        pass

    @abstractmethod
    def get_rsync_command(self, new_backup_dir: str, backup_method: BackupType):
        pass
