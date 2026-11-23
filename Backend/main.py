
# ==========================================
# AQUASENSE AI - FASTAPI BACKEND
# ==========================================

from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models"

RESULTS_PATH = BASE_DIR / "reports" / "AquaSense_Integrated_Model_Results.csv"

FORECAST_MODEL_PATH = MODEL_DIR / "AquaSense_Demand_Forecasting_Model.pkl"

FORECAST_FEATURES_PATH = MODEL_DIR / "AquaSense_Model_Features.pkl"

ANOMALY_MODEL_PATH = MODEL_DIR / "AquaSense_Anomaly_Detection_Model_V3.pkl"


# ==========================================
# 2. FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="AquaSense AI API",
    description="Smart Water Intelligence Platform",
    version="1.0.0"
)


# ==========================================
# 3. CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 4. LOAD MACHINE LEARNING MODELS
# ==========================================

forecast_model = joblib.load(FORECAST_MODEL_PATH)

forecast_features = joblib.load(FORECAST_FEATURES_PATH)

anomaly_bundle = joblib.load(ANOMALY_MODEL_PATH)

anomaly_model = anomaly_bundle["model"]

anomaly_threshold = anomaly_bundle["threshold"]

anomaly_features = anomaly_bundle["features"]


# ==========================================
# 5. HOME API
# ==========================================

@app.get("/")
def home():

    return {
        "message": "Welcome to AquaSense AI API",
        "status": "Running"
    }


# ==========================================
# 6. HEALTH CHECK API
# ==========================================

@app.get("/api/health")
def health_check():

    return {
        "status": "healthy",
        "project": "AquaSense AI",
        "forecast_model": "Random Forest Loaded",
        "anomaly_model": "Isolation Forest V3 Loaded",
        "forecast_features": len(forecast_features),
        "anomaly_features": len(anomaly_features),
        "anomaly_threshold": float(anomaly_threshold)
    }


# ==========================================
# 7. DASHBOARD SUMMARY API
# ==========================================

@app.get("/api/dashboard-summary")
def dashboard_summary():

    # Check whether results file exists
    if not RESULTS_PATH.exists():

        raise HTTPException(
            status_code=404,
            detail=f"Results file not found: {RESULTS_PATH}"
        )

    # Load integrated ML results
    df = pd.read_csv(RESULTS_PATH)

    # Check required columns
    required_columns = [
        "Actual_Consumption",
        "Anomaly_Status"
    ]

    for column in required_columns:

        if column not in df.columns:

            raise HTTPException(
                status_code=500,
                detail=f"Required column missing: {column}"
            )

    # Calculate dashboard statistics
    total_records = len(df)

    total_consumption = pd.to_numeric(
        df["Actual_Consumption"],
        errors="coerce"
    ).sum()

    average_consumption = pd.to_numeric(
        df["Actual_Consumption"],
        errors="coerce"
    ).mean()

    # Count anomaly records
    anomaly_alerts = (
        df["Anomaly_Status"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("anomaly")
        .sum()
    )

    normal_records = total_records - anomaly_alerts

    # Return dashboard data
    return {
        "total_records": int(total_records),
        "total_consumption": round(float(total_consumption), 2),
        "average_consumption": round(float(average_consumption), 2),
        "anomaly_alerts": int(anomaly_alerts),
        "normal_records": int(normal_records)
    }


# ==========================================
# 8. MONTHLY CONSUMPTION TRENDS API
# ==========================================

@app.get("/api/consumption-trends")
def consumption_trends():

    if not RESULTS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Integrated results file not found"
        )

    df = pd.read_csv(RESULTS_PATH)

    required_columns = [
        "Timestamp",
        "Actual_Consumption",
        "Predicted_Consumption",
        "Anomaly_Status"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise HTTPException(
                status_code=500,
                detail=f"Missing column: {column}"
            )

    # Convert timestamp and consumption columns
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"],
        errors="coerce"
    )

    df["Actual_Consumption"] = pd.to_numeric(
        df["Actual_Consumption"],
        errors="coerce"
    )

    df["Predicted_Consumption"] = pd.to_numeric(
        df["Predicted_Consumption"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "Timestamp",
            "Actual_Consumption",
            "Predicted_Consumption"
        ]
    ).copy()

    # Create monthly grouping column
    df["Month"] = df["Timestamp"].dt.to_period("M")

    # Calculate monthly averages and anomaly counts
    monthly = df.groupby("Month").agg(
        actual_mean=("Actual_Consumption", "mean"),
        predicted_mean=("Predicted_Consumption", "mean"),
        anomaly_count=(
            "Anomaly_Status",
            lambda x: (
                x.astype(str).str.strip().str.lower() == "anomaly"
            ).sum()
        )
    ).reset_index()

    return {
        "months": monthly["Month"].astype(str).tolist(),
        "actual_consumption": monthly["actual_mean"].round(2).tolist(),
        "predicted_consumption": monthly["predicted_mean"].round(2).tolist(),
        "anomaly_count": monthly["anomaly_count"].astype(int).tolist()
    }

