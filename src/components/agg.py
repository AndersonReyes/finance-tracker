import decimal
from typing import Dict, Sequence

from components.db.models import Bill, BillCharged, Transaction


def agg_amount_by_bill(
    bills: Sequence[Bill], trans: Sequence[Transaction]
) -> Sequence[BillCharged]:
    agg: Dict[int, decimal.Decimal] = {}

    for t in trans:
        agg[t.bill_id] = agg.get(t.bill_id, decimal.Decimal("0")) + t.amount

    return [
        BillCharged(
            name=bill.name,
            expected_amount=bill.expected_amount,
            charged=agg.get(bill.id, decimal.Decimal("0")),
        )
        for bill in bills
    ]
