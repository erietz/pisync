from typing import List
from pathlib import Path
from pisync.config.base_config import _BaseConfig, InvalidPath
from pisync.util import get_time_stamp


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

    def is_symlink(self, path: str) -> bool:
        return Path(path).is_symlink()

    def file_exists(self, path: str) -> bool:
        return Path(path).exists()

    def unlink(self, path: str) -> None:
        Path(path).unlink()

    def symlink_to(self, symlink: str, file: str) -> None:
        Path(symlink).symlink_to(file)

    def resolve(self, path: str) -> str:
        """Make the path absolute, resolving any symlinks."""
        return str(Path(path).resolve())

    def is_empty_directory(self, path: str) -> bool:
        return not any(Path(path).iterdir())

    def ensure_dir_exists(self, path: str):
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
