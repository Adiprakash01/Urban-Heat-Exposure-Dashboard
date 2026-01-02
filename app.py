import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import folium
from folium.plugins import HeatMap, MiniMap
import streamlit.components.v1 as components

# -----------------------------------------
# FORCE TIMES NEW ROMAN (PLOTS)
# -----------------------------------------
mpl.rcParams["font.family"] = "Times New Roman"
mpl.rcParams["axes.titlesize"] = 14
mpl.rcParams["axes.labelsize"] = 12
mpl.rcParams["xtick.labelsize"] = 10
mpl.rcParams["ytick.labelsize"] = 10
mpl.rcParams["legend.fontsize"] = 10

# -----------------------------------------
# PAGE CONFIG
# -----------------------------------------
st.set_page_config(
    page_title="Global Urban Heat Exposure",
    layout="wide"
)

# -----------------------------------------
# FORCE TIMES NEW ROMAN (STREAMLIT UI)
# -----------------------------------------
st.markdown(
    """
    <style>
    html, body, [class*="css"], div, span, p, label {
        font-family: "Times New Roman", Times, serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------
# LOAD DATA
# -----------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "global_urban_heat_daily_temperature_2024_2025.csv",
        parse_dates=["Date"]
    )
    df.loc[df["Temperature_C"] <= -900, "Temperature_C"] = pd.NA
    return df.dropna(subset=["Temperature_C"])

df = load_data()

# -----------------------------------------
# LOCATIONS (GLOBAL)
# -----------------------------------------
df_locations = pd.DataFrame({
    "Area": ["Mumbai", "Dubai", "Singapore", "London", "New York", "Sydney"],
    "Latitude": [19.0760, 25.2048, 1.3521, 51.5074, 40.7128, -33.8688],
    "Longitude": [72.8777, 55.2708, 103.8198, -0.1278, -74.0060, 151.2093]
})

# -----------------------------------------
# FEATURE ENGINEERING
# -----------------------------------------
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

# -----------------------------------------
# HEADER
# -----------------------------------------
st.markdown("<h1>🌍 Global Urban Heat Exposure Dashboard</h1>", unsafe_allow_html=True)

st.markdown(
    """
    Comparative analysis of urban heat exposure across global cities using
    **NASA POWER daily temperature reanalysis data (2024–2025)**.
    """
)

# -----------------------------------------
# SIDEBAR
# -----------------------------------------
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

# -----------------------------------------
# FILTER DATA
# -----------------------------------------
filtered_df = df[df["Area"] == selected_city]
if selected_period != "Full Year":
    filtered_df = filtered_df[filtered_df["Season"] == selected_period]

metric_col = "Heat_Exposure_Index" if show_index else "Temperature_C"

# -----------------------------------------
# METRICS
# -----------------------------------------
avg_temp = df.groupby("Area")["Temperature_C"].mean().reset_index()
global_avg = avg_temp["Temperature_C"].mean()

c1, c2, c3 = st.columns(3)
c1.metric("🔥 Hottest City", avg_temp.loc[avg_temp["Temperature_C"].idxmax(), "Area"])
c2.metric("❄️ Coolest City", avg_temp.loc[avg_temp["Temperature_C"].idxmin(), "Area"])
c3.metric("🌡️ Global Avg Temp", f"{global_avg:.2f} °C")

# -----------------------------------------
# TABS
# -----------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Trends", "🗺️ Map", "📊 Distribution", "🔥 Ranking"]
)

# -----------------------------------------
# TAB 1: CITY-WISE TRENDS
# -----------------------------------------
with tab1:
    cities = df["Area"].unique()
    n_rows = (len(cities) + 1) // 2

    fig, axes = plt.subplots(n_rows, 2, figsize=(16, 4 * n_rows))
    axes = axes.flatten()

    for i, city in enumerate(cities):
        city_df = df[df["Area"] == city]
        axes[i].plot(city_df["Date"], city_df[metric_col])
        axes[i].set_title(city)
        axes[i].set_ylabel("°C")
        axes[i].grid(alpha=0.3)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    st.pyplot(fig)

# -----------------------------------------
# TAB 2: MAP WITH MINI-MAP + CLEAN POPUPS
# -----------------------------------------
with tab2:
    m = folium.Map(location=[20, 0], zoom_start=2)

    # Mini map for context
    MiniMap(toggle_display=True, position="bottomright").add_to(m)

    map_data = avg_temp.merge(df_locations, on="Area")

    for _, row in map_data.iterrows():
        deviation = row["Temperature_C"] - global_avg
        color = "red" if deviation > 0 else "blue"

        popup_html = f"""
        <div style="
            width:220px;
            font-family:'Times New Roman';
            line-height:1.6;
        ">
            <h4 style="margin-bottom:8px;">{row['Area']}</h4>
            <b>Average Temperature:</b><br>
            {row['Temperature_C']:.2f} °C<br><br>
            <b>Heat Exposure Index:</b><br>
            {deviation:+.2f} °C
        </div>
        """

        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=14,
            color=color,
            fill=True,
            fill_opacity=0.8,
            popup=popup_html
        ).add_to(m)

    HeatMap(
        [
            [r["Latitude"], r["Longitude"], r["Temperature_C"]]
            for _, r in map_data.iterrows()
        ],
        radius=30,
        blur=18
    ).add_to(m)

    components.html(m._repr_html_(), height=550)

# -----------------------------------------
# TAB 3: DISTRIBUTION (BOX + HIST + PIE)
# -----------------------------------------
with tab3:
    st.subheader("Temperature Distribution & Seasonal Share")

    # Box plot
    fig, ax = plt.subplots(figsize=(8,5))
    df.boxplot(column="Temperature_C", by="Area", ax=ax)
    ax.set_title("Temperature Variability by City")
    plt.suptitle("")
    st.pyplot(fig)

    # Histogram
    fig, ax = plt.subplots()
    ax.hist(filtered_df["Temperature_C"], bins=20, edgecolor="black")
    ax.set_title(f"{selected_city} – Temperature Frequency")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Number of Days")
    st.pyplot(fig)

    # Pie chart
    seasonal_sum = filtered_df.groupby("Season")["Temperature_C"].sum()
    fig, ax = plt.subplots()
    ax.pie(
        seasonal_sum,
        labels=seasonal_sum.index,
        autopct="%1.1f%%",
        startangle=90
    )
    ax.set_title(f"{selected_city} – Seasonal Contribution")
    st.pyplot(fig)

# -----------------------------------------
# TAB 4: HEAT RANKING
# -----------------------------------------
with tab4:
    ranking = avg_temp.sort_values(
        "Temperature_C", ascending=False
    ).reset_index(drop=True)
    ranking.index += 1
    st.dataframe(ranking, use_container_width=True)

# -----------------------------------------
# DOWNLOAD
# -----------------------------------------
st.markdown("---")
st.download_button(
    "⬇️ Download Dataset (CSV)",
    df.to_csv(index=False),
    "global_urban_heat_daily_temperature_2024_2025.csv",
    "text/csv"
)

st.caption("Data Source: NASA POWER API | Global Geospatial Analytics using Streamlit")
