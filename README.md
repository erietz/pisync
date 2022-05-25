# About

I wanted incremental backups and I wanted to be convinced that they were
working properly. It is hard to write good shell scripts so I chose to keep
everything in python. I wanted to keep things simple so this is not a cli tool.

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


# TODO

- Add logging
