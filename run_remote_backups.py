from rsync.config import RemoteConfig
from rsync.backup import backup

config = RemoteConfig(
    "ethan@iron.local",
    "/Users/ethan/Documents",
    "/tmp/remote_directory",
    exclude_file_patterns=[
        "/home/*/.cache/",          # no need for cached files
        "/home/*/.local/",          # nvim plugins and python packages are huge
        "/home/*/.npm/",            # what is the crap in here?
        "**/node_modules/",         # yikes
    ],
    log_file="/tmp/rsync-remote-backups.log"
)

backup(config)
