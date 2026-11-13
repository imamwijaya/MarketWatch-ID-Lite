from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ========================================
# 1. PAGE CONFIGURATION
# ========================================

st.set_page_config(
    page_title="MarketWatch-ID Lite",
    page_icon="📈",
    layout="wide",
)


# ========================================
# 2. LOAD DATA
# ========================================

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "demo" / "detection_results.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df.sort_values("date").reset_index(drop=True)


df = load_data()



# ========================================
# 3. PROFESSIONAL DASHBOARD HEADER
# ========================================

header_left, header_right = st.columns([4, 1])

with header_left:
    st.title("MarketWatch-ID Lite")
    st.subheader("Equity Market Anomaly Surveillance")
    st.caption(
        "RULE-BASED MONITORING  |  "
        "END-OF-DAY SIMULATION  |  "
        "BBCA_DEMO"
    )

with header_right:
    st.write("")
    st.caption("SYSTEM MODE")
    st.markdown("**SYNTHETIC DEMO**")

st.info(
    "Demo environment using synthetic BBCA_DEMO data. "
    "Not actual BBCA trading records or an official IDX system."
)


# ========================================
# 4. SURVEILLANCE KPI CARDS
# ========================================

st.markdown("### Surveillance Overview")

total_obs = len(df)

total_alerts = int(
    (df["alert_type"] != "NORMAL").sum()
)

price_alerts = int(df["price_alert"].sum())
volume_alerts = int(df["volume_alert"].sum())

kpi_data = [
    {
        "label": "Observations",
        "value": total_obs,
        "description": "Synthetic OHLCV records",
    },
    {
        "label": "Unique Alerts",
        "value": total_alerts,
        "description": "Flagged observations",
    },
    {
        "label": "Price Alerts",
        "value": price_alerts,
        "description": "Absolute Z-score ≥ 3",
    },
    {
        "label": "Volume Alerts",
        "value": volume_alerts,
        "description": "Volume ratio ≥ 3x",
    },
]

kpi_columns = st.columns(4, gap="medium")

for column, item in zip(kpi_columns, kpi_data):
    with column:
        with st.container(border=True):
            st.metric(
                label=item["label"],
                value=item["value"],
            )
            st.caption(item["description"])

st.caption(
    "Combined anomalies are counted in both price and "
    "volume categories, but only once in Unique Alerts."
)



# ========================================
# 6. PRICE CHART & ANOMALY MARKERS
# ========================================

st.divider()

st.subheader("Closing Price & Anomaly Detection")

st.caption(
    "Synthetic closing prices with detected price anomalies."
)

fig = go.Figure()

# Garis harga penutupan
fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["close"],
        mode="lines",
        name="Closing Price",
        line=dict(
            color="#2563EB",
            width=2,
        ),
        hovertemplate=(
            "Date: %{x|%Y-%m-%d}<br>"
            "Close: %{y:,.2f}"
            "<extra></extra>"
        ),
    )
)

# Konfigurasi penanda anomali
alert_styles = {
    "PRICE_ONLY": {
        "name": "Price Anomaly",
        "color": "#F59E0B",
        "symbol": "circle",
    },
    "COMBINED": {
        "name": "Combined Anomaly",
        "color": "#DC2626",
        "symbol": "diamond",
    },
}

# Menambahkan titik anomali
for alert_type, style in alert_styles.items():

    subset = df.loc[
        df["alert_type"] == alert_type
    ]

    if subset.empty:
        continue

    fig.add_trace(
        go.Scatter(
            x=subset["date"],
            y=subset["close"],
            mode="markers",
            name=style["name"],
            marker=dict(
                color=style["color"],
                size=12,
                symbol=style["symbol"],
                line=dict(
                    color="white",
                    width=1.5,
                ),
            ),
            customdata=subset[
                ["price_zscore"]
            ].to_numpy(),
            hovertemplate=(
                "Date: %{x|%Y-%m-%d}<br>"
                "Close: %{y:,.2f}<br>"
                "Z-score: %{customdata[0]:.2f}"
                "<extra></extra>"
            ),
        )
    )

