from config import Config
from backup import backup

# will need to be root to run rsync for a different user
home_directories = Config(
    source_dir="/home/",
    destination_dir="/media/backup_drive_linux/home_directory_backups/",
    exclude_file_patterns=[
        "/home/*/.cache/",          # no need for cached files
        "/home/*/.local/",          # nvim plugins and python packages are huge
        "/home/*/.npm/",            # what is the crap in here?
        "**/node_modules/",         # yikes
    ]
)

large_harddrive = Config(
    source_dir="/mnt/hd2",
    destination_dir="/media/backup_drive_linux/hd2_backups/"
)

backup(home_directories)
backup(large_harddrive)
