import io
from collections import namedtuple

import PySimpleGUI as sg
from PIL import Image
from fitz import open as pdf_open

from app.config import Config
from app.layout import Key
from app.elements import FilePicker, Converter, ProgressBar
from app.utils import get_file_info, FileInfo


class EventLoop:
    source_finfo: FileInfo = None
    target_finfo: FileInfo = None

    result: tuple[str, FileInfo] = namedtuple('EventLoopResult', ['event', 'finfo'])

    def run(self, window: sg.Window) -> result:
        file_source_picker = FilePicker(window, Key.FILE_SOURCE_INPUT, Key.FILE_SOURCE_BROWSE)
        converter = Converter(ProgressBar(window), window)

        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, Key.ACTIONS_CANCEL):
                break
            elif event in [file_source_picker.key, Key.FILE_TARGET_INPUT]:
                finfo = get_file_info(values[event])
                if event == file_source_picker.key and finfo != self.source_finfo:
                    self.source_finfo = finfo
                    if self.is_finfo_valid(self.source_finfo, Config.SOURCE_EXTENSIONS):
                        Key.PREVIEW_IMAGE.get_element(window).update(data=self.get_preview_image(finfo.ext))
                        target_filename = f'{finfo.filename}_ocr.pdf'
                        Key.FILE_TARGET_INPUT.get_element(window).update(disabled=False, value=target_filename)
                        self.target_finfo = get_file_info(target_filename)
                    else:
                        Key.FILE_TARGET_INPUT.get_element(window).update(disabled=True)
                        converter.disable()
                elif finfo != self.target_finfo:
                    self.target_finfo = finfo

                if self.is_finfo_valid(self.source_finfo, Config.SOURCE_EXTENSIONS) \
                        and self.is_finfo_valid(self.target_finfo, Config.TARGET_EXTENSIONS):
                    converter.enable()
                else:
                    converter.disable()
            elif event == converter.key:
                Key.FILE_TARGET_INPUT.get_element(window).update(disabled=True)
                EventLoop.disable(converter, file_source_picker)
                if not self.target_finfo.dir:
                    self.target_finfo.dir = self.source_finfo.dir
                converter.run(self.source_finfo.path, self.target_finfo.path)
                break

        return EventLoop.result(event, self.target_finfo)

    def get_preview_image(self, ext: str) -> bytes:
        if ext == '.pdf':
            doc = pdf_open(self.source_finfo.path)
            doc_png_data = doc[0].get_displaylist().get_pixmap(alpha=False).getPNGData()
            img = Image.open(io.BytesIO(doc_png_data))
        else:
            img = Image.open(self.source_finfo.path)

        with io.BytesIO() as bio:
            img = img.resize(Config.PREVIEW_RESOLUTION, Image.ANTIALIAS)
            img.save(bio, format='PNG')
            del img
            return bio.getvalue()

    @staticmethod
    def is_finfo_valid(finfo: FileInfo, ext: list[str]) -> bool:
        return finfo is not None and finfo.filename and finfo.ext in ext

    @staticmethod
    def disable(*args: any):
        [obj.disable() for obj in args if hasattr(obj, 'disable')]

    @staticmethod
    def enable(*args: any):
        [obj.enable() for obj in args if hasattr(obj, 'enable')]
