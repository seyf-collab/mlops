import tempfile
from pathlib import Path

import joblib
import mlflow
from mlflow import MlflowClient

from src.features import transform_features


class Predictor:
    def __init__(self, config):
        self.config = config

        mlflow_uri = config["mlflow"]["tracking_uri"]

        mlflow.set_tracking_uri(
            mlflow_uri
        )

        self.client = MlflowClient(
            tracking_uri=mlflow_uri
        )

        model_name = config["model"]["name"]
        model_version = str(
            config["model"]["version"]
        )

        model_uri = (
            f"models:/{model_name}/{model_version}"
        )

        self.model = mlflow.sklearn.load_model(
            model_uri
        )

        model_info = self.client.get_model_version(
            model_name,
            model_version,
        )

        self.model_version = str(
            model_info.version
        )

        self.model_stage = (
            model_info.current_stage
        )

        cache_dir = Path(
            tempfile.mkdtemp(
                prefix="olist_model_"
            )
        )

        numeric_path = (
            self.client.download_artifacts(
                model_info.run_id,
                "inference_artifacts/"
                "numeric_imputer.pkl",
                str(cache_dir),
            )
        )

        categorical_path = (
            self.client.download_artifacts(
                model_info.run_id,
                "inference_artifacts/"
                "categorical_imputer.pkl",
                str(cache_dir),
            )
        )

        encoder_path = (
            self.client.download_artifacts(
                model_info.run_id,
                "inference_artifacts/"
                "onehot_encoder.pkl",
                str(cache_dir),
            )
        )

        self.numeric_imputer = joblib.load(
            numeric_path
        )

        self.categorical_imputer = joblib.load(
            categorical_path
        )

        self.encoder = joblib.load(
            encoder_path
        )

    def predict(self, df):
        features = transform_features(
            df,
            self.config,
            self.numeric_imputer,
            self.categorical_imputer,
            self.encoder,
        )

        probabilities = (
            self.model.predict_proba(features)
        )[:, 1]

        predictions = self.model.predict(
            features
        )

        return predictions, probabilities