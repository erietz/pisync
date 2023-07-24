import getpass
from pathlib import Path
from typing import Tuple

import pytest

from pisync.config import BackupType, InvalidPathError, RemoteConfig
from pisync.util import get_time_stamp


@pytest.fixture
def home() -> str:
    return str(Path("~/").expanduser())


@pytest.fixture
def tmp(tmp_path) -> str:
    return tmp_path


@pytest.fixture
def user_at_localhost() -> str:
    return f"{getpass.getuser()}@localhost"


@pytest.fixture
def home_tmp_config(user_at_localhost, home, tmp) -> Tuple[str, str, RemoteConfig]:
    return home, tmp, RemoteConfig(user_at_localhost, home, tmp)


class TestInitConfig:
    def test_valid_params_no_exceptions(self, home_tmp_config, optionless_arguments):
        home, tmp, config = home_tmp_config
        assert str(config.source_dir) == home
        assert str(config.destination_dir) == str(tmp)
        assert str(config.link_dir) == f"{tmp}/latest"
        assert config.exclude_file_patterns is None
        assert config._optionless_rsync_arguments == optionless_arguments

    def test_source_does_not_exist_throws_invalid_path(self, user_at_localhost, tmp):
        source = "/bad/directory/path/here/does/not/exist"
        dest = tmp
        with pytest.raises(InvalidPathError):
            _ = RemoteConfig(user_at_localhost, source, dest)

    def test_destination_does_not_exist_throws_invalid_path(self, user_at_localhost):
        source = str(Path("~/").expanduser())
        dest = "/bad/directory/path/here/does/not/exist"
        with pytest.raises(InvalidPathError):
            _ = RemoteConfig(user_at_localhost, source, dest)


class TestGetRsyncCommand:
    def test_no_previous_backup(self, home_tmp_config, optionless_arguments, user_at_localhost):
        home, tmp, config = home_tmp_config
        new_backup_dir = config.generate_new_backup_dir_path()
        rsync_cmd = config.get_rsync_command(new_backup_dir, backup_method=BackupType.Complete)

        # For example: /tmp/2023-07-14-17-24-23
        assert new_backup_dir.startswith(str(tmp.parts[0]))
        assert rsync_cmd == ["rsync", *optionless_arguments, home, f"{user_at_localhost}:{new_backup_dir}"]

    def test_previous_backup_exists(self, home_tmp_config, optionless_arguments, user_at_localhost):
        home, tmp, config = home_tmp_config
        new_backup_dir = config.generate_new_backup_dir_path()
        rsync_cmd = config.get_rsync_command(new_backup_dir, backup_method=BackupType.Incremental)

        # For example: /tmp/2023-07-14-17-24-23
        assert new_backup_dir.startswith(str(tmp.parts[0]))
        assert rsync_cmd == [
            "rsync",
            *optionless_arguments,
            f"--link-dest={tmp}/latest",
            home,
            f"{user_at_localhost}:{new_backup_dir}",
        ]

    def test_exclude_patterns(self, home, tmp, optionless_arguments, user_at_localhost):
        exclude_file_patterns = ["/exclude/path1", "/exclude/path2", "/exclude/path3/**/*.bak"]
        config = RemoteConfig(user_at_localhost, home, tmp, exclude_file_patterns)
        new_backup_dir = config.generate_new_backup_dir_path()
        rsync_cmd = config.get_rsync_command(new_backup_dir, backup_method=BackupType.Complete)

        # For example: /tmp/2023-07-14-17-24-23
        assert new_backup_dir.startswith(str(tmp.parts[0]))
        assert rsync_cmd == [
            "rsync",
            *optionless_arguments,
            *(f"--exclude={p}" for p in exclude_file_patterns),
            home,
            f"{user_at_localhost}:{new_backup_dir}",
        ]


