import re

from components.money.categories import Categories

# bills_regex = re.compile(
#     "|".join(
#         [
#             "verizon",
#             "cloudflare",
#             "progressive",
#             "bank of america",
#             "head over heels",
#             "clubpilate",
#             "pets best ins",
#             "youtubepremium",
#             "netflix",
#             "pseg",
#             "bsi financial",
#             "cko",
#             "octopus music school",
#         ]
#     )
# )
income_regex = re.compile(
    "|".join(["payroll ach from spotify", "ach deposit", "interest paid", "cashback"])
)


credit_card_payment_regex = re.compile("(capital one online pmt)")
transfer_regex = re.compile("(transfer to|transfer from)")

all_regex = {
    Categories.Income: income_regex,
    Categories.CreditCardPayment: credit_card_payment_regex,
    Categories.Transfer: transfer_regex,
}


def get_category(description: str, existing: str) -> str:
    if not existing:
        for cat, r in all_regex.items():
            if r.match(description):
                existing = cat.name
    return existing or Categories.Other.name
