import csv
import decimal
import io
from datetime import datetime
from typing import List

from nicegui import binding, ui
from nicegui.events import UploadEventArguments

from components.db import client, models
from components.money import rules
from nav import nav


@binding.bindable_dataclass
class _State:
    bank = ""


state = _State()

tables = [models.Transaction]
current_table = ""


colMaps = {
    "money-cli": {
        "Date": "date",
        "SourceAccount": "source_account_name",
        "Amount": "amount",
        "Description": "description",
        "Category": "category",
    }
}


def money_cli(data: List[dict]) -> List[models.Transaction]:
    trs = []
    for row in data:
        trs.append(
            models.Transaction(
                date=datetime.strptime(row["Date"], "%Y-%m-%d"),
                source_account_name=row["SourceAccount"],
                amount=row["Amount"],
                description=row["Description"],
                category=row["Category"],
            )
        )
    return trs


def process_discover_bank(acc_name: str, data: List[dict]) -> List[models.Transaction]:
    trs = []
    for row in data:
        if row["Transaction Type"] == "Credit":
            amount = decimal.Decimal.from_float(float(row["Credit"][1:]))
        else:
            amount = decimal.Decimal.from_float(-float(row["Debit"][1:]))

        trs.append(
            models.Transaction(
                date=datetime.strptime(row["Transaction Date"], "%m/%d/%Y"),
                source_account_name=acc_name,
                amount=amount,
                description=row["Transaction Description"],
                category=rules.get_category(row["Transaction Description"], ""),
            )
        )
    return trs


def process_capitalone_bank(
    acc_name: str, data: List[dict]
) -> List[models.Transaction]:
    trs = []
    for row in data:
        if row["Credit"] != "":
            amount = decimal.Decimal.from_float(float(row["Credit"]))
        else:
            amount = decimal.Decimal.from_float(-float(row["Debit"]))

        trs.append(
            models.Transaction(
                date=datetime.strptime(row["Transaction Date"], "%Y-%m-%d"),
                source_account_name=acc_name,
                amount=amount,
                description=row["Description"],
                category=row["Category"],
                tags=f"cardno-{row['Card No.']}",
            )
        )
    return trs


@ui.refreshable
async def transactions():
    trans = client.get_transactions(datetime.min, datetime.max)
    columns = [
        {"field": "id", "name": "id"},
        {"field": "date", "sortable": True},
        {"field": "category"},
        {"field": "description", "filter": "agTextColumnFilter"},
        {"field": "amount"},
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
            "pagination": True,
        }
    ).classes("w-full").style("height: 66.67vh")


async def insert_data(e: UploadEventArguments):
    if not state.bank:
        return

    buf = io.StringIO(await e.file.text())
    reader = csv.reader(buf)
    columns = next(reader)
    data = []
    for row in reader:
        if not row:
            continue

        datum = {}
        for i in range(len(columns)):
            v = row[i]
            datum[columns[i]] = v
        data.append(datum)

    if state.bank == "money-cli":
        trs = money_cli(data)
    elif state.bank.startswith("discover"):
        trs = process_discover_bank(state.bank, data)
    elif state.bank.startswith("capitalone"):
        trs = process_capitalone_bank(state.bank, data)
    else:
        print("no transactions processed")
        trs = []

    client.add_transactions(trs)
    transactions.refresh()
    print("processed file: ", e.file.name)
    ui.notify("processed file: " + e.file.name)


@ui.refreshable
def budget_editor():
    pass


async def page():
    nav()
    with ui.column(align_items="center").classes("w-full"):
        ui.markdown("## Import Transactions")

        with ui.row(align_items="center"):
            ui.select(
                # TODO: move this to db
                {
                    "discover-0075": "Discover Savings",
                    "discover-7150": "Discover Checkings",
                    "discover-5029": "Discover Kids Savings",
                    "capitalone-8444": "Capital One Credit Card",
                    "money-cli": "money cli",
                },
                label="select account",
            ).classes("w-96").bind_value(state, "bank")
            ui.upload(label="upload a csv", on_upload=insert_data).props("accept=.csv")

        ui.separator()

        ui.markdown("## Transaction History")
        await transactions()
