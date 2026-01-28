from dataclasses import field
from typing import Sequence

from nicegui import binding, ui

import utils
from components import date_range
from components.db import client, models
from nav import nav


@binding.bindable_dataclass
class _State:
    file = ""
    data: Sequence[models.CategoryExpense] = field(default_factory=list)
    budget_chart: dict = field(default_factory=dict)
    dates = ""


state = _State()


@ui.refreshable
def category_table():
    data = [
        utils.dataclass_to_dict(
            v,
        )
        for v in state.data
    ]
    table = ui.table(rows=data, pagination=50).classes("w-full")
    with table.add_slot("body-cell-spent"):
        with table.cell("spent"):
            ui.badge().props(
                """
                :color="((props.row.spent < -props.row.budget) && props.row.budget > 0) ? 'red' : 'green'"
                :label="props.value"
            """
            )


@ui.refreshable
def category_chart():
    chart = ui.echart(state.budget_chart).classes("w-full h-128")
    state.budget_chart = {
        "xAxis": {
            "type": "category",
            "axisLabel": {
                "rotate": 90,
            },
            "data": [v.category for v in state.data],
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "type": "bar",
                "name": "Spent",
                "emphasis": {"focus": "self"},
                "label": {
                    "show": False,
                    "rotate": 90,
                    "position": "insideBottom",
                    "distance": 35,
                    "align": "left",
                    "verticalAlign": "middle",
                },
                "data": [v.spent for v in state.data],
            },
            {
                "type": "bar",
                "name": "Budget",
                "emphasis": {"focus": "self"},
                "label": {
                    "show": False,
                    "rotate": 90,
                    "position": "insideBottom",
                    "distance": 35,
                    "align": "left",
                    "verticalAlign": "middle",
                },
                "data": [v.budget for v in state.data],
            },
        ],
        "legend": {"data": ["Spent", "Budget"]},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
    }

    chart.options.update(state.budget_chart)


def load_data():
    start, end = utils.get_dates(state.dates)
    state.data = client.get_category_expenses(start, end)

    category_chart.refresh()
    category_table.refresh()


def page():
    nav()

    with ui.column(align_items="center").classes("w-full"):
        with ui.row():
            date_input = date_range.component()
            date_input.bind_value_to(state, "dates")
            date_input.on_value_change(lambda x: load_data())

        category_chart()
        ui.separator()
        ui.markdown("## Categories")
        category_table()
