import sys

from pisync import LocalConfig, RemoteConfig, backup

# will need to be root to run rsync for a different users home dir

log_file = "/home/ethan/.local/share/backup/rsync-backups.log"
home_dir_exclude_file_patterns = [
    "/home/*/.cache/",  # no need for cached files
    "/home/*/.local/",  # nvim plugins and python packages are huge
    "/home/*/.npm/",  # what is the crap in here?
    "**/node_modules/",  # yikes
]

local_home_directories = LocalConfig(
    source_dir="/home/",
    destination_dir="/media/backup_drive_linux/home_directory_backups/",
    exclude_file_patterns=home_dir_exclude_file_patterns,
    log_file=log_file,
)

local_large_harddrive = LocalConfig(
    source_dir="/mnt/hd2", destination_dir="/media/backup_drive_linux/hd2_backups/", log_file=log_file
)

remote_home_directories = RemoteConfig(
    user_at_hostname="ethan@hydrogen.local",
    source_dir="/home/",
    destination_dir="/mnt/hd/sulfur_backups/home_directory_backups",
    exclude_file_patterns=home_dir_exclude_file_patterns,
    log_file=log_file,
)

remote_large_harddrive = RemoteConfig(
    user_at_hostname="ethan@hydrogen.local",
    source_dir="/mnt/hd2/",
    destination_dir="/mnt/hd/sulfur_backups/hd2_backups",
    log_file=log_file,
)

success = True

try:
    backup(local_home_directories)
    backup(local_large_harddrive)
except Exception as e:
    success = False
    print(e)

try:
    backup(remote_home_directories)
    backup(remote_large_harddrive)
except Exception as e:
    success = False
    print(e)

if not success:
    sys.exit(1)
