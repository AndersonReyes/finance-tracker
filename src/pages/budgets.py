import decimal

from nicegui import binding, ui
from nicegui.events import GenericEventArguments

from components.db import client, models
from nav import nav


@binding.bindable_dataclass
class _State:
    pass


def add_row_edit(e: GenericEventArguments):
    row = e.args["data"]
    client.update_budgets(
        [dict(id=row["id"], budget=row["budget"], category=row["category"])]
    )
    list_budgets.refresh()
    ui.notify("row updated")


async def delete_selected(table: ui.aggrid):
    selected_ids = [row["id"] for row in await table.get_selected_rows()]
    client.delete_budget_by_id(selected_ids)
    list_budgets.refresh()
    ui.notify("row deleted")


@ui.refreshable
def list_budgets():
    budgets = [
        {
            "id": b.id,
            "category": b.category,
            "budget": b.budget,
        }
        for b in client.get_budgets()
    ]
    columns = [
        {"field": "id", "editable": False, "sortable": True},
        {"field": "category", "editable": True, "sortable": True},
        {"field": "budget", "editable": True, "sortable": True},
    ]
    table = (
        ui.aggrid(
            {
                "columnDefs": columns,
                "rowData": budgets,
                "stopEditingWhenCellsLoseFocus": True,
                "pagination": True,
                "rowSelection": {"mode": "multiRow"},
            }
        )
        .classes("w-full")
        .style("height: 66.67vh")
    )
    table = table.on("cellValueChanged", lambda x: add_row_edit(x))
    ui.button("Delete selected", color="red", on_click=lambda: delete_selected(table))


def discover_from_db():
    cats = client.get_categories()
    cats = [models.Budget(category=c, budget=decimal.Decimal("0")) for c in cats]
    existing = {b.category for b in client.get_budgets()}

    to_add = [b for b in cats if b.category not in existing]
    client.add_budgets(to_add)

    list_budgets.refresh()


def page():
    nav()

    with ui.column(align_items="center").classes("w-full"):
        with ui.row(align_items="center").classes("w-full"):
            ui.button("Discover from DB", on_click=lambda x: discover_from_db())
        list_budgets()
