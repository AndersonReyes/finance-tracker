import decimal

from nicegui import binding, ui
from nicegui.events import GenericEventArguments

from components.db import client, models
from nav import nav


@binding.bindable_dataclass
class _State:
    pass


def row_add():
    client.add_bills(
        [
            models.Bill(
                name="New BILL: Edit ME",
                spent=decimal.Decimal("0"),
                regex_str="",
                expected_amount=decimal.Decimal("0"),
            )
        ]
    )
    list_bills.refresh()
    ui.notify("row added")


def row_edit(e: GenericEventArguments):
    row = e.args["data"]
    client.update_bills(
        [
            dict(
                id=row["id"],
                name=row["name"],
                expected_amount=row["expected_amount"],
                regex_str=row["regex_str"],
            )
        ]
    )
    list_bills.refresh()
    ui.notify("row updated")


async def delete_selected(table: ui.aggrid):
    selected_ids = [row["id"] for row in await table.get_selected_rows()]
    client.delete_bill_by_id(selected_ids)
    list_bills.refresh()
    ui.notify("row deleted")


@ui.refreshable
def list_bills():
    bills = [
        {
            "id": b.id,
            "name": b.name,
            "expected_amount": b.expected_amount,
            "regex_str": b.regex_str,
            "spent": b.spent,
        }
        for b in client.get_bills()
    ]
    columns = [
        {"field": "id", "editable": False, "sortable": True},
        {"field": "name", "editable": True, "sortable": True},
        {"field": "expected_amount", "editable": True, "sortable": True},
        {"field": "regex_str", "editable": True, "sortable": True},
    ]

    ui.button("Add Row", color="primary", on_click=lambda: row_add())
    table = (
        ui.aggrid(
            {
                "columnDefs": columns,
                "rowData": bills,
                "stopEditingWhenCellsLoseFocus": True,
                "pagination": True,
                "rowSelection": {"mode": "multiRow"},
            }
        )
        .classes("w-full")
        .style("height: 66.67vh")
    )
    table = table.on("cellValueChanged", lambda x: row_edit(x))
    ui.button("Delete selected", color="red", on_click=lambda: delete_selected(table))


def page():
    nav()

    with ui.column(align_items="center").classes("w-full"):
        list_bills()
