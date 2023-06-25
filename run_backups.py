from rsync.config import LocalConfig
from rsync.backup import backup


LOG_FILE = "/home/ethan/.local/share/backup/rsync-backups.log"

# will need to be root to run rsync for a different user
HOME_DIRECTORIES = LocalConfig(
    source_dir="/home/",
    destination_dir="/media/backup_drive_linux/home_directory_backups/",
    exclude_file_patterns=[
        "/home/*/.cache/",          # no need for cached files
        "/home/*/.local/",          # nvim plugins and python packages are huge
        "/home/*/.npm/",            # what is the crap in here?
        "**/node_modules/",         # yikes
    ],
    log_file=LOG_FILE
)

LARGE_HARDDRIVE = LocalConfig(
    source_dir="/mnt/hd2",
    destination_dir="/media/backup_drive_linux/hd2_backups/",
    log_file=LOG_FILE
)

backup(HOME_DIRECTORIES)
backup(LARGE_HARDDRIVE)
