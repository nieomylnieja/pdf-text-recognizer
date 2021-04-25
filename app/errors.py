from contextlib import contextmanager

import PySimpleGUI as sg


@contextmanager
def handle_exceptions():
    try:
        yield
    except Exception as e:
        sg.popup_error(e, title='Error')
