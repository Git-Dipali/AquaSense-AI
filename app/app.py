
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import joblib

from pathlib import Path

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AquaSense AI",
    page_icon="💧",
    layout="wide"
)

# ==========================================
# 2. FILE PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR / "reports" /
    "AquaSense_Integrated_Model_Results.csv"
)

MODEL_PATH = (
    BASE_DIR / "models" /
    "AquaSense_Demand_Forecasting_Model.pkl"
)

FEATURES_PATH = (
    BASE_DIR / "models" /
    "AquaSense_Model_Features.pkl"
)

FEATURE_DATA_PATH = (
    BASE_DIR / "dataset" /
    "AquaSense_Feature_Engineered.csv"
)

# ==========================================
# 3. LOAD TRAINED MODEL
# ==========================================

try:

    forecast_model = joblib.load(MODEL_PATH)

    forecast_features = joblib.load(FEATURES_PATH)

    feature_data = pd.read_csv(FEATURE_DATA_PATH)

    feature_data["Timestamp"] = pd.to_datetime(
        feature_data["Timestamp"]
    )

    feature_data = feature_data.sort_values(
        by="Timestamp"
    ).reset_index(drop=True)

except Exception as e:

    st.error(f"Unable to load forecasting model or data: {e}")
    st.stop()

# ==========================================
# 4. PROFESSIONAL CUSTOM CSS
# ==========================================

