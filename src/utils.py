from dataclasses import asdict
from datetime import datetime
from typing import Dict, Iterator, List, Tuple


def iterate_nodes(nodes: List[Dict]) -> Iterator[Dict]:
    for node in nodes:
        yield node
        yield from iterate_nodes(node.get("children", []))


def get_dates(str_range: str) -> Tuple[datetime, datetime]:
    if str_range:
        start, end = str_range.split(" - ")
        return (
            datetime.strptime(start, "%Y-%m-%d"),
            datetime.strptime(end, "%Y-%m-%d"),
        )
    return (datetime.min, datetime.min)


def dataclass_to_dict(d, **kwargs):
    return {**asdict(d), **kwargs}


class Javascript:
    currency_formatter = {
        ":valueFormatter": "(p) => '$' + p.value.toLocaleString('en-US')"
    }
