"""
Author      : Ethan Rietz
Date        : 2022-05-23
Description : Incremental backups script using rsync.

Notes:

https://linuxconfig.org/how-to-create-incremental-backups-using-rsync-on-linux
"""

import subprocess
import sys
import shutil
import time
from typing import List
from pathlib import Path

from config import Config


def backup(config: Config) -> Path:
    """
    Returns the path to the latest backup directory
    """
    enforce_system_requirements()
    latest_backup_path = config.generate_new_backup_dir_path()

    prev_backup_exists = not directory_is_empty(config.destination_dir)

    rsync_command = config.get_rsync_command(
        latest_backup_path,
        previous_backup_exists=prev_backup_exists
    )

    exit_code = run_rsync(rsync_command)

    if exit_code == 0:
        if config.link_dir.exists():
            config.link_dir.unlink()
        config.link_dir.symlink_to(latest_backup_path)
        return latest_backup_path
    else:
        # backup failed, we should delete the most recent backup
        if latest_backup_path.exists():
            shutil.rmtree(latest_backup_path)
        return None


def enforce_system_requirements() -> None:
    if sys.version_info < (3, 6):
        print("Requires Python 3.6 due to f strings", file=sys.stderr)
        sys.exit(1)

    if shutil.which("rsync") is None:
        print("rsync is not installed", file=sys.stderr)
        sys.exit(1)


def directory_is_empty(dir: Path) -> bool:
    return not any(dir.iterdir())


def run_rsync(rsync_command: List[str]) -> int:
    print("Running ", rsync_command)

    start_time = time.perf_counter()
    process = subprocess.run(rsync_command)
    end_time = time.perf_counter()

    print("Finished running ", rsync_command)
    print("Time elapsed", end_time - start_time)

    return process.returncode
