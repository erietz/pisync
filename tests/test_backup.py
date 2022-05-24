import unittest
from unittest.main import main
from backup import backup, get_time_stamp, run_rsync
from config import Config, InvalidPath
from pathlib import Path


class ConfigTests(unittest.TestCase):
    def test_init_valid_parameters(self):
        # arrange
        home = str(Path("~/").expanduser())
        tmp = "/tmp"

        # act
        config = Config(home, tmp)

        # assert
        self.assertEqual(str(config.source_dir), home)
        self.assertEqual(str(config.destination_dir), tmp)
        self.assertEqual(str(config.link_dir), tmp + "/" + "latest")

    def test_init_source_does_not_exist(self):
        # arrange
        source = "/bad/directory/path/here/does/not/exist"
        dest = "/tmp"

        # act + assert
        with self.assertRaises(InvalidPath):
            config = Config(source, dest)

    def test_init_destination_does_not_exist(self):
        # arrange
        source = str(Path("~/").expanduser())
        dest = "/bad/directory/path/here/does/not/exist"

        # act + assert
        with self.assertRaises(InvalidPath):
            _ = Config(source, dest)

    def test_get_rsync_command_no_exclude_patterns(self):
        # arrange
        home = str(Path("~/").expanduser())
        tmp = "/tmp"
        config = Config(home, tmp)
        time_stamp = get_time_stamp()

        # act
        cmd = config.get_rsync_command(time_stamp)

        # assert
        self.assertEqual(cmd[0], "rsync")
        self.assertIn(home, cmd)
        self.assertIn(f"{tmp}/{time_stamp}", cmd)
        self.assertIn(f"--link-dest={tmp}/latest", cmd)
        optionless_rsync_arguments = [
            "--delete",
            "--archive",
            "--acls",
            "--xattrs",
            "--verbose",
        ]
        for option in optionless_rsync_arguments:
            self.assertIn(option, cmd)
        self.assertEqual(len(cmd), len(optionless_rsync_arguments) + 4)

    def test_get_rsync_command_with_exclude_patters(self):
        # arrange
        home = str(Path("~/").expanduser())
        tmp = "/tmp"
        exclude_file_patterns = [
            "/exclude/path1",
            "/exclude/path2",
            "/exclude/path3/**/*.bak"
        ]
        config = Config(
            home,
            tmp,
            exclude_file_patterns
        )
        time_stamp = get_time_stamp()

        # act
        cmd = config.get_rsync_command(time_stamp)

        # assert
        self.assertEqual(cmd[0], "rsync")
        self.assertIn(home, cmd)
        self.assertIn(f"{tmp}/{time_stamp}", cmd)
        self.assertIn(f"--link-dest={tmp}/latest", cmd)
        optionless_rsync_arguments = [
            "--delete",
            "--archive",
            "--acls",
            "--xattrs",
            "--verbose",
        ]
        for option in optionless_rsync_arguments:
            self.assertIn(option, cmd)

        self.assertEqual(len(cmd), len(optionless_rsync_arguments) + 4 + 3)
        for pattern in exclude_file_patterns:
            self.assertIn(f"--exclude={pattern}", cmd)


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
    pass


if __name__ == '__main__':
    unittest.main(verbosity=3)
