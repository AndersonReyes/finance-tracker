import decimal
from datetime import datetime, timedelta
from typing import List, Sequence

from sqlalchemy import and_, create_engine, delete, func, or_, select, update
from sqlalchemy.orm import Session, joinedload

from components.db.models import (
    Base,
    Bill,
    BillCharged,
    Budget,
    CategoryExpense,
    Transaction,
)

_engine = create_engine("sqlite:///db.sqlite", echo=False)

Base.metadata.create_all(_engine)

# with Session(_engine) as s:
#     tr = s.scalars(select(Transaction)).all()
#     for t in tr:
#         s.delete(t)
#     s.commit()


def add_transactions(trans: List[Transaction]):
    with Session(_engine) as s:
        s.add_all(trans)
        s.commit()


def _get_exclusive_end_date(d: datetime) -> datetime:
    """Returns the date with a +  1 day offset. This is to handle time filters
    based on exclusive ends rather than inclusive"""
    if d == datetime.max or d == datetime.min:
        return d
    return d + timedelta(days=1)


def get_transactions(start: datetime, end: datetime) -> Sequence[Transaction]:
    with Session(_engine) as s:
        stmt = (
            select(Transaction)
            .options(joinedload(Transaction.bill))
            .where(
                and_(
                    Transaction.date >= start,
                    Transaction.date < _get_exclusive_end_date(end),
                )
            )
            .order_by(Transaction.date.desc())
        )
        return s.scalars(stmt).all()


def get_category_expenses(start: datetime, end: datetime) -> Sequence[CategoryExpense]:
    with Session(_engine) as s:
        agg = (
            select(Transaction.category, func.sum(Transaction.amount).label("spent"))
            .where(
                and_(
                    Transaction.date >= start,
                    Transaction.date < _get_exclusive_end_date(end),
                )
            )
            .group_by(Transaction.category)
            .order_by(Transaction.category)
            .subquery()
        )
        budgets = (
            select(Budget.category, agg.c.spent, Budget.budget)
            .join(agg, Budget.category == agg.c.category, isouter=True)
            .subquery()
        )

        stmt = select(
            agg.c.category,
            agg.c.spent,
            func.coalesce(budgets.c.budget, decimal.Decimal.from_float(0.0)),
        ).join(budgets, agg.c.category == budgets.c.category, isouter=True)

        return [
            CategoryExpense(category=v[0], spent=v[1], budget=v[2])
            for v in s.execute(stmt).all()
        ]


def get_categories() -> Sequence[str]:
    with Session(_engine) as s:
        res = s.execute(
            select(Transaction.category).distinct().order_by(Transaction.category)
        )
        return [v[0] for v in res.all()]


def get_budgets() -> Sequence[Budget]:
    with Session(_engine) as s:
        qry = select(Budget).order_by(Budget.category)

        return s.scalars(qry).all()


def add_budgets(budgets: List[Budget]):
    with Session(_engine) as s:
        s.add_all(budgets)
        s.commit()


def update_budgets(budgets: List[dict]):
    with Session(_engine) as s:
        s.execute(update(Budget), budgets)
        s.commit()


def delete_budget_by_id(ids: List[int]):
    with Session(_engine) as s:
        s.execute(delete(Budget).where(Budget.id.in_(ids)))
        s.commit()


def get_bills() -> Sequence[Bill]:
    with Session(_engine) as s:
        qry = select(Bill).order_by(Bill.id)
        return s.scalars(qry).all()


def add_bills(bills: List[Bill]):
    with Session(_engine) as s:
        s.add_all(bills)
        s.commit()


def update_bills(bills: List[dict]):
    with Session(_engine) as s:
        s.execute(update(Bill), bills)
        s.commit()


def delete_bill_by_id(ids: List[int]):
    with Session(_engine) as s:
        s.execute(delete(Bill).where(Bill.id.in_(ids)))
        s.commit()


def match_bills_to_transactions(bills: List[Bill]) -> int:
    num_updated = 0
    with Session(_engine) as s:
        for b in bills:
            res = s.execute(
                update(Transaction)
                .where(
                    and_(
                        or_(Transaction.bill_id != b.id, Transaction.bill_id.is_(None)),
                        Transaction.description.like(b.regex_str),
                    )
                )
                .values(bill_id=b.id)
                .returning(Transaction.id)
            ).all()
            s.commit()
            num_matched = len(res)
            num_updated += num_matched

            print(f"assigned {num_matched} transactions for bill: {b.name}")
    return num_updated
