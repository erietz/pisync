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

    @staticmethod
    @abstractmethod
    def is_symlink(path: str) -> bool:
        """returns true if path is a symbolic link"""
        pass

    @staticmethod
    @abstractmethod
    def is_empty_directory(path: str) -> bool:
        """returns true if path is a directory and contains no files"""
        pass

    @staticmethod
    @abstractmethod
    def file_exists(path: str) -> bool:
        """returns true if the file or directory exists"""
        pass

    @staticmethod
    @abstractmethod
    def unlink(path: str) -> None:
        """Remove this file or symbolic link."""
        pass

    @staticmethod
    @abstractmethod
    def symlink_to(path: str, target: str) -> None:
        """Make this path a symbolic link to target."""
        pass

    @staticmethod
    @abstractmethod
    def resolve(path: str) -> str:
        """Make the path absolute, resolving any symlinks."""
        pass

    @staticmethod
    @abstractmethod
    def ensure_dir_exists(path: str):
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

    def get_rsync_command(
            self,
            new_backup_dir: str,
            previous_backup_exists: bool = False
    ) -> List[str]:
        destination = new_backup_dir
        source = self.source_dir
        link_dest = self.link_dir
        option_arguments = []

        if previous_backup_exists:
            option_arguments.append(f"--link-dest={link_dest}")

        if self.exclude_file_patterns is not None:
            for pattern in self.exclude_file_patterns:
                option_arguments.append(f"--exclude={pattern}")

        return [
            "rsync",
            *self._optionless_rsync_arguments,
            *option_arguments,
            source,
            destination
        ]
