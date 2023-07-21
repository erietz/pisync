from pathlib import Path
from typing import List, Optional

from fabric import Connection

from pisync.config.base_config import InvalidPath, _BaseConfig
from pisync.util import get_time_stamp


class RemoteConfig(_BaseConfig):
    def __init__(
        self,
        user_at_hostname: str,
        source_dir: str,
        destination_dir: str,
        exclude_file_patterns: Optional[List[str]] = None,
        log_file: str = Path.home() / ".local/share/backup/rsync-backups.log",
    ):
        self.user_at_hostname = user_at_hostname
        self.connection: Connection = Connection(user_at_hostname)
        self._ensure_dir_exists_locally(source_dir)
        self.ensure_dir_exists(destination_dir)
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.exclude_file_patterns = exclude_file_patterns
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
        path = Path(path)
        if not path.exists():
            msg = f"{path} does not exist"
            raise InvalidPath(msg)
        if not path.is_dir():
            msg = f"{path} is not a directory"
            raise InvalidPath(msg)

    def is_symlink(self, path: str) -> bool:
        """returns true if path is a symbolic link"""
        result = self.connection.run(f"test -L {path}", warn=True)
        return result.ok

    def is_empty_directory(self, path: str) -> bool:
        """returns true if path is a directory and contains no files"""
        result = self.connection.run(f'test -n "$(find {path} -maxdepth 0 -empty)"', warn=True)
        return result.ok

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

    def symlink_to(self, symlink: str, file: str) -> None:
        """Make symlink a symbolic link to file."""
        result = self.connection.run(f"ln -s {file} {symlink}", warn=True)
        return result.ok

    def resolve(self, path: str) -> str:
        """Make the path absolute, resolving any symlinks."""
        result = self.connection.run(f"realpath {path}", warn=True)
        return result.stdout.strip()

    def ensure_dir_exists(self, path: str) -> str:
        result = self.connection.run(f"test -d {path}", warn=True)
        if not result.ok:
            msg = f"{path} is not a directory"
            raise InvalidPath(msg)

    def _is_directory(self, path) -> bool:
        result = self.connection.run(f"test -d {path}", warn=True)
        return result.ok

    def generate_new_backup_dir_path(self) -> str:
        """
        :returns: The Path string of the directory where the new backup will be
        written.
        :raises:
            InvalidPath: If the destination directory already exists
        """
        time_stamp = get_time_stamp()
        new_backup_dir = f"{self.destination_dir}/{time_stamp}"
        exists = self._is_directory(new_backup_dir) or self.file_exists(new_backup_dir)
        if exists:
            msg = f"{new_backup_dir} already exists and will get overwritten"
            raise InvalidPath(msg)
        else:
            return str(new_backup_dir)

    def get_rsync_command(self, new_backup_dir: str, previous_backup_exists: bool = False) -> List[str]:
        destination = f"{self.user_at_hostname}:{new_backup_dir}"
        source = self.source_dir
        link_dest = self.link_dir
        option_arguments = []

        if previous_backup_exists:
            option_arguments.append(f"--link-dest={link_dest}")

        if self.exclude_file_patterns is not None:
            for pattern in self.exclude_file_patterns:
                option_arguments.append(f"--exclude={pattern}")

        return ["rsync", *self._optionless_rsync_arguments, *option_arguments, source, destination]
