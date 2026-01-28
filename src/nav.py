from nicegui import ui


def nav():
    ui.add_body_html("""
        <script>
        function currencyFormatter(v) {
            return '$' + v.value.toLocaleString("en-US")
        }
        </script>""")
    with ui.column(align_items="center").classes("w-full"):
        dark = ui.dark_mode(None)
        ui.switch("Dark mode").bind_value(dark)

        with ui.row(align_items="end"):
            ui.button("Back", on_click=ui.navigate.back)
            ui.button("Forward", on_click=ui.navigate.forward)

            ui.button(
                "Expense Reports",
                on_click=lambda: ui.navigate.to("/expense_report"),
            )

            ui.button(
                "Transactions",
                on_click=lambda: ui.navigate.to("/transactions"),
            )
            ui.button(
                "Budgets",
                on_click=lambda: ui.navigate.to("/budgets"),
            )
            ui.button(
                "Bills",
                on_click=lambda: ui.navigate.to("/bills"),
            )

    ui.separator().classes("w-full")
