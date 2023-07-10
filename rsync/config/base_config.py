from abc import ABC, abstractmethod
from typing import List


class InvalidPath(Exception):
    pass


class _BaseConfig(ABC):
    source_dir: str
    destination_dir: str
    exclude_file_patterns: List[str]
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
    def symlink_to(self, path: str, target: str) -> None:
        """Make this path a symbolic link to target."""
        pass

    @abstractmethod
    def resolve(self, path: str) -> str:
        """Make the path absolute, resolving any symlinks."""
        pass

    @abstractmethod
    def ensure_dir_exists(self, path: str):
        """
        :returns: The Path object from the input path str
        :raises:
            InvalidPath: If path does not exist or is not a directory
        """
        pass

    @abstractmethod
    def generate_new_backup_dir_path(self) -> str:
        """
        :returns: The Path string of the directory where the new backup will be
        written.
        :raises:
            InvalidPath: If the destination directory already exists
        """
        pass

    @abstractmethod
    def get_rsync_command(self, new_backup_dir: str, previous_backup_exists: bool = False):
        pass
