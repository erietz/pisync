from typing import List
from pathlib import Path
from rsync.base_config import _BaseConfig, InvalidPath
from rsync.util import get_time_stamp


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
        self.source_dir = self.ensure_dir_exists(source_dir)
        self.destination_dir = self.ensure_dir_exists(destination_dir)
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

    @staticmethod
    def ensure_dir_exists(path: str) -> str:
        pass

    def generate_new_backup_dir_path(self) -> str:
        pass

    def get_rsync_command(self) -> List[str]:
        pass
