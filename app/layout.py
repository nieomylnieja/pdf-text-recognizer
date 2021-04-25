from dataclasses import dataclass
from pathlib import Path
from enum import auto, Enum
from typing import TypeVar, Type

import PySimpleGUI as sg

from app.config import Config


class Key(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return f'-{name}-'

    FILE_SOURCE_TEXT = auto()
    FILE_SOURCE_INPUT = auto()
    FILE_SOURCE_BROWSE = auto()
    FILE_TARGET_TEXT = auto()
    FILE_TARGET_INPUT = auto()
    PROGRESS_BAR_FRAME = auto()
    PROGRESS_BAR_TEXT = auto()
    PROGRESS_BAR = auto()
    ACTIONS_CONVERT = auto()
    ACTIONS_CANCEL = auto()
    PREVIEW_FRAME = auto()
    PREVIEW_IMAGE = auto()

    T = TypeVar('T', sg.Frame, sg.Button, sg.ProgressBar, sg.Image, sg.Input, sg.Text)

    def get_element_safe(key, w: sg.Window, t: Type[T]) -> T:
        element = w[key]
        if not isinstance(element, t):
            raise TypeError(f'Element type: {type(element)} does not match {t}')
        return element

    def get_element(key, w: sg.Window) -> sg.Element:
        return w[key]


@dataclass(frozen=True)
class Layout:

    @staticmethod
    def get() -> list:
        default_dir = str(Path.home()) + '/myProjects/pdf-text-recognizer'

        file_source_text = [sg.Text('Pick a file for recognition', key=Key.FILE_SOURCE_TEXT)]
        file_source_row = [
            sg.Input(
                key=Key.FILE_SOURCE_INPUT,
                default_text=default_dir,
                enable_events=True),
            sg.FileBrowse(
                key=Key.FILE_SOURCE_BROWSE,
                file_types=(('pdf', '*.pdf'), ('jpg', '*.jpg')),
                initial_folder=default_dir),
        ]
        file_target_text = [sg.Text('Save as', key=Key.FILE_TARGET_TEXT)]
        file_target_row = [
            sg.Input(
                key=Key.FILE_TARGET_INPUT,
                enable_events=True,
                disabled=True),
        ]
        progress_bar_row = [
            sg.Frame(key=Key.PROGRESS_BAR_FRAME, title='Conversion progress', visible=False,
                     layout=[[sg.ProgressBar(0, key=Key.PROGRESS_BAR, orientation='h', size=(35, 10))],
                             [sg.Text(key=Key.PROGRESS_BAR_TEXT, size=(35, 1))]])
        ]
        actions_row = [
            sg.Button(key=Key.ACTIONS_CONVERT, disabled=True, button_text='Convert'),
            sg.Cancel(key=Key.ACTIONS_CANCEL)
        ]
        preview_row = [
            sg.Frame(key=Key.PREVIEW_FRAME, title='Preview', pad=(0, 20), size=Config.PREVIEW_RESOLUTION,
                     layout=[[sg.Image(key=Key.PREVIEW_IMAGE, size=Config.PREVIEW_RESOLUTION)]])
        ]

        layout = [
            file_source_text,
            file_source_row,
            file_target_text,
            file_target_row,
            progress_bar_row,
            actions_row,
            preview_row
        ]

        Layout._verify_keys(layout)

        return layout

    @staticmethod
    def _verify_keys(layout: list):
        keys: set[Key] = set()
        for element in layout:
            if isinstance(element, list):
                Layout._verify_keys(element)
            if isinstance(element, sg.Element):
                if not isinstance(element.Key, Key):
                    raise TypeError(f'invalid type for element.Key: {type(element.Key)}')
                if element.Key.value in keys:
                    raise KeyError(f'{element.Key} can only be used on one element, but was also set for {element}')
                keys.add(element.Key.value)
                return
            else:
                return

        key_cls_values = [e.value for e in Key if isinstance(e.value, str)]
        for v in key_cls_values:
            if v not in keys:
                raise NotImplementedError(f'{v} key was not used, remove it or use it')
