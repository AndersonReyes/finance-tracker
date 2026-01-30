import alembic.config
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


def run_migrations():
    print("running migrations:\n")
    alembic.config.main(argv=["upgrade", "head"])
    print("migrations done\n")


if __name__ in {"__main__", "__mp_main__"}:
    run_migrations()
    ui.run(root)
