from dataclasses import field
from typing import Sequence

from nicegui import binding, ui

import utils
from components import agg, date_range
from components.db import client, models
from nav import nav


@binding.bindable_dataclass
class _State:
    file = ""
    data: Sequence[models.CategoryExpense] = field(default_factory=list)
    budget_chart: dict = field(default_factory=dict)
    dates = ""
    bills: Sequence[models.Bill] = field(default_factory=list)
    transactions: Sequence[models.Transaction] = field(default_factory=list)


state = _State()


# @ui.refreshable
# def category_table():
#     data = [
#         utils.dataclass_to_dict(
#             v,
#         )
#         for v in state.data
#     ]
#     table = ui.table(rows=data, pagination=50).classes("w-full")
#     with table.add_slot("body-cell-spent"):
#         with table.cell("spent"):
#             ui.badge().props(
#                 """
#                 :color="((props.row.spent < -props.row.budget) && props.row.budget > 0) ? 'red' : 'green'"
#                 :label="props.value"
#             """
#             )


@ui.refreshable
def category_chart():
    budget_chart = {
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
    ui.echart(budget_chart).classes("w-full h-128")


@ui.refreshable
def bills_chart():
    aggregated = agg.agg_amount_by_bill(state.bills, state.transactions)
    chart = {
        "xAxis": {
            "type": "category",
            "axisLabel": {
                "rotate": 90,
            },
            "data": [v.name for v in aggregated],
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "type": "bar",
                "name": "expected_amount",
                "emphasis": {"focus": "self"},
                "label": {
                    "show": False,
                    "rotate": 90,
                    "position": "insideBottom",
                    "distance": 35,
                    "align": "left",
                    "verticalAlign": "middle",
                },
                "data": [v.expected_amount for v in aggregated],
            },
            {
                "type": "bar",
                "name": "charged",
                "emphasis": {"focus": "self"},
                "label": {
                    "show": False,
                    "rotate": 90,
                    "position": "insideBottom",
                    "distance": 35,
                    "align": "left",
                    "verticalAlign": "middle",
                },
                "data": [abs(v.actual_amount) for v in aggregated],
            },
        ],
        "legend": {"data": ["Expected", "Charged"]},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
    }
    ui.echart(chart).classes("w-full h-128")


def load_data():
    start, end = utils.get_dates(state.dates)
    state.data = client.get_category_expenses(start, end)
    state.bills = client.get_bills()
    state.transactions = client.get_transactions(start, end)

    category_chart.refresh()
    # category_table.refresh()
    bills_chart.refresh()


def page():
    nav()

    with ui.column(align_items="center").classes("w-full"):
        with ui.row():
            date_input = date_range.component()
            date_input.bind_value_to(state, "dates")
            date_input.on_value_change(lambda x: load_data())
            load_data()

        ui.markdown("## Category: budget vs expense")
        category_chart()
        ui.separator()

        ui.markdown("## Bills: expected vs actual")
        bills_chart()
        # category_table()
