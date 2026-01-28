import datetime
import decimal
import re
from dataclasses import dataclass
from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    name: Mapped[str] = mapped_column(String(256), primary_key=True, unique=True)
    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="source_account"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    description: Mapped[str] = mapped_column(String(256))
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric())
    category: Mapped[str] = mapped_column(String(256), index=True)
    date: Mapped[datetime.datetime] = mapped_column(DateTime(), index=True)
    source_account_name: Mapped[str] = mapped_column(ForeignKey("accounts.name"))
    source_account: Mapped[Account] = relationship("Account")
    bill_id: Mapped[int] = mapped_column(
        ForeignKey("bills.id", name="fk_bill_id"), nullable=True
    )
    bill = relationship("Bill")


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(256))
    budget: Mapped[decimal.Decimal] = mapped_column(Numeric())


class Bill(Base):
    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    # Amount matched in a period for bill
    name: Mapped[str] = mapped_column(String(256), index=True)
    regex_str: Mapped[str] = mapped_column(String(256))
    expected_amount: Mapped[decimal.Decimal] = mapped_column(Numeric())
    transactions: Mapped[List[Transaction]] = relationship(
        "Transaction", back_populates="bill"
    )


@dataclass
class CategoryExpense:
    category: str
    spent: decimal.Decimal
    budget: decimal.Decimal


@dataclass
class BillCharged:
    name: str
    expected_amount: decimal.Decimal
    charged: decimal.Decimal
