from dataclasses import dataclass
from os import path


def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


@dataclass
class FileInfo:
    dir: str
    filename: str
    ext: str

    @property
    def path(self):
        return f'{self.dir}/{self.filename}{self.ext}'


def get_file_info(filepath: str) -> FileInfo:
    return FileInfo(path.dirname(filepath), *path.splitext(path.basename(filepath)))