st.markdown("""
<style>

/* MAIN BACKGROUND */

.stApp {
    background-color: #F3F7FB;
    color: #243447;
}

/* MAIN CONTENT */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* HEADINGS */

h1 {
    color: #123B5D !important;
    font-weight: 750 !important;
}

h2, h3 {
    color: #164E75 !important;
    font-weight: 650 !important;
}

/* TEXT */

p, label {
    color: #34495E;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #102F4F 0%,
        #164E75 100%
    );
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* KPI CARDS */

[data-testid="stMetric"] {
    background-color: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #DCE8F2;
    box-shadow: 0 3px 10px rgba(20, 60, 90, 0.06);
}

[data-testid="stMetricLabel"] {
    color: #58758D !important;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #123B5D !important;
    font-weight: 750;
}

/* BUTTONS */

.stButton > button {
    background-color: #087EAC;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 10px 22px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #065F85;
    color: white;
}

/* DOWNLOAD BUTTONS */

.stDownloadButton > button {
    background-color: #087EAC;
    color: white;
    border-radius: 9px;
    border: none;
    font-weight: 600;
}

.stDownloadButton > button:hover {
    background-color: #065F85;
    color: white;
}

/* INPUT FIELDS */

.stTextInput input,
.stNumberInput input {
    border-radius: 8px;
}

/* DATA TABLE */

[data-testid="stDataFrame"] {
    border: 1px solid #DCE8F2;
    border-radius: 10px;
}

/* DIVIDERS */

hr {
    border-color: #DCE8F2;
}

/* ALERT BOXES */

[data-testid="stAlert"] {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. LOAD INTEGRATED MODEL RESULTS
# ==========================================

@st.cache_data
def load_data():

    data = pd.read_csv(DATA_PATH)

    data["Timestamp"] = pd.to_datetime(
        data["Timestamp"]
    )

    return data


try:

    df = load_data()

except FileNotFoundError:

    st.error("Integrated results file not found.")

    st.write(
        "Expected file:",
        str(DATA_PATH)
    )

    st.stop()

except Exception as e:

    st.error(f"Unable to load integrated data: {e}")

    st.stop()

# ==========================================
# 6. PREPARE DATA
# ==========================================

required_columns = [
    "Timestamp",
    "Actual_Consumption",
    "Predicted_Consumption",
    "Anomaly_Score",
    "Anomaly_Status"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:

    st.error(
        f"Missing required columns: {missing_columns}"
    )

    st.stop()


df = df.sort_values(
    by="Timestamp"
).reset_index(drop=True)


# Convert anomaly status into numeric values

numeric_status = pd.to_numeric(
    df["Anomaly_Status"],
    errors="coerce"
)

text_status = (
    df["Anomaly_Status"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map({
        "anomaly": -1,
        "normal": 1,
        "-1": -1,
        "1": 1
    })
)

df["Anomaly_Status"] = numeric_status.fillna(
    text_status
)


# Create readable anomaly labels

df["Anomaly_Label"] = df["Anomaly_Status"].map({
    -1: "Anomaly",
    1: "Normal"
})


# Calculate overall statistics

total_records = len(df)

total_consumption = df["Actual_Consumption"].sum()

average_consumption = df["Actual_Consumption"].mean()

anomaly_count = (
    df["Anomaly_Status"] == -1
).sum()

normal_count = (
    df["Anomaly_Status"] == 1
).sum()


# ==========================================
# 7. SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("💧 AquaSense AI")

st.sidebar.caption(
    "Smart Water Intelligence Platform"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Demand Prediction",
        "Anomaly Detection",
        "Analytics",
        "Reports"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "AI-powered water demand forecasting "
    "and unusual consumption monitoring."
)

st.sidebar.caption(
    "Machine Learning | Smart Water Management"
)


# ==========================================
# 8. PAGE 1: OVERVIEW
# ==========================================

if page == "Overview":

    st.title("💧 AquaSense AI")

    st.subheader(
        "Smart Water Intelligence Dashboard"
    )

    st.write(
        "Monitor water consumption, forecast demand, "
        "and identify unusual usage patterns."
    )

    st.divider()

    # DATE FILTER

    st.subheader("Filter Consumption by Date")

    min_date = df["Timestamp"].min().date()

    max_date = df["Timestamp"].max().date()

    date_col1, date_col2 = st.columns(2)

    with date_col1:

        start_date = st.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

    with date_col2:

        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

    if start_date > end_date:

        st.error(
            "Start Date cannot be after End Date."
        )

        st.stop()

    filtered_df = df[
        (df["Timestamp"].dt.date >= start_date) &
        (df["Timestamp"].dt.date <= end_date)
    ]

    if filtered_df.empty:

        st.warning(
            "No records found for the selected dates."
        )

        st.stop()

    # FILTERED STATISTICS

    filtered_total = len(filtered_df)

    filtered_consumption = (
        filtered_df["Actual_Consumption"].sum()
    )

    filtered_average = (
        filtered_df["Actual_Consumption"].mean()
    )

    filtered_anomalies = (
        filtered_df["Anomaly_Status"] == -1
    ).sum()

    filtered_normal = (
        filtered_df["Anomaly_Status"] == 1
    ).sum()

    st.divider()

    # KPI CARDS

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Records",
        f"{filtered_total:,}"
    )

    col2.metric(
        "Total Consumption",
        f"{filtered_consumption:,.0f}"
    )

    col3.metric(
        "Average Consumption",
        f"{filtered_average:,.2f}"
    )

    col4.metric(
        "Anomaly Alerts",
        f"{filtered_anomalies:,}"
    )

    st.divider()

    # ACTUAL VS PREDICTED

    st.subheader(
        "Water Demand: Actual vs Predicted"
    )

    fig = px.line(
        filtered_df.tail(300),
        x="Timestamp",
        y=[
            "Actual_Consumption",
            "Predicted_Consumption"
        ],
        labels={
            "value": "Water Consumption",
            "Timestamp": "Date",
            "variable": "Measurement"
        },
        title="Recent Water Consumption"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.divider()

    # ANOMALY SUMMARY

    st.subheader(
        "Anomaly Detection Summary"
    )

    anomaly_data = pd.DataFrame({
        "Status": ["Normal", "Anomaly"],
        "Records": [
            filtered_normal,
            filtered_anomalies
        ]
    })

    fig2 = px.pie(
        anomaly_data,
        names="Status",
        values="Records",
        hole=0.5,
        title="Normal vs Unusual Consumption"
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )


# ==========================================
# 9. PAGE 2: DEMAND PREDICTION
# ==========================================

elif page == "Demand Prediction":

    st.title("AI Water Demand Prediction")

    st.write(
        "Estimate water consumption using the "
        "trained Random Forest model."
    )

    st.divider()

    st.subheader(
        "Enter Prediction Details"
    )

    col1, col2 = st.columns(2)

    with col1:

        prediction_date = st.date_input(
            "Select Date",
            value=pd.Timestamp.now().date()
        )

        prediction_hour = st.slider(
            "Select Hour",
            min_value=0,
            max_value=23,
            value=12
        )

        temperature = st.number_input(
            "Temperature (°C)",
            min_value=-20.0,
            max_value=50.0,
            value=20.0,
            step=0.5
        )

    with col2:

        rain = st.number_input(
            "Rainfall",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.5
        )

        sun = st.number_input(
            "Sunshine",
            min_value=0.0,
            max_value=24.0,
            value=5.0,
            step=0.5
        )

    st.info(
        "The model also uses recent consumption history "
        "to generate its prediction."
    )

    if st.button(
        "Predict Water Demand",
        type="primary"
    ):

        selected_timestamp = (
            pd.Timestamp(prediction_date) +
            pd.Timedelta(hours=prediction_hour)
        )

        history = feature_data[
            feature_data["Timestamp"] < selected_timestamp
        ]

        if len(history) < 168:

            st.error(
                "Not enough historical consumption data "
                "before this date. Select a later date."
            )

        else:

            latest = history.iloc[-1]

            input_data = {

                "Hour": prediction_hour,

                "Day": selected_timestamp.day,

                "Month": selected_timestamp.month,

                "Year": selected_timestamp.year,

                "DayOfWeek": selected_timestamp.dayofweek,

                "Temperature": temperature,

                "Rain": rain,

                "Sun": sun,

                "Hour_sin": np.sin(
                    2 * np.pi * prediction_hour / 24
                ),

                "Hour_cos": np.cos(
                    2 * np.pi * prediction_hour / 24
                ),

                "Month_sin": np.sin(
                    2 * np.pi * selected_timestamp.month / 12
                ),

                "Month_cos": np.cos(
                    2 * np.pi * selected_timestamp.month / 12
                ),

                "Lag_1": latest["Consumption"],

                "Lag_24": history.iloc[-24]["Consumption"],

                "Lag_168": history.iloc[-168]["Consumption"],

                "Rolling_Mean_24": latest["Rolling_Mean_24"],

                "Rolling_Mean_168": latest["Rolling_Mean_168"]

            }

            input_df = pd.DataFrame(
                [input_data]
            )[forecast_features]

            prediction = forecast_model.predict(
                input_df
            )[0]

            st.divider()

            st.subheader(
                "Prediction Result"
            )

            st.metric(
                "Predicted Water Consumption",
                f"{prediction:,.2f}"
            )

            st.success(
                "Water demand prediction generated successfully!"
            )

            st.write(
                "Prediction Date:",
                selected_timestamp.strftime(
                    "%d %B %Y, %H:%M"
                )
            )

            st.caption(
                "Experimental estimate using the latest "
                "available historical consumption as lag "
                "information. It is not a guaranteed future forecast."
            )


# ==========================================
# 10. PAGE 3: ANOMALY DETECTION
# ==========================================

elif page == "Anomaly Detection":

    st.title("Anomaly Detection")

    st.write(
        "Identify unusual water consumption patterns "
        "using the Isolation Forest model."
    )

    st.warning(
        "An anomaly indicates unusual consumption. "
        "It does not confirm a physical water leak."
    )

    st.divider()

    anomaly_df = df[
        df["Anomaly_Status"] == -1
    ].copy()

    if anomaly_df.empty:

        st.info(
            "No anomaly records are available."
        )

    else:

        # DATE FILTERS

        st.subheader(
            "Filter Anomaly Alerts"
        )

        min_date = anomaly_df["Timestamp"].min().date()

        max_date = anomaly_df["Timestamp"].max().date()

        col1, col2 = st.columns(2)

        with col1:

            alert_start = st.date_input(
                "Start Date",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="alert_start"
            )

        with col2:

            alert_end = st.date_input(
                "End Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="alert_end"
            )

        if alert_start > alert_end:

            st.error(
                "Start Date cannot be after End Date."
            )

            st.stop()

        filtered_alerts = anomaly_df[
            (anomaly_df["Timestamp"].dt.date >= alert_start) &
            (anomaly_df["Timestamp"].dt.date <= alert_end)
        ].copy()

        st.divider()

        # ALERT STATISTICS

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Anomaly Alerts",
            f"{len(filtered_alerts):,}"
        )

        col2.metric(
            "Normal Records",
            f"{normal_count:,}"
        )

        # SORTING

        st.subheader(
            "Sort Anomaly Alerts"
        )

        sort_order = st.selectbox(
            "Choose sorting order",
            [
                "Most Unusual First",
                "Least Unusual First",
                "Latest First",
                "Oldest First"
            ]
        )

        if sort_order == "Most Unusual First":

            filtered_alerts = filtered_alerts.sort_values(
                "Anomaly_Score",
                ascending=True
            )

        elif sort_order == "Least Unusual First":

            filtered_alerts = filtered_alerts.sort_values(
                "Anomaly_Score",
                ascending=False
            )

        elif sort_order == "Latest First":

            filtered_alerts = filtered_alerts.sort_values(
                "Timestamp",
                ascending=False
            )

        else:

            filtered_alerts = filtered_alerts.sort_values(
                "Timestamp",
                ascending=True
            )

        # ALERT TABLE

        st.subheader(
            "Detected Unusual Consumption"
        )

        display_columns = [
            "Timestamp",
            "Actual_Consumption",
            "Predicted_Consumption",
            "Anomaly_Score"
        ]

        if filtered_alerts.empty:

            st.info(
                "No anomaly alerts found in the selected date range."
            )

        else:

            st.dataframe(
                filtered_alerts[display_columns],
                width="stretch",
                hide_index=True
            )

            # DOWNLOAD ALERT REPORT

            st.subheader(
                "Download Anomaly Report"
            )

            anomaly_csv = filtered_alerts[
                display_columns
            ].to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="Download Anomaly Alerts (CSV)",
                data=anomaly_csv,
                file_name="AquaSense_Anomaly_Alerts.csv",
                mime="text/csv",
                width="stretch"
            )

            # ANOMALY VISUALIZATION

            st.divider()

            st.subheader(
                "Anomaly Pattern Over Time"
            )

            fig = px.scatter(
                filtered_alerts,
                x="Timestamp",
                y="Actual_Consumption",
                color_discrete_sequence=["#E74C3C"],
                title="Detected Unusual Consumption Records"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        # AI ANOMALY INSIGHTS

        st.divider()

        st.subheader(
            "AquaSense AI - Anomaly Insights"
        )

        if not filtered_alerts.empty:

            insights_df = filtered_alerts.copy()

            insights_df["Consumption_Difference"] = (
                insights_df["Actual_Consumption"] -
                insights_df["Predicted_Consumption"]
            )

            # HIGHEST ALERT DAY

            daily_alerts = insights_df.groupby(
                insights_df["Timestamp"].dt.date
            ).size()

            highest_alert_date = daily_alerts.idxmax()

            highest_alert_count = daily_alerts.max()

            # HIGHEST CONSUMPTION

            highest_consumption = insights_df.loc[
                insights_df["Actual_Consumption"].idxmax()
            ]

            # LARGEST POSITIVE DIFFERENCE

            positive_differences = insights_df[
                insights_df["Consumption_Difference"] > 0
            ]

            if not positive_differences.empty:

                largest_difference = positive_differences[
                    "Consumption_Difference"
                ].max()

                st.markdown(
                    f"**3. Largest Positive Prediction Difference:** "
                    f"{largest_difference:,.2f}"
                )

            else:

                st.markdown(
                    "**3. Largest Positive Prediction Difference:** "
                    "No positive difference found."
                )

            # MOST FREQUENT ALERT HOUR

            hourly_alerts = insights_df.groupby(
                insights_df["Timestamp"].dt.hour
            ).size()

            busiest_hour = hourly_alerts.idxmax()

            # DISPLAY INSIGHTS

            st.markdown(
                f"**1. Highest Alert Day:** "
                f"{highest_alert_date} "
                f"({highest_alert_count} alerts)"
            )

            st.markdown(
                f"**2. Highest Consumption:** "
                f"{highest_consumption['Actual_Consumption']:,.2f}"
            )

            st.markdown(
                f"**4. Most Frequent Alert Hour:** "
                f"{busiest_hour}:00"
            )

            st.info(
                "These insights highlight unusual consumption patterns. "
                "They do not independently confirm a water leak."
            )

        else:

            st.info(
                "No anomaly insights available for the selected date range."
            )


# ==========================================
# 11. PAGE 4: ANALYTICS
# ==========================================

elif page == "Analytics":

    st.title(
        "Water Consumption Analytics"
    )

    st.write(
        "Explore historical consumption trends "
        "and distribution."
    )

    st.divider()

    analytics_df = df.copy()

    analytics_df["Month"] = (
        analytics_df["Timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    # MONTHLY AVERAGE

    monthly_data = (
        analytics_df.groupby("Month")["Actual_Consumption"]
        .mean()
        .reset_index()
    )

    st.subheader(
        "Monthly Average Consumption"
    )

    fig = px.bar(
        monthly_data,
        x="Month",
        y="Actual_Consumption",
        title="Average Monthly Water Consumption",
        labels={
            "Month": "Month",
            "Actual_Consumption": "Average Consumption"
        }
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # CONSUMPTION DISTRIBUTION

    st.subheader(
        "Water Consumption Distribution"
    )

    fig2 = px.histogram(
        df,
        x="Actual_Consumption",
        nbins=50,
        title="Distribution of Water Consumption"
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )

    # STATISTICS

    st.subheader(
        "Consumption Statistics"
    )

    stats = (
        df["Actual_Consumption"]
        .describe()
        .reset_index()
    )

    stats.columns = [
        "Statistic",
        "Value"
    ]

    st.dataframe(
        stats,
        width="stretch",
        hide_index=True
    )


# ==========================================
# 12. PAGE 5: REPORTS
# ==========================================

elif page == "Reports":

    st.title(
        "Reports & Downloads"
    )

    st.write(
        "Download integrated forecasting "
        "and anomaly detection results."
    )

    st.divider()

    st.subheader(
        "Integrated Model Report"
    )

    st.write(
        "This report contains actual consumption, "
        "predicted consumption, anomaly scores, "
        "and anomaly status."
    )

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Complete Report (CSV)",
        data=csv_data,
        file_name="AquaSense_Integrated_Report.csv",
        mime="text/csv",
        width="stretch"
    )

    st.divider()

    st.subheader(
        "Report Summary"
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Total Records",
        f"{total_records:,}"
    )

    col2.metric(
        "Anomaly Alerts",
        f"{anomaly_count:,}"
    )

    st.subheader(
        "Recent Model Results"
    )

    st.dataframe(
        df.tail(20),
        width="stretch",
        hide_index=True
    )


# ==========================================
# 13. FOOTER
# ==========================================

st.divider()

st.caption(
    "AquaSense AI | Smart Water Intelligence Platform"
)

st.caption(
    "Developed using Python, Machine Learning and Streamlit"
)
