"""
Author      : Ethan Rietz
Date        : 2022-05-23
Description : Incremental backups script using rsync
"""

import subprocess
import sys
import shutil
from pathlib import Path
from config import Config


def main():
    enforce_system_requirements()


def enforce_system_requirements() -> None:
    if sys.version_info < (3, 9):
        print("Pretty sure this requires python 3.9 or above", file=sys.stderr)
        sys.exit(1)

    if shutil.which("rsync") is None:
        print("rsync is not installed", file=sys.stderr)
        sys.exit(1)


def run_backup(source_dir, destination_dir, rsync_arguments: list[str]) -> int:
    process = subprocess.run(rsync_command, capture_output=True, text=True)


if __name__ == '__main__':
    main()
