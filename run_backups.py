from config import Config
from backup import backup

config = Config(
    source_dir="/home/ethan/Documents",
    destination_dir="/tmp/backup_test",
    exclude_file_patterns=[
        "from-usb-sticks",
        "discord",
    ]
)

backup(config)
