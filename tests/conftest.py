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
