from typing import List
from pathlib import Path
from rsync.base_config import _BaseConfig, InvalidPath
from rsync.util import get_time_stamp
from fabric import Connection


class LocalConfig(_BaseConfig):
    def __init__(
        self,
        source_dir: str,
        destination_dir: str,
        exclude_file_patterns: List[str] = None,
        log_file: str = str(Path.home() / ".local/share/backup/rsync-backups.log")
    ):
        self.ensure_dir_exists(source_dir)
        self.ensure_dir_exists(destination_dir)
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.exclude_file_patterns = exclude_file_patterns
        self.log_file = log_file
        self.link_dir = str(Path(self.destination_dir) / "latest")
        self._optionless_rsync_arguments = [
            "--delete",     # delete extraneous files from dest dirs
            "--archive",    # archive mode is -rlptgoD (no -A,-X,-U,-N,-H)
            "--verbose",    # increase verbosity
        ]

    @staticmethod
    def is_symlink(path: str) -> bool:
        return Path(path).is_symlink()

    @staticmethod
    def file_exists(path: str) -> bool:
        return Path(path).exists()

    @staticmethod
    def unlink(path: str) -> None:
        return Path(path).unlink()

    @staticmethod
    def symlink_to(path: str, target: str) -> None:
        return Path(path).symlink_to(target)

    @staticmethod
    def resolve(path: str) -> str:
        """Make the path absolute, resolving any symlinks."""
        return Path(path).resolve()

    @staticmethod
    def is_empty_directory(path: str) -> bool:
        return not any(Path(path).iterdir())

    @staticmethod
    def ensure_dir_exists(path: str):
        path = Path(path)
        if not path.exists():
            raise InvalidPath(f"{path} does not exist")
        if not path.is_dir():
            raise InvalidPath(f"{path} is not a directory")

    def generate_new_backup_dir_path(self) -> str:
        time_stamp = get_time_stamp()
        new_backup_dir = Path(self.destination_dir) / time_stamp
        if new_backup_dir.exists():
            raise InvalidPath(
                f"{new_backup_dir} already exists and will get overwritten"
            )
        else:
            return str(new_backup_dir)


class RemoteConfig(_BaseConfig):
    def __init__(
        self,
        user_at_hostname: str,
        source_dir: str,
        destination_dir: str,
        exclude_file_patterns: List[str] = None,
        log_file: str = Path.home() / ".local/share/backup/rsync-backups.log",
    ):
        self.connection: Connection = Connection(user_at_hostname)
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.exclude_file_patterns = exclude_file_patterns
        self.log_file = log_file
        self.link_dir = self.destination_dir / "latest"
        self._optionless_rsync_arguments = [
            "--delete",     # delete extraneous files from dest dirs
            "--archive",    # archive mode is -rlptgoD (no -A,-X,-U,-N,-H)

            # NOTE: these options are linux specific and do not work on the
            # macOS version of rsync.
            # "--acls",       # preserve ACLs (implies --perms)
            # "--xattrs",     # preserve extended attributes

            "--verbose",    # increase verbosity
        ]

    def ensure_dir_exists(self, path: str) -> str:
        result = self.connection.run(f"test -d {path}")
        if not result.ok:
            raise InvalidPath(f"{path} is not a directory")

    def is_symlink(self, path: str) -> bool:
        """returns true if path is a symbolic link"""
        result = self.connection.run(f"test -L {path}")
        return result.ok

    @staticmethod
    def is_empty_directory(path: str) -> bool:
        """returns true if path is a directory and contains no files"""
        pass

    @staticmethod
    def file_exists(path: str) -> bool:
        """returns true if the file or directory exists"""
        pass

    @staticmethod
    def unlink(path: str) -> None:
        """Remove this file or symbolic link."""
        pass

    @staticmethod
    def symlink_to(path: str, target: str) -> None:
        """Make this path a symbolic link to target."""
        pass

    @staticmethod
    def resolve(path: str) -> str:
        """Make the path absolute, resolving any symlinks."""
        pass

    def generate_new_backup_dir_path(self) -> str:
        """
        :returns: The Path string of the directory where the new backup will be
        written.
        :raises:
            InvalidPath: If the destination directory already exists
        """
        pass
