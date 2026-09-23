import json
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]

TRAIN_PATH = ROOT_DIR / "artifacts" / "train.csv"

OUTPUT_PATH = ROOT_DIR / "config" / "validation_rules.json"


NUMERICAL = [
    "customer_zip_code_prefix",
    "number_of_items",
    "total_price",
    "total_freight",
    "total_payment",
    "max_installments",
]

CATEGORICAL = [
    "customer_city",
    "customer_state",
]


def main():
    train = pd.read_csv(TRAIN_PATH)

    rules = {
        "columns": (
            NUMERICAL
            + CATEGORICAL
            + [
                "order_purchase_timestamp",
                "order_estimated_delivery_date",
            ]
        ),
        "numeric_ranges": {},
        "allowed_categories": {},
        "missing_rates": {},
    }

    for column in NUMERICAL:
        rules["numeric_ranges"][column] = {
            "min": float(train[column].min()),
            "max": float(train[column].max()),
        }

        rules["missing_rates"][column] = float(train[column].isna().mean())

    for column in CATEGORICAL:
        rules["allowed_categories"][column] = sorted(
            train[column].dropna().astype(str).unique().tolist()
        )

        rules["missing_rates"][column] = float(train[column].isna().mean())

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            rules,
            file,
            indent=2,
            ensure_ascii=False,
        )


if __name__ == "__main__":
    main()
