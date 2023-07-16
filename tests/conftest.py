import pytest


@pytest.fixture
def optionless_arguments():
    return [
        "--delete",
        "--archive",
        # "--acls",
        # "--xattrs",
        "--verbose",
    ]


@pytest.fixture(scope="function")
def scratch_file_system(tmp_path):
    file1 = tmp_path / "file1"
    file2 = tmp_path / "file2"
    file3 = tmp_path / "file3"
    file3_symlink = tmp_path / "file3_symlink"
    dir1 = tmp_path / "dir1"
    dir2 = tmp_path / "dir2"
    dir3 = tmp_path / "dir3"
    dir3_symlink = tmp_path / "dir3_symlink"
    dir1_file1 = dir1 / "file1"
    dir1_file2 = dir1 / "file2"

    file1.touch()
    file2.touch()
    file3.touch()
    dir1.mkdir()
    dir2.mkdir()
    dir3.mkdir()
    file3_symlink.symlink_to(file3)
    dir3_symlink.symlink_to(dir3)
    dir1_file1.touch()
    dir1_file2.touch()

    return tmp_path
