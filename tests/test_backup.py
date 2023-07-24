import getpass
import os
import tempfile
import unittest
from pathlib import Path
from time import sleep
from unittest.mock import Mock, patch

import pytest

from pisync.config import LocalConfig, RemoteConfig
from pisync.util import BackupFailedError, backup, run_rsync


@pytest.fixture
def user_at_localhost() -> str:
    return f"{getpass.getuser()}@localhost"


class RunRsyncTests(unittest.TestCase):
    def test_fake_command_exit_zero(self):
        rsync_command = ["ls", "-al"]
        exit_code = run_rsync(rsync_command)
        self.assertEqual(exit_code, 0)

    def test_fake_command_exit_non_zero(self):
        rsync_command = ["ls", "-z"]  # there is no -z options for ls
        exit_code = run_rsync(rsync_command)
        self.assertNotEqual(exit_code, 0)


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.src_dir = tempfile.TemporaryDirectory()
        self.dest_dir = tempfile.TemporaryDirectory()
        self.config = LocalConfig(self.src_dir.name, self.dest_dir.name)
        self.src_dir_path = Path(self.src_dir.name)
        self.dest_dir_path = Path(self.dest_dir.name)

    def tearDown(self):
        self.src_dir.cleanup()
        self.dest_dir.cleanup()

    def test_five_backups_while_adding_files_each_time_successfully(self):
        for i in range(5):
            # arrange
            for j in range(i):
                curr_file_path = self.src_dir_path / f"test{j}.txt"
                curr_file_path.touch()

            # act
            latest_backup_path = backup(self.config)

            # assert
            files_in_source = list(self.src_dir_path.iterdir())
            self.assertEqual(len(files_in_source), i)
            for source_file in files_in_source:
                dest_file = self.dest_dir_path / latest_backup_path / source_file
                self.assertTrue(dest_file.exists())

            latest_link = self.dest_dir_path / "latest"
            self.assertTrue(latest_link.exists())
            self.assertTrue(latest_link.is_symlink())
            self.assertEqual(os.readlink(latest_link), latest_backup_path)
            sleep(1)  # next time stamp (in seconds) must be unique

    def test_backup_saves_accidental_file_deletion_situation(self):
        # arrange
        file_names = [f"test{i}.txt" for i in range(5)]
        for name in file_names:
            file = self.src_dir_path / name
            file.touch()

        # act
        first_backup_path = Path(backup(self.config))
        file_to_delete = self.src_dir_path / file_names[3]
        file_to_delete.unlink()
        sleep(1)  # cannot run two backups at same dest in same second
        second_backup_path = Path(backup(self.config))

        # assert
        files_in_source = list(self.src_dir_path.iterdir())
        files_in_first_backup = list((first_backup_path / self.src_dir_path.name).iterdir())
        files_in_second_backup = list((second_backup_path / self.src_dir_path.name).iterdir())

        self.assertEqual(len(files_in_source), 4)
        self.assertEqual(len(files_in_first_backup), 5)
        self.assertEqual(len(files_in_second_backup), 4)

        # first backup contains all five files
        for name in file_names:
            file = first_backup_path / self.src_dir_path.name / name
            self.assertTrue(file.exists())

        # file at index 3 (aka test3.txt) is not in source
        self.assertNotIn(self.src_dir_path / file_names[3], files_in_source)

        # file at index 3 (aka test3.txt) is not in latest backup
        self.assertNotIn(second_backup_path / self.src_dir_path.name / file_names[3], files_in_second_backup)


@patch("pisync.util.run_rsync", Mock(return_value=1))
def test_local_backup_rsync_fails_removes_previous_failed_backup(tmp_path):
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()

    config = LocalConfig(source_dir, dest_dir)
    config.rmtree = Mock()
    config.file_exists = Mock()
    config.unlink = Mock()
    config.file_exists.return_value = True

    with pytest.raises(BackupFailedError):
        backup(config)
        assert config.rmtree.called is True


@patch("pisync.util.run_rsync", Mock(return_value=1))
def test_remote_backup_rsync_fails_removes_previous_failed_backup(tmp_path, user_at_localhost):
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()

    config = RemoteConfig(user_at_localhost, source_dir, dest_dir)
    config.rmtree = Mock()
    config.file_exists = Mock()
    config.unlink = Mock()
    config.file_exists.return_value = True

    with pytest.raises(BackupFailedError):
        backup(config)
        assert config.rmtree.called is True
