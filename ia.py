import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor


def pivot_forecasts(all_forecasts):
    """
    Pivot forecasts to have one row per run_datetime + datetime with each model as a column.

    Args:
        all_forecasts: DataFrame with [model, run_datetime, datetime, precipitation, precipitation_obs]

    Return:
        pivoted DataFrame
    """
    pivot_df = all_forecasts.pivot_table(
        index=["run_datetime", "datetime", "precipitation_obs"],
        columns="model",
        values="precipitation"
    ).reset_index()
    pivot_df.columns.name = None
    return pivot_df


def train_weights(pivot_df):
    """
    Train linear regression to find optimal weights for models.

    Args:
        pivot_df: DataFrame with [run_datetime, datetime, precipitation_obs, models...]

    Return:
        fitted model, weights dict
    """
    X = pivot_df.drop(columns=["run_datetime", "datetime", "precipitation_obs"]).values
    y = pivot_df["precipitation_obs"].values

    reg = LinearRegression(fit_intercept=False)
    reg.fit(X, y)

    model_names = pivot_df.drop(columns=["run_datetime", "datetime", "precipitation_obs"]).columns
    weights = dict(zip(model_names, reg.coef_))
    return reg, weights


def evaluate_models(pivot_df, reg):
    """
    Compute RMSE/MAE for each model and for the ensemble.

    Args:
        pivot_df: DataFrame pivoted
        reg: trained regression model

    Return:
        metrics DataFrame
    """
    results = []

    # Métricas por modelo individual
    for model in pivot_df.drop(columns=["run_datetime", "datetime", "precipitation_obs"]).columns:
        rmse = np.sqrt(mean_squared_error(
            pivot_df["precipitation_obs"], pivot_df[model].fillna(0)
        ))
        mae = mean_absolute_error(
            pivot_df["precipitation_obs"], pivot_df[model].fillna(0)
        )
        results.append({"model": model, "RMSE": rmse, "MAE": mae})

    # Ensemble treinado
    X = pivot_df.drop(columns=["run_datetime", "datetime", "precipitation_obs"]).fillna(0).values
    y_true = pivot_df["precipitation_obs"].values
    y_pred = reg.predict(X)

    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    results.append({"model": "Ensemble_AI", "RMSE": rmse, "MAE": mae})

    return pd.DataFrame(results)


def pipeline(df_pivot):
    X = df_pivot.drop(columns=["run_datetime", "datetime", "precipitation_obs"])
    y = df_pivot["precipitation_obs"]

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Define candidate models
    models = {
        "RandomForest": RandomForestRegressor(n_estimators=200, random_state=42),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=200, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=300, learning_rate=0.05, random_state=42)
    }

    results = {}
    for name, model in models.items():
        pipe = Pipeline([
            ("scaler", StandardScaler()),  # optional, tree models don’t need scaling
            ("regressor", model)
        ])
        
        scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring="neg_mean_squared_error")
        rmse_scores = np.sqrt(-scores)
        
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        
        results[name] = {
            "CV RMSE mean": rmse_scores.mean(),
            "Test RMSE": np.sqrt(mean_squared_error(y_test, y_pred)),
            "Test MAE": mean_absolute_error(y_test, y_pred),
            "Test R2": r2_score(y_test, y_pred),
            "Model": pipe
        }

    best_model = min(results.items(), key=lambda x: x[1]["Test RMSE"])
    print("Best model:", best_model[0])
    print(results[best_model[0]])