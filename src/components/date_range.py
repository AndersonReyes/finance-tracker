from datetime import datetime, timedelta

from nicegui import ui


def _defaul_dates():
    end = datetime.today().replace(day=1) - timedelta(days=1)
    start = end.replace(day=1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def component():
    ffrom, to = _defaul_dates()

    date_input = ui.input("Date range", value=f"{ffrom} - {to}").classes("w-40")
    date_input.set_visibility(False)
    ui.date().props("range").bind_value(
        date_input,
        forward=lambda x: f"{x['from']} - {x['to']}" if x else None,
        backward=lambda x: (
            {
                "from": x.split(" - ")[0],
                "to": x.split(" - ")[1],
            }
            if " - " in (x or "")
            else None
        ),
    )

    return date_input
