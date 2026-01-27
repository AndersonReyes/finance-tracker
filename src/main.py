from nicegui import ui

from config import PAGES
from nav import nav


def root():
    ui.sub_pages({"/": main, **PAGES}).classes("w-full")


def main():
    with ui.column():
        nav()


ui.run(root)
