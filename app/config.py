from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    PREVIEW_RESOLUTION: tuple[int, int] = (500, 500)
    SOURCE_EXTENSIONS: list[str] = ('.pdf', '.jpg')
    TARGET_EXTENSIONS: list[str] = '.pdf'