# Pengaturan grafik
fig.update_layout(
    height=460,
    xaxis_title="Date",
    yaxis_title="Synthetic Closing Price",
    hovermode="closest",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
    ),
    margin=dict(
        l=20,
        r=20,
        t=50,
        b=20,
    ),
)

# Tampilkan grafik
st.plotly_chart(
    fig,
    width="stretch",
    config={"displaylogo": False},
)


# ========================================
# 7. VOLUME CHART & SPIKE DETECTION
# ========================================

st.divider()

st.subheader("Trading Volume & Spike Detection")

st.caption(
    "Synthetic trading volume with detected volume spikes."
)

volume_fig = go.Figure()

# 1. Volume biasa
normal_volume = df.loc[
    ~df["alert_type"].isin(["VOLUME_ONLY", "COMBINED"])
]

volume_fig.add_trace(
    go.Bar(
        x=normal_volume["date"],
        y=normal_volume["volume"],
        name="Regular Volume",
        marker_color="#94A3B8",
        hovertemplate=(
            "Date: %{x|%Y-%m-%d}<br>"
            "Volume: %{y:,.0f}"
            "<extra></extra>"
        ),
    )
)

# 2. Volume anomaly dan combined anomaly
volume_styles = {
    "VOLUME_ONLY": {
        "name": "Volume Anomaly",
        "color": "#F59E0B",
    },
    "COMBINED": {
        "name": "Combined Anomaly",
        "color": "#DC2626",
    },
}

for alert_type, style in volume_styles.items():

    subset = df.loc[
        df["alert_type"] == alert_type
    ]

    if subset.empty:
        continue

    volume_fig.add_trace(
        go.Bar(
            x=subset["date"],
            y=subset["volume"],
            name=style["name"],
            marker_color=style["color"],
            customdata=subset["volume_ratio"],
            hovertemplate=(
                "Date: %{x|%Y-%m-%d}<br>"
                "Volume: %{y:,.0f}<br>"
                "Volume Ratio: %{customdata:.2f}x"
                "<extra></extra>"
            ),
        )
    )

# 3. Layout grafik
volume_fig.update_layout(
    height=420,
    barmode="overlay",
    xaxis_title="Date",
    yaxis_title="Synthetic Trading Volume",
    hovermode="closest",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
    ),
    margin=dict(
        l=20,
        r=20,
        t=50,
        b=20,
    ),
)

# 4. Tampilkan grafik
st.plotly_chart(
    volume_fig,
    width="stretch",
    config={"displaylogo": False},
)


# ========================================
# 8. ALERT TABLE & INTERACTIVE FILTERS
# ========================================

st.divider()

st.subheader("Anomaly Alert Monitor")

st.caption(
    "Review detected price, volume, and combined anomalies."
)

# Hanya ambil observasi yang memiliki alert
alert_df = df.loc[
    df["alert_type"] != "NORMAL"
].copy()

# ----------------------------------------
# FILTERS
# ----------------------------------------

filter_col1, filter_col2, filter_col3 = st.columns(3)

alert_options = [
    "PRICE_ONLY",
    "VOLUME_ONLY",
    "COMBINED",
]

with filter_col1:
    selected_types = st.multiselect(
        "Alert Type",
        options=alert_options,
        default=alert_options,
    )

with filter_col2:
    start_date = st.date_input(
        "Start Date",
        value=df["date"].min().date(),
        min_value=df["date"].min().date(),
        max_value=df["date"].max().date(),
    )

with filter_col3:
    end_date = st.date_input(
        "End Date",
        value=df["date"].max().date(),
        min_value=df["date"].min().date(),
        max_value=df["date"].max().date(),
    )

# ----------------------------------------
# APPLY FILTERS
# ----------------------------------------

if start_date > end_date:
    st.warning(
        "Start Date must not be later than End Date."
    )
