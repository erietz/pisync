"""
Author      : Ethan Rietz
Date        : 2022-05-23
Description : Incremental backups script using rsync.

Notes:

https://linuxconfig.org/how-to-create-incremental-backups-using-rsync-on-linux
"""

from pathlib import Path
from typing import List
import logging
import shutil
import subprocess
import sys
import time

from rsync.config import Config

def backup(config: Config) -> Path:
    """
    Returns the path to the latest backup directory
    """
    enforce_system_requirements()
    configure_logging(config.log_file)

    latest_backup_path = config.generate_new_backup_dir_path()

    prev_backup_exists = not directory_is_empty(config.destination_dir)
    if prev_backup_exists and not config.link_dir.is_symlink():
        msg = (
            f"{config.destination_dir} exists and is not empty indicating "
            "that a previous backup exists. However, there is no symlink "
            f"at {config.link_dir} pointing to the most recent backup. "
            "This would result a complete backup backup of "
            f"{config.source_dir} rather than an incremental backup. "
            "This is probably not the intended behavior so we are aborting. "
            f"Make sure that {config.destination_dir} is empty or manually "
            f"create the necessary symlink at {config.link_dir}."
            )
        logging.error(msg)
        raise Exception(
            msg
        )

    if prev_backup_exists:
        logging.info(f"Starting incremental backup from {config.link_dir.resolve()}")
    else:
        logging.info(f"No previous backup found at {config.destination_dir}")
        logging.info(f"Starting a fresh complete backup from {config.source_dir} to {config.destination_dir}")

    rsync_command = config.get_rsync_command(
        latest_backup_path,
        previous_backup_exists=prev_backup_exists
    )

    exit_code = run_rsync(rsync_command)

    if exit_code == 0:
        logging.info("Finished backup successfully")
        if config.link_dir.exists():
            config.link_dir.unlink()
        config.link_dir.symlink_to(latest_backup_path)
        logging.info(f"Symlink created from {config.link_dir} to {latest_backup_path}")
        return latest_backup_path
    else:
        # backup failed, we should delete the most recent backup
        logging.error(f"Backup failed. Rsync exit code: {exit_code}")
        if latest_backup_path.exists():
            logging.info(f"Deleting failed backup at {latest_backup_path}")
            shutil.rmtree(latest_backup_path)
        return None


def configure_logging(filename: str):
    filename = Path(filename)
    if not filename.parent.exists():
        filename.parent.mkdir(parents=True)

    logging.basicConfig(
        filename=str(filename.resolve()),
        filemode="a",
        format='%(levelname)s\t%(asctime)s\t%(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.INFO
    )


def enforce_system_requirements() -> None:
    if sys.version_info < (3, 6):
        logging.critical("Requires Python 3.6 due to f strings")
        sys.exit(1)

    if shutil.which("rsync") is None:
        logging.critical("rsync is not installed")
        sys.exit(1)


def directory_is_empty(path: Path) -> bool:
    return not any(path.iterdir())


def run_rsync(rsync_command: List[str]) -> int:
    logging.info(f"Running {rsync_command}")

    start_time = time.perf_counter()
    #---------------------------------------------------------------------------
    # stdout and stderr of subprocess are not captured and therefore are still
    # sent as streams to the same location as calling process. 
    #
    # TODO: Running like so will put rsync stderr into the log file which may
    # or may not be wanted:
    #
    #   `sudo python3 ./run_backups.py 2>$HOME/backups.log`
    #
    # Another solution would be to log to a file instead of stderr.
    #---------------------------------------------------------------------------
    process = subprocess.run(rsync_command)
    end_time = time.perf_counter()

    logging.info(f"Time elapsed {end_time - start_time} seconds")

    return process.returncode
