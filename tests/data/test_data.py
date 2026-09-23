import pandas as pd


def test_train_schema():
    train = pd.read_csv("artifacts/train.csv")

    required_columns = [
        "order_id",
        "customer_id",
        "customer_city",
        "customer_state",
        "late_delivery",
    ]

    for column in required_columns:
        assert column in train.columns


def test_label_values():
    train = pd.read_csv("artifacts/train.csv")

    assert set(train["late_delivery"].dropna().unique()).issubset({0, 1})


def test_no_label_in_inference_features():
    forbidden = {
        "late_delivery",
        "order_delivered_customer_date",
        "order_delivered_carrier_date",
    }

    feature_columns = {
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
        "number_of_items",
        "total_price",
        "total_freight",
        "total_payment",
        "max_installments",
        "purchase_year",
        "purchase_month",
        "purchase_dayofweek",
        "purchase_hour",
        "estimated_delivery_days",
    }

    assert forbidden.isdisjoint(feature_columns)
