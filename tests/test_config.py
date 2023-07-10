import unittest
from pathlib import Path
from rsync.config import LocalConfig, InvalidPath


OPTIONLESS_RSYNC_ARGUMENTS = [
    "--delete",
    "--archive",
    # "--acls",
    # "--xattrs",
    "--verbose",
]


class LocalConfigTests(unittest.TestCase):
    def test_init_valid_parameters(self):
        # arrange
        home = str(Path("~/").expanduser())
        tmp = "/tmp"

        # act
        config = LocalConfig(home, tmp)

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
            _ = LocalConfig(source, dest)

    def test_init_destination_does_not_exist(self):
        # arrange
        source = str(Path("~/").expanduser())
        dest = "/bad/directory/path/here/does/not/exist"

        # act + assert
        with self.assertRaises(InvalidPath):
            _ = LocalConfig(source, dest)

    def test_get_rsync_command_no_previous_backup(self):
        # arrange
        home = str(Path("~/").expanduser())
        tmp = "/tmp"
        config = LocalConfig(home, tmp)

        # act
        new_backup_dir = config.generate_new_backup_dir_path()
        cmd = config.get_rsync_command(
            new_backup_dir,
            previous_backup_exists=False
        )

        # assert
        self.assertEqual(cmd[0], "rsync")
        self.assertIn(home, cmd)
        self.assertIn(str(new_backup_dir), cmd)
        self.assertNotIn(f"--link-dest={tmp}/latest", cmd)
        for option in OPTIONLESS_RSYNC_ARGUMENTS:
            self.assertIn(option, cmd)
        self.assertEqual(len(cmd), len(OPTIONLESS_RSYNC_ARGUMENTS) + 3)

    def test_get_rsync_command_no_exclude_patterns(self):
        # arrange
        home = str(Path("~/").expanduser())
        tmp = "/tmp"
        config = LocalConfig(home, tmp)

        # act
        new_backup_dir = config.generate_new_backup_dir_path()
        cmd = config.get_rsync_command(
            new_backup_dir,
            previous_backup_exists=True
        )

        # assert
        self.assertEqual(cmd[0], "rsync")
        self.assertIn(home, cmd)
        self.assertIn(str(new_backup_dir), cmd)
        self.assertIn(f"--link-dest={tmp}/latest", cmd)
        for option in OPTIONLESS_RSYNC_ARGUMENTS:
            self.assertIn(option, cmd)
        self.assertEqual(len(cmd), len(OPTIONLESS_RSYNC_ARGUMENTS) + 4)

    def test_get_rsync_command_with_exclude_patters(self):
        # arrange
        home = str(Path("~/").expanduser())
        tmp = "/tmp"
        exclude_file_patterns = [
            "/exclude/path1",
            "/exclude/path2",
            "/exclude/path3/**/*.bak"
        ]
        config = LocalConfig(
            home,
            tmp,
            exclude_file_patterns
        )

        # act
        new_backup_dir = config.generate_new_backup_dir_path()
        cmd = config.get_rsync_command(
            new_backup_dir,
            previous_backup_exists=True
        )

        # assert
        self.assertEqual(cmd[0], "rsync")
        self.assertIn(home, cmd)
        self.assertIn(str(new_backup_dir), cmd)
        self.assertIn(f"--link-dest={tmp}/latest", cmd)
        for option in OPTIONLESS_RSYNC_ARGUMENTS:
            self.assertIn(option, cmd)

        self.assertEqual(len(cmd), len(OPTIONLESS_RSYNC_ARGUMENTS) + 4 + 3)
        for pattern in exclude_file_patterns:
            self.assertIn(f"--exclude={pattern}", cmd)
