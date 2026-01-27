from nicegui import ui

import config


def nav():
    with ui.column(align_items="center").classes("w-full"):
        dark = ui.dark_mode(None)
        ui.switch("Dark mode").bind_value(dark)

        with ui.row(align_items="end"):
            ui.button("Back", on_click=ui.navigate.back)
            ui.button("Forward", on_click=ui.navigate.forward)

            for uri in config.PAGES:
                name = uri.replace("_", " ").replace("/", "").capitalize()
                ui.button(
                    name,
                    on_click=lambda: ui.navigate.to(uri),
                )
            # ui.button(
            #     "import transactions",
            #     on_click=lambda: ui.navigate.to("/import"),
            # )
            # ui.button(
            #     "Budgets",
            #     on_click=lambda: ui.navigate.to("/budgets"),
            # )

    ui.separator().classes("w-full")