else:
    filtered_alerts = alert_df.loc[
        alert_df["alert_type"].isin(selected_types)
        & (alert_df["date"].dt.date >= start_date)
        & (alert_df["date"].dt.date <= end_date)
    ].copy()

    # ------------------------------------
    # SUMMARY
    # ------------------------------------

    st.metric(
        "Matching Alerts",
        len(filtered_alerts),
    )

    # ------------------------------------
    # DISPLAY TABLE
    # ------------------------------------

    if filtered_alerts.empty:
        st.info(
            "No alerts match the selected filters."
        )

    else:
        display_alerts = filtered_alerts[
            [
                "date",
                "symbol",
                "close",
                "volume",
                "price_zscore",
                "volume_ratio",
                "alert_type",
            ]
        ].copy()

        display_alerts["date"] = (
            display_alerts["date"]
            .dt.strftime("%Y-%m-%d")
        )

        display_alerts["price_zscore"] = (
            display_alerts["price_zscore"].round(3)
        )

        display_alerts["volume_ratio"] = (
            display_alerts["volume_ratio"].round(3)
        )

        st.dataframe(
            display_alerts,
            width="stretch",
            hide_index=True,
        )


# ========================================
# 9. DETECTION PERFORMANCE EVALUATION
# ========================================

st.divider()

st.subheader("Detection Performance Evaluation")

st.caption(
    "Performance against injected synthetic anomaly labels."
)

# 1. Membaca ground-truth sintetis
LABEL_PATH = ROOT / "data" / "demo" / "demo_labels.csv"

labels = pd.read_csv(
    LABEL_PATH,
    parse_dates=["date"]
)

# 2. Memilih observasi dengan baseline lengkap
evaluable_mask = (
    df["evaluable"]
    .astype(str)
    .str.lower()
    .eq("true")
)

eval_df = df.loc[evaluable_mask].copy()

# 3. Menggabungkan prediksi dengan label
eval_df = eval_df.merge(
    labels[["date", "symbol", "scenario"]],
    on=["date", "symbol"],
    how="left",
    validate="one_to_one"
)

eval_df["actual"] = (
    eval_df["scenario"].fillna("NORMAL")
)

eval_df["predicted"] = eval_df["alert_type"]

# 4. Menghitung confusion matrix
actual_positive = eval_df["actual"] != "NORMAL"
predicted_positive = eval_df["predicted"] != "NORMAL"

tp = int((actual_positive & predicted_positive).sum())
fp = int((~actual_positive & predicted_positive).sum())
fn = int((actual_positive & ~predicted_positive).sum())
tn = int((~actual_positive & ~predicted_positive).sum())

# 5. Menghitung metrik
precision = tp / (tp + fp) if (tp + fp) else 0.0
recall = tp / (tp + fn) if (tp + fn) else 0.0

f1 = (
    2 * precision * recall / (precision + recall)
    if (precision + recall) else 0.0
)

labeled = eval_df.loc[actual_positive]

correct_types = int(
    (labeled["actual"] == labeled["predicted"]).sum()
)

# 6. Menampilkan KPI
metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric("Precision", f"{precision:.2%}")

with metric2:
    st.metric("Recall", f"{recall:.2%}")

with metric3:
    st.metric("F1-score", f"{f1:.2%}")

with metric4:
    st.metric(
        "Correct Anomaly Types",
        f"{correct_types}/{len(labeled)}"
    )

# 7. Menampilkan confusion matrix
st.markdown("#### Confusion Matrix")

confusion_df = pd.DataFrame(
    {
        "Predicted Normal": [tn, fn],
        "Predicted Anomaly": [fp, tp],
    },
    index=["Actual Normal", "Actual Anomaly"]
)

st.dataframe(
    confusion_df,
    width="stretch"
)

# 8. Informasi evaluasi
st.caption(
    f"Evaluated observations: {len(eval_df)} | "
    f"TP: {tp} | FP: {fp} | FN: {fn} | TN: {tn}"
)

st.info(
    "Evaluation uses synthetic data with injected anomalies. "
    "These metrics do not represent performance on real "
    "stock market surveillance."
)

# ========================================
# 10. DATA PREVIEW
# ========================================

st.divider()

st.subheader("Dataset Preview")

st.dataframe(
    df[
        [
            "date",
            "symbol",
            "close",
            "volume",
            "alert_type",
        ]
    ].tail(10),
    width="stretch",
    hide_index=True,
)

st.caption(
    "Displaying the latest 10 observations."
)