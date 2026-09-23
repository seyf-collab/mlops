from datetime import datetime

from pydantic import BaseModel


class OrderInput(BaseModel):
    order_purchase_timestamp: datetime
    order_estimated_delivery_date: datetime

    customer_zip_code_prefix: int | None = None
    customer_city: str
    customer_state: str

    number_of_items: float | None = None
    total_price: float | None = None
    total_freight: float | None = None
    total_payment: float | None = None
    max_installments: float | None = None


class PredictionResponse(BaseModel):
    prediction: str
    probability: float
    model_version: str


class BatchOrderInput(BaseModel):
    orders: list[OrderInput]


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]
