import argparse
import json
import sys

import pandas as pd

from src.config import load_config
from src.predictor import Predictor
from src.validation import DataValidator


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
    )

    args = parser.parse_args()

    config = load_config()

    predictor = Predictor(config)

    validator = DataValidator(
        config["validation"]["rules_file"]
    )

    with open(
        args.input,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    df = pd.DataFrame([data])

    validation_result = validator.validate(
        df
    )

    if not validation_result["success"]:
        sys.stderr.write(
            json.dumps(
                validation_result,
                indent=2,
            )
        )
        sys.exit(1)

    predictions, probabilities = (
        predictor.predict(df)
    )

    output = {
        "prediction": (
            "late"
            if int(predictions[0]) == 1
            else "on_time"
        ),
        "probability": float(
            probabilities[0]
        ),
        "model_version": predictor.model_version,
    }

    sys.stdout.write(
        json.dumps(
            output,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()