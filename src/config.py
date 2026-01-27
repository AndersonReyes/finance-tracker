from pages import budgets, expense_report, import_transactions

PAGES = {
    "/expense_report": expense_report.page,
    "/import_transactions": import_transactions.page,
    "/budgets": budgets.page,
}
