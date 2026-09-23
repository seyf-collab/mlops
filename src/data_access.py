import json
import os

from sqlalchemy import create_engine, text


def get_engine():
    database_url = os.environ["DATABASE_URL"]

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


def init_prediction_logs():
    engine = get_engine()

    query = text(
        """
        CREATE TABLE IF NOT EXISTS prediction_logs (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            model_version VARCHAR(100),
            latency_ms DOUBLE,
            input_json JSON,
            output_json JSON
        )
        """
    )

    with engine.begin() as connection:
        connection.execute(query)


def save_prediction_log(
    input_data,
    output_data,
    latency_ms,
    model_version,
):
    engine = get_engine()

    query = text(
        """
        INSERT INTO prediction_logs
        (
            model_version,
            latency_ms,
            input_json,
            output_json
        )
        VALUES
        (
            :model_version,
            :latency_ms,
            :input_json,
            :output_json
        )
        """
    )

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "model_version": model_version,
                "latency_ms": latency_ms,
                "input_json": json.dumps(
                    input_data,
                    default=str,
                ),
                "output_json": json.dumps(
                    output_data,
                    default=str,
                ),
            },
        )
