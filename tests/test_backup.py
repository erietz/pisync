from time import sleep
import unittest
import tempfile
from pathlib import Path

from rsync.backup import backup, run_rsync, directory_is_empty
from rsync.config import Config


class UtilityFunctionTests(unittest.TestCase):
    def test_directory_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            self.assertTrue(directory_is_empty(tmp_dir))

            new_file = tmp_dir / "new-file-name-here.txt"
            new_file.touch()
            self.assertFalse(directory_is_empty(tmp_dir))


class RunRsyncTests(unittest.TestCase):
    def test_fake_command_exit_zero(self):
        rsync_command = ["ls", "-al"]
        exit_code = run_rsync(rsync_command)
        self.assertEqual(exit_code, 0)

    def test_fake_command_exit_non_zero(self):
        rsync_command = ["ls", "-z"]    # there is no -z options for ls
        exit_code = run_rsync(rsync_command)
        self.assertNotEqual(exit_code, 0)


class BackupTests(unittest.TestCase):
    def test_five_backups_while_adding_files_each_time_successfully(self):
        source_dir = tempfile.TemporaryDirectory()
        destination_dir = tempfile.TemporaryDirectory()
        config = Config(source_dir.name, destination_dir.name)
        source_dir_path = Path(source_dir.name)
        dest_dir_path = Path(destination_dir.name)

        for i in range(5):
            # arrange
            for j in range(i):
                curr_file_path = source_dir_path / f"test{j}.txt"
                curr_file_path.touch()

            # act
            latest_backup_path = backup(config)

            # assert
            files_in_source = list(source_dir_path.iterdir())
            self.assertEqual(len(files_in_source), i)
            for source_file in files_in_source:
                dest_file = dest_dir_path / latest_backup_path / source_file
                self.assertTrue(dest_file.exists())

            latest_link = dest_dir_path / "latest"
            self.assertTrue(latest_link.exists())
            self.assertTrue(latest_link.is_symlink())
            self.assertEqual(latest_link.readlink(), latest_backup_path)

            sleep(1)    # next time stamp (in seconds) must be unique

        # Remove all files and directories generated
        source_dir.cleanup()
        destination_dir.cleanup()

    def test_latest_backup_contains_files_deleted_accidentally(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=3)