class TestPathOperations:
    def test_is_symlink(self, scratch_file_system, home_tmp_config):
        _, _, config = home_tmp_config
        assert config.is_symlink(scratch_file_system / "file1") is False
        assert config.is_symlink(scratch_file_system / "file3") is False
        assert config.is_symlink(scratch_file_system / "file3_symlink") is True
        assert config.is_symlink(scratch_file_system / "dir1") is False
        assert config.is_symlink(scratch_file_system / "dir3") is False
        assert config.is_symlink(scratch_file_system / "dir3_symlink") is True

    def test_file_exists(self, scratch_file_system, home_tmp_config):
        _, _, config = home_tmp_config
        assert config.file_exists(scratch_file_system / "file1") is True
        assert config.file_exists(scratch_file_system / "file2") is True
        assert config.file_exists(scratch_file_system / "file3") is True
        assert config.file_exists(scratch_file_system / "file3_symlink") is True
        assert config.file_exists(scratch_file_system / "dir1") is True
        assert config.file_exists(scratch_file_system / "dir2") is True
        assert config.file_exists(scratch_file_system / "dir3") is True
        assert config.file_exists(scratch_file_system / "dir3_symlink") is True
        assert config.file_exists(scratch_file_system / "dir1" / "file1") is True
        assert config.file_exists(scratch_file_system / "dir1" / "file2") is True
        assert config.file_exists(scratch_file_system / "foo") is False
        assert config.file_exists(scratch_file_system / "bar") is False
        assert config.file_exists(scratch_file_system / "dir1" / "foo") is False
        assert config.file_exists(scratch_file_system / "dir2" / "foo") is False

    def test_unlink(self, scratch_file_system, home_tmp_config):
        _, _, config = home_tmp_config

        assert (scratch_file_system / "file3_symlink").exists() is True
        config.unlink(scratch_file_system / "file3_symlink")
        assert (scratch_file_system / "file3_symlink").exists() is False

        assert (scratch_file_system / "file1").exists() is True
        config.unlink(scratch_file_system / "file1")
        assert (scratch_file_system / "file1").exists() is False

    def test_symlink_to(self, scratch_file_system, home_tmp_config):
        _, _, config = home_tmp_config

        assert (scratch_file_system / "file_symlink").exists() is False
        config.symlink_to(scratch_file_system / "file_symlink", scratch_file_system / "file1")
        assert (scratch_file_system / "file_symlink").exists() is True

        assert (scratch_file_system / "dir_symlink").exists() is False
        config.symlink_to(scratch_file_system / "dir_symlink", scratch_file_system / "dir1")
        assert (scratch_file_system / "dir_symlink").exists() is True

    def test_resolve(self, scratch_file_system, home_tmp_config):
        _, _, config = home_tmp_config
        fs = scratch_file_system
        assert config.resolve(fs / "file3_symlink") == str(fs / "file3")
        assert config.resolve(fs / "dir3_symlink") == str(fs / "dir3")

    def test_is_empty_directory(self, scratch_file_system, home_tmp_config):
        _, _, config = home_tmp_config
        fs = scratch_file_system
        assert (fs / "dir1").exists() is True
        assert (fs / "dir2").exists() is True
        assert config.is_empty_directory(fs / "dir1") is False
        assert config.is_empty_directory(fs / "dir2") is True

    def test_ensure_dir_exists(self, scratch_file_system, home_tmp_config):
        _, _, config = home_tmp_config
        fs = scratch_file_system

        # no exception thrown
        config.ensure_dir_exists(fs / "dir1")

        # not a dir
        assert (fs / "file1").exists()
        with pytest.raises(InvalidPathError):
            config.ensure_dir_exists(fs / "file1")

        # non existent
        with pytest.raises(InvalidPathError):
            config.ensure_dir_exists(fs / "dir")

    @pytest.mark.skip(reason="Time difference between the two statements sometimes causes fail")
    def test_generate_new_backup_dir_path(self, tmp_path, scratch_file_system, user_at_localhost):
        config = RemoteConfig(user_at_localhost, scratch_file_system, tmp_path)
        # these two lines should be run within one second of each other
        new_backup_dir = config.generate_new_backup_dir_path()
        time_stamp = get_time_stamp()
        assert new_backup_dir.split("/")[-1] == time_stamp

    def test_generate_new_backup_dir_throws_exception_on_overwrite(
        self, tmp_path, scratch_file_system, user_at_localhost
    ):
        config = RemoteConfig(user_at_localhost, scratch_file_system, tmp_path)
        time_stamp = get_time_stamp()
        (tmp_path / time_stamp).mkdir()

        with pytest.raises(InvalidPathError):
            _ = config.generate_new_backup_dir_path()
