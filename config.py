import sys
from pathlib import Path
from typing import List


class InvalidPath(Exception):
    pass


class Config:
    """Configuration for rsync backups"""
    def __init__(
        self,
        source_dir: str,
        destination_dir: str,
        exclude_file_patterns: List[str] = None
    ):
        self.source_dir = self._validate_dir(source_dir)
        self.destination_dir = self._validate_dir(destination_dir)
        self.link_dir = self.destination_dir / "latest"
        self.exclude_file_patterns = exclude_file_patterns
        self._optionless_rsync_arguments = [
            "--delete",     # delete extraneous files from dest dirs
            "--archive",    # archive mode is -rlptgoD (no -A,-X,-U,-N,-H)
            "--acls",       # preserve ACLs (implies --perms)
            "--xattrs",     # preserve extended attributes
            "--verbose",    # increase verbosity
        ]

    def _validate_dir(self, dir: str) -> Path:
        dir = Path(dir)
        if not dir.exists():
            raise InvalidPath(f"{dir} does not exist")
        if not dir.is_dir():
            raise InvalidPath(f"{dir} is not a directory")
        return dir

    def get_rsync_command(self, time_stamp: str) -> List[str]:
        source = str(self.source_dir)
        destination = str(self.destination_dir / time_stamp)
        link_dest = str(self.link_dir)

        option_arguments = []
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