@app.get("/api/anomaly-records")
def anomaly_records():
    if not RESULTS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Integrated results file not found"
        )

    df = pd.read_csv(RESULTS_PATH)

    required_columns = [
        "Timestamp",
        "Actual_Consumption",
        "Predicted_Consumption",
        "Anomaly_Score",
        "Anomaly_Status"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise HTTPException(
                status_code=500,
                detail=f"Missing column: {column}"
            )

    df["Anomaly_Status"] = (
        df["Anomaly_Status"].astype(str).str.strip().str.lower()
    )

    anomalies = df[df["Anomaly_Status"] == "anomaly"].copy()
    anomalies["Timestamp"] = pd.to_datetime(
        anomalies["Timestamp"], errors="coerce"
    )

    anomalies = anomalies.dropna(subset=["Timestamp"])
    anomalies = anomalies.sort_values("Timestamp", ascending=False)

    return {
        "total_anomalies": len(anomalies),
        "records": [
            {
                "timestamp": row["Timestamp"].strftime("%Y-%m-%d %H:%M"),
                "actual_consumption": round(float(row["Actual_Consumption"]), 2),
                "predicted_consumption": round(float(row["Predicted_Consumption"]), 2),
                "anomaly_score": round(float(row["Anomaly_Score"]), 6),
                "status": "Anomaly"
            }
            for _, row in anomalies.iterrows()
        ]
    }

    
# ==========================================
# 10. DEMAND PREDICTION RECORDS API
# ==========================================

@app.get("/api/prediction-records")
def prediction_records():

    if not RESULTS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Integrated results file not found"
        )

    df = pd.read_csv(RESULTS_PATH)

    required_columns = [
        "Timestamp",
        "Actual_Consumption",
        "Predicted_Consumption"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise HTTPException(
                status_code=500,
                detail=f"Missing column: {column}"
            )

    # Convert columns to correct data types
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"], errors="coerce"
    )

    df["Actual_Consumption"] = pd.to_numeric(
        df["Actual_Consumption"], errors="coerce"
    )

    df["Predicted_Consumption"] = pd.to_numeric(
        df["Predicted_Consumption"], errors="coerce"
    )

    # Remove incomplete records
    df = df.dropna(
        subset=[
            "Timestamp",
            "Actual_Consumption",
            "Predicted_Consumption"
        ]
    ).copy()

    # Calculate prediction error
    df["Prediction_Error"] = (
        df["Actual_Consumption"] -
        df["Predicted_Consumption"]
    )

    df["Absolute_Error"] = df["Prediction_Error"].abs()

    # Sort newest records first
    df = df.sort_values(
        "Timestamp",
        ascending=False
    )

    return {
        "total_records": int(len(df)),

        "mae": round(
            float(df["Absolute_Error"].mean()), 2
        ),

        "average_actual": round(
            float(df["Actual_Consumption"].mean()), 2
        ),

        "average_predicted": round(
            float(df["Predicted_Consumption"].mean()), 2
        ),

        "records": [
            {
                "timestamp": row["Timestamp"].strftime(
                    "%Y-%m-%d %H:%M"
                ),

                "actual_consumption": round(
                    float(row["Actual_Consumption"]), 2
                ),

                "predicted_consumption": round(
                    float(row["Predicted_Consumption"]), 2
                ),

                "prediction_error": round(
                    float(row["Prediction_Error"]), 2
                )
            }

            for _, row in df.head(100).iterrows()
        ]
    }


