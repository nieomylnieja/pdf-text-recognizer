import os
import io

import PySimpleGUI as sg
import pytesseract
from PySimpleGUI import Window, Element
from PyPDF2 import PdfFileMerger
from pdf2image import convert_from_path
from langdetect import detect
from PIL import Image

from app.layout import Key


class LayoutElement:

    def enable(self):
        self._update_disabled(False)

    def disable(self):
        self._update_disabled(True)

    def _update_disabled(self, disabled: bool):
        for v in self.__dict__.values():
            if isinstance(v, Element):
                v.update(disabled=disabled)

    def get_row(self):
        return [v for v in self.__dict__.values() if isinstance(v, Element)]


class ProgressBar(LayoutElement):
    _step = 0

    def __init__(self, window: sg.Window):
        self._frame = Key.PROGRESS_BAR_FRAME.get_element_safe(window, sg.Frame)
        self._textbox = Key.PROGRESS_BAR_TEXT.get_element_safe(window, sg.Text)
        self._progress_bar = Key.PROGRESS_BAR.get_element_safe(window, sg.ProgressBar)

    def get_row(self):
        return self._frame

    def set_max_step(self, max_step: int):
        self._progress_bar.update(0, max=max_step)

    def make_visible(self):
        self._frame.update(visible=True)

    def step_forward(self, msg: str):
        self._step += 1
        self._progress_bar.update(self._step)
        self._textbox.update(value=msg)


class Converter(LayoutElement):
    _merger = PdfFileMerger()

    def __init__(self, progress_bar: ProgressBar, window: sg.Window):
        self._progress_bar = progress_bar
        self._button = Key.ACTIONS_CONVERT.get_element_safe(window, sg.Button)
        self._language = None

    @property
    def key(self) -> str:
        return self._button.Key

    def get_button(self):
        return self._button

    def run(self, source: str, target: str):
        ext = os.path.splitext(os.path.basename(source))[1]
        if ext == '.pdf':
            images = convert_from_path(source, fmt='pdf')
        elif ext == '.jpg':
            images = [Image.open(source)]
        else:
            raise NotImplementedError(f'unsupported extension: {ext}')
        if len(images) == 0:
            return
        self._progress_bar.set_max_step(3 + len(images))
        self._progress_bar.make_visible()
        language = self._detect_language(images[0])
        if language not in pytesseract.get_languages():
            raise ModuleNotFoundError(
                f'{language} is not supported, consider installing additional tesseract train data')

        for i, image in enumerate(images):
            pdf = self._to_pdf(image, i, language)
            self._merger.append(io.BytesIO(pdf))

        self._write_result(target)

    def _extract_text_from_image(self, image: list):
        self._progress_bar.step_forward('extracting text data from image')
        return pytesseract.image_to_string(image)

    def _detect_language(self, image: list) -> str:
        text = self._extract_text_from_image(image)
        self._progress_bar.step_forward('detecting language')
        return detect(text)

    def _to_pdf(self, image: list, i: int, language: str):
        self._progress_bar.step_forward(f'converting page {i} to pdf')
        return pytesseract.image_to_pdf_or_hocr(image, lang=language, extension='pdf')

    def _write_result(self, target: str):
        self._progress_bar.step_forward('merging results into final pdf')
        self._merger.write(target)

    def __del__(self):
        self._merger.close()


class FilePicker(LayoutElement):

    def __init__(self, window: sg.Window, input_key: Key, button_key: Key):
        self._input = input_key.get_element_safe(window, sg.Input)
        self._button = button_key.get_element_safe(window, sg.Button)

    @property
    def key(self) -> str:
        return self._input.Key
