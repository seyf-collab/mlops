import pandas as pd

from src.config import load_config
from src.predictor import Predictor


def test_model_loads():
    config = load_config()

    predictor = Predictor(config)

    assert predictor.model is not None


def test_prediction_shape():
    config = load_config()

    predictor = Predictor(config)

    df = pd.DataFrame(
        [
            {
                "order_purchase_timestamp": "2018-01-01 10:00:00",
                "order_estimated_delivery_date": "2018-01-10 00:00:00",
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

    predictions, probabilities = predictor.predict(df)

    assert len(predictions) == 1
    assert len(probabilities) == 1
