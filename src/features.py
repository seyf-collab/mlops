import pandas as pd
from scipy import sparse


def build_feature_frame(df, config):
    df = df.copy()

    purchase_datetime = config["features"]["purchase_datetime"]
    estimated_datetime = config["features"]["estimated_datetime"]

    df[purchase_datetime] = pd.to_datetime(
        df[purchase_datetime],
        errors="coerce",
    )

    df[estimated_datetime] = pd.to_datetime(
        df[estimated_datetime],
        errors="coerce",
    )

    df["purchase_year"] = df[purchase_datetime].dt.year
    df["purchase_month"] = df[purchase_datetime].dt.month
    df["purchase_dayofweek"] = df[purchase_datetime].dt.dayofweek
    df["purchase_hour"] = df[purchase_datetime].dt.hour

    df["estimated_delivery_days"] = (
        df[estimated_datetime] - df[purchase_datetime]
    ).dt.total_seconds() / (24 * 60 * 60)

    numerical_features = config["features"]["numerical"]
    categorical_features = config["features"]["categorical"]

    feature_columns = numerical_features + categorical_features

    return df[feature_columns]


def transform_features(
    df,
    config,
    numeric_imputer,
    categorical_imputer,
    encoder,
):
    feature_df = build_feature_frame(
        df,
        config,
    )

    numerical_features = config["features"]["numerical"]
    categorical_features = config["features"]["categorical"]

    numeric = numeric_imputer.transform(feature_df[numerical_features])

    categorical_imputed = categorical_imputer.transform(
        feature_df[categorical_features]
    )

    categorical = encoder.transform(categorical_imputed)

    numeric_sparse = sparse.csr_matrix(numeric)

    return sparse.hstack(
        [numeric_sparse, categorical],
        format="csr",
    )
