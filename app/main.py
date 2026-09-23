import json
import logging
import time
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from app.schemas import (
    BatchOrderInput,
    BatchPredictionResponse,
    OrderInput,
    PredictionResponse,
)

from src.config import load_config
from src.data_access import (
    init_prediction_logs,
    save_prediction_log,
)
from src.logging_config import setup_logging
from src.predictor import Predictor
from src.validation import DataValidator


config = load_config()

log_path = (
    Path(config["paths"]["prediction_log"])
)

setup_logging(log_path)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Olist Late Delivery API",
    version="1.0.0",
)

predictor = Predictor(config)

validator = DataValidator(
    config["validation"]["rules_file"]
)

request_count = Counter(
    "prediction_requests_total",
    "Total prediction requests",
)

error_count = Counter(
    "prediction_errors_total",
    "Total prediction errors",
)

prediction_count = Counter(
    "prediction_total",
    "Total predictions",
    ["prediction"],
)

latency = Histogram(
    "prediction_latency_seconds",
    "Prediction latency",
)

predicted_late_rate = Gauge(
    "predicted_late_rate",
    "Current late prediction rate",
)

prediction_drift = Gauge(
    "prediction_drift",
    "Difference from baseline late rate",
)

total_predictions = 0
late_predictions = 0


@app.on_event("startup")
def startup():
    try:
        init_prediction_logs()
    except Exception:
        logger.exception(
            "Could not initialize prediction logs"
        )


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.get("/model")
def model_info():
    return {
        "model_name": config["model"]["name"],
        "model_version": predictor.model_version,
        "model_stage": predictor.model_stage,
    }


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


def run_prediction(order_dict):
    global total_predictions
    global late_predictions

    request_count.inc()

    start = time.perf_counter()

    df = pd.DataFrame(
        [order_dict]
    )

    validation_result = validator.validate(
        df
    )

    if not validation_result["success"]:
        error_count.inc()

        raise HTTPException(
            status_code=422,
            detail={
                "message": "Input validation failed",
                "details": validation_result[
                    "failures"
                ],
            },
        )

    try:
        predictions, probabilities = (
            predictor.predict(df)
        )

        predicted_class = int(
            predictions[0]
        )

        probability = float(
            probabilities[0]
        )

        prediction_name = (
            "late"
            if predicted_class == 1
            else "on_time"
        )

        elapsed = (
            time.perf_counter() - start
        )

        latency.observe(elapsed)

        prediction_count.labels(
            prediction=prediction_name
        ).inc()

        total_predictions += 1

        if predicted_class == 1:
            late_predictions += 1

        current_late_rate = (
            late_predictions
            / total_predictions
        )

        predicted_late_rate.set(
            current_late_rate
        )

        drift = abs(
            current_late_rate
            - config["monitoring"][
                "baseline_late_rate"
            ]
        )

        prediction_drift.set(
            drift
        )

        if (
            drift
            > config["monitoring"][
                "prediction_drift_threshold"
            ]
        ):
            logger.warning(
                "Prediction drift threshold exceeded"
            )

        output = {
            "prediction": prediction_name,
            "probability": probability,
            "model_version": (
                predictor.model_version
            ),
        }

        input_data = json.loads(
            json.dumps(
                order_dict,
                default=str,
            )
        )

        logger.info(
            "Prediction | input=%s | output=%s | "
            "latency_ms=%.3f | model_version=%s",
            input_data,
            output,
            elapsed * 1000,
            predictor.model_version,
        )

        try:
            save_prediction_log(
                input_data=input_data,
                output_data=output,
                latency_ms=elapsed * 1000,
                model_version=(
                    predictor.model_version
                ),
            )
        except Exception:
            logger.exception(
                "Failed to store prediction log"
            )

        return output

    except HTTPException:
        raise

    except Exception as exc:
        error_count.inc()

        logger.exception(
            "Prediction failed: %s",
            exc,
        )

        raise HTTPException(
            status_code=500,
            detail="Prediction failed",
        ) from exc


@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(order: OrderInput):
    return run_prediction(
        order.model_dump(mode="json")
    )


@app.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
)
def predict_batch(
    request: BatchOrderInput,
):
    outputs = []

    for order in request.orders:
        outputs.append(
            run_prediction(
                order.model_dump(mode="json")
            )
        )

    return {
        "predictions": outputs
    }