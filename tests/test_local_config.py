import pytest
from pathlib import Path
from rsync.config import LocalConfig, InvalidPath
from typing import Tuple


@pytest.fixture
def home() -> str:
    return str(Path("~/").expanduser())


@pytest.fixture
def tmp() -> str:
    return "/tmp"


@pytest.fixture
def home_tmp_config(home, tmp) -> Tuple[str, str, LocalConfig]:
    return home, tmp, LocalConfig(home, tmp)


class TestInitConfig:
    def test_valid_params_no_exceptions(self, home_tmp_config, optionless_arguments):
        home, tmp, config = home_tmp_config
        assert str(config.source_dir) == home
        assert str(config.destination_dir) == tmp
        assert str(config.link_dir) == f"{tmp}/latest"
        assert config.exclude_file_patterns is None
        assert config._optionless_rsync_arguments == optionless_arguments

    def test_source_does_not_exist_throws_invalid_path(self):
        source = "/bad/directory/path/here/does/not/exist"
        dest = "/tmp"
        with pytest.raises(InvalidPath):
            _ = LocalConfig(source, dest)

    def test_destination_does_not_exist_throws_invalid_path(self):
        source = str(Path("~/").expanduser())
        dest = "/bad/directory/path/here/does/not/exist"
        with pytest.raises(InvalidPath):
            _ = LocalConfig(source, dest)


class TestGetRsyncCommand:
    def test_no_previous_backup(self, home_tmp_config, optionless_arguments):
        home, tmp, config = home_tmp_config
        new_backup_dir = config.generate_new_backup_dir_path()
        rsync_cmd = config.get_rsync_command(new_backup_dir, previous_backup_exists=False)

        # For example: /tmp/2023-07-14-17-24-23
        assert new_backup_dir.startswith("/tmp/")
        assert rsync_cmd == ["rsync", *optionless_arguments, home, new_backup_dir]

    def test_previous_backup_exists(self, home_tmp_config, optionless_arguments):
        home, tmp, config = home_tmp_config
        new_backup_dir = config.generate_new_backup_dir_path()
        rsync_cmd = config.get_rsync_command(new_backup_dir, previous_backup_exists=True)

        # For example: /tmp/2023-07-14-17-24-23
        assert new_backup_dir.startswith("/tmp/")
        assert rsync_cmd == [
            "rsync",
            *optionless_arguments,
            f"--link-dest={tmp}/latest",
            home,
            new_backup_dir
        ]

    def test_exclude_patterns(self, home, tmp, optionless_arguments):
        exclude_file_patterns = [
            "/exclude/path1",
            "/exclude/path2",
            "/exclude/path3/**/*.bak"
        ]
        config = LocalConfig(home, tmp, exclude_file_patterns)
        new_backup_dir = config.generate_new_backup_dir_path()
        rsync_cmd = config.get_rsync_command(new_backup_dir, previous_backup_exists=False)

        # For example: /tmp/2023-07-14-17-24-23
        assert new_backup_dir.startswith("/tmp/")
        assert rsync_cmd == [
            "rsync",
            *optionless_arguments,
            *map(lambda p: f"--exclude={p}", exclude_file_patterns),
            home,
            new_backup_dir
        ]
