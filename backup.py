"""
Author      : Ethan Rietz
Date        : 2022-05-23
Description : Incremental backups script using rsync
"""

import subprocess
import sys
import shutil
import time
from datetime import datetime
from pathlib import Path

from config import Config


def main(config: Config):
    enforce_system_requirements()
    time_stamp = get_time_stamp()
    rsync_command = config.get_rsync_command(time_stamp)
    exit_code = run_backup(rsync_command)

    if exit_code == 0:
        if config.link_dir.exists():
            config.link_dir.unlink()
        backup_path = config.backup_dir / time_stamp
        config.link_dir.symlink_to(backup_path)
    else:
        # backup failed, we should delete the most recent backup
        if backup_path.exists():
            shutil.rmtree(backup_path)


def enforce_system_requirements() -> None:
    if sys.version_info < (3, 9):
        print("Pretty sure this requires python 3.9 or above", file=sys.stderr)
        sys.exit(1)

    if shutil.which("rsync") is None:
        print("rsync is not installed", file=sys.stderr)
        sys.exit(1)


def get_time_stamp() -> str:
    now = datetime.now()
    stamp = now.strftime("%d-%m-%Y-%H-%M-%S")
    return str(stamp)


def run_backup(rsync_command: list[str]) -> int:
    print("Running ", rsync_command)

    start_time = time.perf_counter()
    process = subprocess.run(rsync_command)
    end_time = time.perf_counter()

    print("Finished running ", rsync_command)
    print("Time elapsed", end_time - start_time)

    return process.returncode


if __name__ == '__main__':
    config = Config("/home/ethan/Documents", "/tmp/backup/my_implementation")
    main(config)
