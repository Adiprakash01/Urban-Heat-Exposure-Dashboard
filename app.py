import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import folium
from folium.plugins import HeatMap, MiniMap
import streamlit.components.v1 as components
import warnings

warnings.filterwarnings("ignore")

mpl.rcParams["font.family"] = "serif"
mpl.rcParams["font.serif"] = [
    "Times New Roman",
    "Liberation Serif",
    "DejaVu Serif",
    "serif"
]
mpl.rcParams["axes.titlesize"] = 14
mpl.rcParams["axes.labelsize"] = 12

# PAGE CONFIG
st.set_page_config(
    page_title="Global Urban Heat Exposure Dashboard",
    layout="wide")

# FORCE TIMES NEW ROMAN (UI + HEADINGS) – EMBED FONT
st.markdown(
    """
    <style>
    @font-face {
        font-family: 'Times New Roman';
        src: local('Times New Roman'), local('TimesNewRoman');
    }

    html, body, [class*="css"] {
        font-family: 'Times New Roman', Times, serif !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Times New Roman', Times, serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# LOAD DATA
@st.cache_data
def load_data():
    df = pd.read_csv(
        "global_urban_heat_daily_temperature_2024_2025.csv",
        parse_dates=["Date"]
    )
    df.loc[df["Temperature_C"] <= -900, "Temperature_C"] = pd.NA
    df = df.dropna(subset=["Temperature_C"])
    return df

df = load_data()

# LOCATIONS
df_locations = pd.DataFrame({
    "Area": ["Mumbai", "Dubai", "Singapore", "London", "New York", "Sydney"],
    "Latitude": [19.0760, 25.2048, 1.3521, 51.5074, 40.7128, -33.8688],
    "Longitude": [72.8777, 55.2708, 103.8198, -0.1278, -74.0060, 151.2093]
})

# FEATURE ENGINEERING

df["Month"] = df["Date"].dt.month
df["Season"] = df["Month"].apply(
    lambda x: "Summer" if x in [6,7,8]
    else "Winter" if x in [12,1,2]
    else "Transition"
)

df["Heat_Exposure_Index"] = (
    df["Temperature_C"] -
    df.groupby("Area")["Temperature_C"].transform("mean")
)

# HEADER

st.markdown("<h1>🌍 Global Urban Heat Exposure Dashboard</h1>", unsafe_allow_html=True)

st.markdown(
    """
    This dashboard provides a **comparative geospatial and temporal analysis of urban heat exposure**
    across globally distributed cities using **NASA POWER daily temperature reanalysis data (2024–2025)**.

    The study highlights how **climatic location, latitude, and seasonal variation** influence
    urban thermal behaviour. A **Heat Exposure Index (HEI)** is used for temporal comparison within cities,
    while **absolute temperature values** are preserved for spatial interpretation.

    This dual-approach ensures methodological clarity and avoids misinterpretation of spatial heat patterns.
    """
)

# SIDEBAR
st.sidebar.header("User Controls")

selected_city = st.sidebar.selectbox(
    "Select City",
    sorted(df["Area"].unique())
)

selected_period = st.sidebar.radio(
    "Select Time Period",
    ["Full Year", "Summer", "Winter", "Transition"]
)

show_index = st.sidebar.checkbox("Show Heat Exposure Index")

# FILTER DATA

filtered_df = df[df["Area"] == selected_city]
if selected_period != "Full Year":
    filtered_df = filtered_df[filtered_df["Season"] == selected_period]

metric_col = "Heat_Exposure_Index" if show_index else "Temperature_C"

# METRICS

avg_temp = df.groupby("Area")["Temperature_C"].mean().reset_index()
global_avg = avg_temp["Temperature_C"].mean()

hottest = avg_temp.loc[avg_temp["Temperature_C"].idxmax()]
coolest = avg_temp.loc[avg_temp["Temperature_C"].idxmin()]

c1, c2, c3 = st.columns(3)
c1.metric("🔥 Hottest City", hottest["Area"])
c2.metric("❄️ Coolest City", coolest["Area"])
c3.metric("🌡️ Global Avg Temp", f"{global_avg:.2f} °C")

# TABS
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Trends", "🗺️ Global Map", "📊 Distribution", "🔥 Ranking"]
)

# TAB 1: TRENDS
with tab1:
    st.subheader("Daily Temperature Trends (One Plot per City)")
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    axes = axes.flatten()

    for i, city in enumerate(df["Area"].unique()):
        city_df = df[df["Area"] == city]
        if selected_period != "Full Year":
            city_df = city_df[city_df["Season"] == selected_period]

        axes[i].plot(city_df["Date"], city_df[metric_col])
        axes[i].set_title(city)
        axes[i].set_ylabel("°C")
        axes[i].grid(alpha=0.3)

    st.pyplot(fig)

# TAB 2: GLOBAL MAP (UNCHANGED)
with tab2:
    st.subheader("Global Spatial Temperature Distribution")

    if show_index:
        st.info(
            "ℹ️ Spatial maps always display **absolute temperature values**. "
            "Heat Exposure Index is used only for temporal analysis."
        )

    m = folium.Map(location=[20, 0], zoom_start=2)
    map_data = avg_temp.merge(df_locations, on="Area")

    for _, row in map_data.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=12,
            color="red" if row["Temperature_C"] > global_avg else "blue",
            fill=True,
            fill_opacity=0.75,
            popup=f"""
            <b>{row['Area']}</b><br>
            Avg Temp: {row['Temperature_C']:.2f} °C<br>
            Deviation: {(row['Temperature_C'] - global_avg):+.2f} °C
            """
        ).add_to(m)

    HeatMap(
        [[r["Latitude"], r["Longitude"], r["Temperature_C"]] for _, r in map_data.iterrows()],
        radius=30, blur=18
    ).add_to(m)

    MiniMap(toggle_display=True).add_to(m)
    components.html(m._repr_html_(), height=520)

# TAB 3: DISTRIBUTION 
with tab3:
    st.subheader("Temperature Distribution & Seasonal Share")

    fig, ax = plt.subplots(figsize=(6,4))
    ax.hist(filtered_df["Temperature_C"], bins=15, edgecolor="black")
    ax.set_title(f"{selected_city} – Temperature Frequency")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Number of Days")
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(7,4))
    city_data = [
        df[
            (df["Area"] == city) &
            ((df["Season"] == selected_period) if selected_period != "Full Year" else True)
        ]["Temperature_C"]
        for city in df["Area"].unique()
    ]
    ax.boxplot(city_data, tick_labels=df["Area"].unique())
    ax.set_title("Temperature Variability by City")
    ax.set_ylabel("Temperature (°C)")
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(4.5,4.5))
    season_share = filtered_df["Season"].value_counts()
    ax.pie(season_share, labels=season_share.index, autopct="%1.1f%%")
    ax.set_title("Seasonal Share")
    st.pyplot(fig)

# TAB 4: RANKING
with tab4:
    ranking = avg_temp.sort_values("Temperature_C", ascending=False).reset_index(drop=True)
    ranking.index += 1
    st.dataframe(ranking, use_container_width=True)

# DOWNLOAD
st.markdown("---")
st.download_button(
    "⬇️ Download Dataset (CSV)",
    df.to_csv(index=False),
    "global_urban_heat_daily_temperature_2024_2025.csv",
    "text/csv"
)

st.caption("Data Source: NASA POWER API | Global Geospatial Analytics using Streamlit")
