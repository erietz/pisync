`pisync` is a simple library to aid in writing incremental backup scripts to
local or remote machines. The only dependencies are [rsync][rsync],
[python][python] >= v3.6, [fabric][fabric], and ssh keys copied over to a unix
machine if doing a remote backup. *Note:* no dependencies are required on the
remote machine.

# Installation

`pip install pisync`

# Example Usage

```Python
from pisync import LocalConfig, RemoteConfig, backup

local_docs = LocalConfig(
    source_dir="/home/ethan/Documents", # local machine
    destination_dir="/tmp/backup_test", # local machine
    exclude_file_patterns=[
        "**/node_modules",
        "junk/",
    ],
    log_file="/tmp/backup-logs/backups.log" # local machine
)

remote_docs = RemoteConfig(
    user_at_hostname="ethan@hydrogen.local", # remote machine
    source_dir="/home/ethan/Documents", # local machine
    destination_dir="/tmp/backup_test", # remote machine
    exclude_file_patterns=[
        "**/node_modules",
        "junk/",
    ],
    log_file="/tmp/backup-logs/backups.log" # local machine
)

backup(local_docs)
backup(remote_docs)
```

Also see [an example config](./examples/run_backups.py) for how I backup my
home server both locally and to an offsite [raspberry pi][pi].

# Notes

## Safety

- Creating a `LocalConfig` or `RemoteConfig` object will fail if `source_dir`
  or `destination_dir` do not exist or are not directories.
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
- You can also specify the log file location in your config.
    - Hard coding the log file path solves some of the quirks that you can run
      into when using a cron job.


## Running tests

The unit/integration tests require password-less login to localhost as the
"remote" machine.

```
ssh-copy-id $USER@localhost
git clone https://github.com/erietz/pisync
cd pisync
pip install -e .
make test
```

[rsync]: https://github.com/WayneD/rsync
[python]: https://www.python.org/
[fabric]: https://github.com/fabric/fabric
[pi]: https://www.raspberrypi.com/
