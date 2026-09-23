import pandas as pd

from src.config import load_config
from src.features import build_feature_frame


def test_feature_building():
    config = load_config()

    df = pd.DataFrame(
        [
            {
                "order_purchase_timestamp":
                    "2018-01-01 10:00:00",
                "order_estimated_delivery_date":
                    "2018-01-10 00:00:00",
                "customer_zip_code_prefix": 1000,
                "customer_city": "sao paulo",
                "customer_state": "SP",
                "number_of_items": 1,
                "total_price": 100,
                "total_freight": 20,
                "total_payment": 120,
                "max_installments": 2,
            }
        ]
    )

    result = build_feature_frame(
        df,
        config,
    )

    assert result.shape[1] == 13