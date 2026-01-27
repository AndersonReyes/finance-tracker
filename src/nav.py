from nicegui import ui


def nav():
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
                "import transactions",
                on_click=lambda: ui.navigate.to("/import"),
            )
            ui.button(
                "Budgets",
                on_click=lambda: ui.navigate.to("/budgets"),
            )

    ui.separator().classes("w-full")
