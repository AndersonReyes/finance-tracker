import decimal
from dataclasses import field

from nicegui import ui
from nicegui.events import GenericEventArguments

from components.db import client, models
from nav import nav


@ui.refreshable
def list_bills():
    bills = [
        {
            "id": b.id,
            "name": b.name,
            "expected_amount": b.expected_amount,
            "matcher": b.regex_str,
        }
        for b in client.get_bills()
    ]
    columns = [
        {"field": "id", "editable": False, "sortable": True},
        {"field": "name", "editable": True, "sortable": True},
        {
            "field": "expected_amount",
            "editable": True,
            # currencyFormatter defined in nav.py
            ":valueFormatter": "currencyFormatter",
        },
        {"field": "matcher", "editable": True},
    ]

    with ui.row(align_items="center").classes("w-full"):
        ui.button("Add Row", color="primary", on_click=lambda: row_add())
        ui.button(
            "Match bill to transactions",
            color="green",
            on_click=lambda x: match_bills(table),
        )

    table = (
        ui.aggrid(
            {
                "columnDefs": columns,
                "rowData": bills,
                "stopEditingWhenCellsLoseFocus": True,
                "pagination": True,
                "paginationPageSize": 20,
                "rowSelection": {"mode": "multiRow"},
                "grandTotalRow": "top",
            }
        )
        .classes("w-full")
        .style("height: 66.67vh")
    )
    table = table.on("cellValueChanged", lambda x: row_edit(x))
    ui.button(
        "Delete selected", color="red", on_click=lambda: delete_selected(table)
    ).classes("flex-end")


async def match_bills(table: ui.aggrid):
    bills = [
        models.Bill(
            id=row["id"],
            name=row["name"],
            regex_str=row["matcher"],
            expected_amount=row["expected_amount"],
        )
        for row in await table.get_selected_rows()
    ]
    matched = client.match_bills_to_transactions(bills)
    ui.notify(f"matched {matched} transactons")


def row_add():
    client.add_bills(
        [
            models.Bill(
                name="New BILL: Edit ME",
                regex_str="",
                expected_amount=decimal.Decimal("0"),
            )
        ]
    )
    ui.notify("row added")


def row_edit(e: GenericEventArguments):
    row = e.args["data"]
    client.update_bills(
        [
            dict(
                id=row["id"],
                name=row["name"],
                expected_amount=row["expected_amount"],
                regex_str=row["matcher"],
            )
        ]
    )


async def delete_selected(table: ui.aggrid):
    selected_ids = [row["id"] for row in await table.get_selected_rows()]
    client.delete_bill_by_id(selected_ids)
    list_bills.refresh()
    ui.notify("row deleted")


def summary():
    bills = client.get_bills()
    monthly_costs = sum([b.expected_amount for b in bills])
    ui.markdown(f"""
    # Summary
    number of bills: {len(bills)} <br>
    monthly costs: ${monthly_costs:,.2f}
    """)


def page():
    nav()

    with ui.column(align_items="center").classes("w-full"):
        summary()
        list_bills()
