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
    dates = ""
    data: Sequence[models.CategoryExpense] = field(default_factory=list)
    budget_chart: dict = field(default_factory=dict)
    # dates = ""
    bills: Sequence[models.Bill] = field(default_factory=list)
    transactions: Sequence[models.Transaction] = field(default_factory=list)
    filters: dict = field(default_factory=dict)


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
                "name": "Net",
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
        "legend": {"data": ["Net", "Budget"]},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
    }
    ui.echart(budget_chart).classes("w-full h-128")


@ui.refreshable
def bills_chart():
    aggregated = agg.agg_amount_by_bill(state.bills, state.transactions)
    total_actual = sum((a.actual_amount for a in aggregated))
    total_expected = sum((a.expected_amount for a in aggregated))
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
    ui.markdown(f"""## Bills: expected vs actual
total expected: ${total_expected:,.2f},  total actual: ${total_actual:,.2f}
""")
    chart = ui.echart(chart).classes("w-full h-128").on_click(lambda x: print(x))


@ui.refreshable
def transactions():
    start, end = utils.get_dates(state.dates)
    trans = client.get_transactions(start, end)
    columns = [
        {"field": "id", "name": "id"},
        {"field": "date", "sortable": True, "filter": "agTextColumnFilter"},
        {"field": "category", "filter": "agTextColumnFilter"},
        {"field": "description", "filter": "agTextColumnFilter"},
        {
            "field": "amount",
            **utils.Javascript.currency_formatter,
        },
        {"field": "source_account_name", "filter": "agTextColumnFilter"},
        {"field": "bill", "filter": "agTextColumnFilter"},
    ]
    rows = []
    for t in trans:
        bill = t.bill
        if bill:
            bill = bill.name
        rows.append(
            {
                "id": t.id,
                "date": t.date,
                "category": t.category,
                "description": t.description,
                "source_account_name": t.source_account_name,
                "amount": t.amount,
                "bill": bill,
            }
        )
        # rows.append({c: getattr(t, c["field"]) for c in columns})

    ui.aggrid(
        {
            "columnDefs": columns,
            "rowData": rows,
            "paginationPageSize": 20,
            "pagination": True,
        }
    ).classes("w-full").style("height: 66.67vh")


def load_data(dates: str):
    start, end = utils.get_dates(dates)
    state.data = client.get_category_expenses(start, end)
    state.bills = client.get_bills()
    state.transactions = client.get_transactions(start, end)

    category_chart.refresh()
    # category_table.refresh()
    bills_chart.refresh()


async def page():
    nav()

    with ui.column(align_items="center").classes("w-full"):
        with ui.row():
            date_input = date_range.component()
            date_input.bind_value_to(state, "dates")
            date_input.on_value_change(lambda x: load_data(x.value))
            load_data(date_input.value)

        ui.markdown("## Category: budget vs expense")
        category_chart()
        ui.separator()

        bills_chart()
        ui.separator()
        # category_table()

        ui.markdown("## Transactions")
        transactions()
