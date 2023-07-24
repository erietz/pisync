from pathlib import Path
from typing import List, Optional

from fabric import Connection

from pisync.config.base_config import BackupType, BaseConfig, InvalidPathError
from pisync.util import get_time_stamp


class RemoteConfig(BaseConfig):
    def __init__(
        self,
        user_at_hostname: str,
        source_dir: str,
        destination_dir: str,
        exclude_file_patterns: Optional[List[str]] = None,
        log_file: Optional[str] = None,
    ):
        self.user_at_hostname = user_at_hostname
        self.connection: Connection = Connection(user_at_hostname)
        self._ensure_dir_exists_locally(source_dir)
        self.ensure_dir_exists(destination_dir)
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.exclude_file_patterns = exclude_file_patterns
        if log_file is None:
            self.log_file = str(Path.home() / ".local/share/backup/rsync-backups.log")
        else:
            self.log_file = log_file
        self.link_dir = f"{self.destination_dir}/latest"
        self._optionless_rsync_arguments = [
            "--delete",  # delete extraneous files from dest dirs
            "--archive",  # archive mode is -rlptgoD (no -A,-X,-U,-N,-H)
            # NOTE: these options are linux specific and do not work on the
            # macOS version of rsync.
            # "--acls",       # preserve ACLs (implies --perms)
            # "--xattrs",     # preserve extended attributes
            "--verbose",  # increase verbosity
        ]

    def _ensure_dir_exists_locally(self, path: str):
        _path = Path(path)
        if not _path.exists():
            msg = f"{_path} does not exist"
            raise InvalidPathError(msg)
        if not _path.is_dir():
            msg = f"{_path} is not a directory"
            raise InvalidPathError(msg)

    def is_symlink(self, path: str) -> bool:
        """returns true if path is a symbolic link"""
        return self.connection.run(f"test -L {path}", warn=True).ok

    def is_empty_directory(self, path: str) -> bool:
        """returns true if path is a directory and contains no files"""
        return self.connection.run(f'test -z "$(ls -A {path})"', warn=True).ok

    def file_exists(self, path: str) -> bool:
        """returns true if the file or directory exists"""
        return (
            self.connection.run(f"test -d {path}", warn=True).ok or self.connection.run(f"test -f {path}", warn=True).ok
        )

    def unlink(self, path: str) -> None:
        """Remove this file or symbolic link."""
        result = self.connection.run(f"rm {path}", warn=True)
        if not result.ok:
            msg = f"Failed to remove {path}"
            raise FileNotFoundError(msg)

    def rmtree(self, path: str) -> None:
        """Recursively delete directory tree"""
        return self.connection.run(f"rm -r {path}").ok

    def symlink_to(self, symlink: str, file: str) -> None:
        """Make symlink a symbolic link to file."""
        return self.connection.run(f"ln -s {file} {symlink}", warn=True).ok

    def resolve(self, path: str) -> str:
        """Make the path absolute, resolving any symlinks."""
        return self.connection.run(f"realpath {path}", warn=True).stdout.rstrip()

    def ensure_dir_exists(self, path: str) -> None:
        result = self.connection.run(f"test -d {path}", warn=True)
        if not result.ok:
            msg = f"{path} is not a directory"
            raise InvalidPathError(msg)

    def _is_directory(self, path) -> bool:
        return self.connection.run(f"test -d {path}", warn=True).ok

    def generate_new_backup_dir_path(self) -> str:
        """
        :returns: The Path string of the directory where the new backup will be
        written.
        :raises:
            InvalidPathError: If the destination directory already exists
        """
        time_stamp = get_time_stamp()
        new_backup_dir = f"{self.destination_dir}/{time_stamp}"
        exists = self._is_directory(new_backup_dir)
        if exists:
            msg = f"{new_backup_dir} already exists and will get overwritten"
            raise InvalidPathError(msg)
        else:
            return str(new_backup_dir)

    def get_rsync_command(self, new_backup_dir: str, backup_method: BackupType) -> List[str]:
        destination = f"{self.user_at_hostname}:{new_backup_dir}"
        source = self.source_dir
        link_dest = self.link_dir
        option_arguments = []

        if backup_method == BackupType.Incremental:
            option_arguments.append(f"--link-dest={link_dest}")

        if self.exclude_file_patterns is not None:
            for pattern in self.exclude_file_patterns:
                option_arguments.append(f"--exclude={pattern}")

        return ["rsync", *self._optionless_rsync_arguments, *option_arguments, source, destination]
