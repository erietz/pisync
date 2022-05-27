from pathlib import Path
from datetime import datetime
from typing import List


class InvalidPath(Exception):
    pass


class Config:
    """Configuration for rsync backups"""
    def __init__(
        self,
        source_dir: str,
        destination_dir: str,
        exclude_file_patterns: List[str] = None,
        log_file: str = Path.home() / ".local/share/backup/rsync-backups.log"
    ):
        self.source_dir = self.ensure_dir_exists(source_dir)
        self.destination_dir = self.ensure_dir_exists(destination_dir)
        self.exclude_file_patterns = exclude_file_patterns
        self.log_file = log_file
        self.link_dir = self.destination_dir / "latest"
        self._optionless_rsync_arguments = [
            "--delete",     # delete extraneous files from dest dirs
            "--archive",    # archive mode is -rlptgoD (no -A,-X,-U,-N,-H)
            "--acls",       # preserve ACLs (implies --perms)
            "--xattrs",     # preserve extended attributes
            "--verbose",    # increase verbosity
        ]

    def ensure_dir_exists(self, dir: str) -> Path:
        dir = Path(dir)
        if not dir.exists():
            raise InvalidPath(f"{dir} does not exist")
        if not dir.is_dir():
            raise InvalidPath(f"{dir} is not a directory")
        return dir

    @staticmethod
    def _get_time_stamp() -> str:
        now = datetime.now()
        stamp = now.strftime("%Y-%m-%d-%H-%M-%S")
        return str(stamp)

    def generate_new_backup_dir_path(self) -> Path:
        time_stamp = self._get_time_stamp()
        new_backup_dir = self.destination_dir / time_stamp
        if new_backup_dir.exists():
            raise InvalidPath(f"{dir} already exists and will get overwritten")
        else:
            return new_backup_dir

    def get_rsync_command(
            self,
            new_backup_dir: Path,
            previous_backup_exists: bool = False
    ) -> List[str]:
        destination = str(new_backup_dir)
        source = str(self.source_dir)
        link_dest = str(self.link_dir)
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
