import PySimpleGUI as sg

from app.errors import handle_exceptions
from app.event_loop import EventLoop
from app.layout import Layout
from app.system import System


def main():
    from layout import Key

    System.validate()

    sg.theme('Dark Blue 2')

    window = sg.Window('Text recognizer', Layout.get())
    result = EventLoop().run(window)
    if result.event == Key.ACTIONS_CONVERT:
        System.open(result.finfo.filename)
    window.close()


if __name__ == '__main__':
    with handle_exceptions():
        main()
