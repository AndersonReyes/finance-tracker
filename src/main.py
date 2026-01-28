from nicegui import ui

from nav import nav
from pages import bills, budgets, expense_report, transactions


def root():
    ui.sub_pages(
        {
            "/": main,
            "/expense_report": expense_report.page,
            "/transactions": transactions.page,
            "/budgets": budgets.page,
            "/bills": bills.page,
        }
    ).classes("w-full")


def main():
    with ui.column():
        nav()


ui.run(root)
