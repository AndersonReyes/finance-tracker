import os
from glob import glob
from pathlib import Path
from typing import List

from nicegui import ui
from nicegui.events import ValueChangeEventArguments


class _State:
    def __init__(self, curr_item: Path = Path(os.getcwd())) -> None:
        self.curr_item = curr_item
        self.editor_value = ""


def _get_children(d: Path) -> List[Path]:
    children = []
    if d.is_dir():
        for c in glob(os.path.join(d, "*")):
            path = Path(os.path.join(d, c))
            children.append(path)
    return children


def _update_selection(grid: ui.aggrid, state: _State, path: Path):
    state.curr_item = path
    if path.is_dir():
        grid.options["rowData"] = [
            {
                "name": f"📁 <strong>{p.name}</strong>" if p.is_dir() else p.name,
                "path": str(p),
            }
            for p in _get_children(path)
        ]
        grid.update()
    else:
        # populate file contents
        with open(path) as f:
            state.editor_value = f.read()


def _save_contents(state: _State, e: ValueChangeEventArguments):
    if state.curr_item.is_file():
        with open(state.curr_item, "w") as f:
            f.write(state.editor_value)


def component():
    state = _State()

    with ui.grid(columns=2):
        with ui.column():
            grid = ui.aggrid(
                {
                    "columnDefs": [{"field": "name", "headerName": "File"}],
                    "rowSelection": {"mode": "multiRow"},
                },
                html_columns=[0],
            ).classes("w-96")

            grid.on(
                "cellClicked",
                lambda e: _update_selection(grid, state, Path(e.args["data"]["path"])),
            )
            _update_selection(grid, state, state.curr_item)
            ui.button(
                "back",
                on_click=lambda e: _update_selection(
                    grid, state, state.curr_item.parent
                ),
            )

        with ui.row(align_items="center"):
            editor = ui.editor(
                placeholder="select a file",
                on_change=lambda e: _save_contents(state, e),
            ).bind_value(state, "editor_value")
            ui.markdown().bind_content_from(editor, "value")
