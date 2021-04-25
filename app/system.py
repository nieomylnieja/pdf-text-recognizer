import sys
import subprocess
from dataclasses import dataclass
from shutil import which


@dataclass(frozen=True)
class System:
    _supported_platforms = ['darwin', 'linux']

    @staticmethod
    def validate():
        if sys.platform not in System._supported_platforms:
            raise SystemError(f'unsupported platform, this program may only run on {System._supported_platforms}')
        if which('tesseract') is None:
            raise SystemError('tesseract was not found')

    @staticmethod
    def open(filename: str):
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])
