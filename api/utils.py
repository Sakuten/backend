import hashlib
import os
__docs__ = """collection of small utilities"""


def calc_sha256(_file: str) -> str:
    """calculate sha256 hash of given file
        Args:
            _file (str): file path
    """
    if not os.path.isfile(_file):
        raise FileNotFoundError

    with open(_file, 'r') as f:
        return hashlib.sha256(f.read().encode()).hexdigest()
