from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200


def test_model_info():
    response = client.get(
        "/model"
    )

    assert response.status_code == 200

    body = response.json()

    assert "model_version" in body


def test_predict():
    payload = {
        "order_purchase_timestamp":
            "2018-01-01T10:00:00",
        "order_estimated_delivery_date":
            "2018-01-10T00:00:00",
        "customer_zip_code_prefix": 1000,
        "customer_city": "sao paulo",
        "customer_state": "SP",
        "number_of_items": 1,
        "total_price": 100,
        "total_freight": 20,
        "total_payment": 120,
        "max_installments": 2,
    }

    response = client.post(
        "/predict",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert "prediction" in body
    assert "probability" in body
    assert "model_version" in body