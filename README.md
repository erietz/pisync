# About

- I wanted incremental backups and I wanted to be convinced that they were
  working properly.
- It is hard to write clean shell scripts so I chose to keep everything in
  python.

# Example Usage

```Python
from rsync.config import Config
from rsync.backup import backup

documents = Config(
    source_dir="/home/ethan/Documents",
    destination_dir="/tmp/backup_test",
    exclude_file_patterns=[
        "**/node_modules",
        "junk/",
    ],
    log_file="/tmp/backup-logs/backups.log"
)

backup(documents)
```

Also see `./run_backups.py` for how I have configured things.

# Notes

## Safety

- Creating a `Config` object will fail if `source_dir` or `destination_dir` do
  not exist or are not directories.
- If `destination_dir` is not empty, it is assumed that a previous backup
  exists.
  - The backup will not run if `destination_dir` is not empty and there is not
    a symlink `destination_dir/latest` pointing to the latest backup.
  - The contents of `source_dir` are compared to `destination_dir/latest`
    during the incremental backup and the changes are written to
    `destination_dir/<current date/time>`.
  - Therefore, you need to ensure that `destination_dir` is empty which will
    start a fresh complete backup, or you can manually create the
    `destination_dir/latest` symlink to continue incrementally.

## Logging

- By default, a default log file will be created (if it does not exists) and
  appended to at `~/.local/share/backup/rsync-backups.log`.
- **NOTE**: If you run your script as `sudo`, the home directory of the root
  user is probably `/root` rather than your `~/` directory.
- If you want the log file to still go the your home directory when you run as
  root, use this `sudo -E python3 ./run_backups.py`
- You can also specify the log file location in your `Config`.

# TODO

- Make this work over ssh.
