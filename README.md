# About

- I wanted incremental backups and I wanted to be convinced that they were
  working properly.
- It is hard to write clean shell scripts so I chose to keep everything in
  python.

# Example Usage

```Python
from rsync.config import Config
from rsync.backup import backup

config = Config(
    source_dir="/home/ethan/Documents",
    destination_dir="/tmp/backup_test",
    exclude_file_patterns=[
        "from-usb-sticks",
        "discord",
    ]
)

backup(config)
```

Also see `./run_backups.py` for how I have configured things.

# TODO

- Do I want to make this work over ssh?
