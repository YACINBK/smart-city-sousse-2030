import hashlib
import os

import folium
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from streamlit_folium import st_folium

from smartcity_backend.api.constants import DEFAULT_DISTRICT, DISTRICT_CENTERS, MAP_CENTER, MAP_ZOOM


API_URL = os.environ.get("SMARTCITY_API_URL", "http://127.0.0.1:8000/api").rstrip("/") + "/"
REQUEST_TIMEOUT = 5

STATUS_FOLIUM_COLORS = {
    "actif": "green",
    "en_maintenance": "orange",
    "hors_service": "red",
}
STATUS_HEX_COLORS = {
    "actif": "#00cc96",
    "en_maintenance": "#ffa15a",
    "hors_service": "#ef553b",
}
STATUS_LABELS = {
    "actif": "Actif",
    "en_maintenance": "En maintenance",
    "hors_service": "Hors service",
}
SENSOR_ICONS = {
    "qualité_air": "leaf",
    "trafic": "road",
    "énergie": "bolt",
    "déchets": "trash",
    "éclairage": "lightbulb",
}
DISTRICT_ALIASES = {
    "medina": "Sousse Ville",
    "la medina": "Sousse Ville",
    "jawhara": "Sousse Jawhara",
    "riadh": "Sousse Riadh",
    "cité riadh": "Sousse Riadh",
    "cite riadh": "Sousse Riadh",
    "ksiba": "Zaouia Ksiba Thrayet",
    "zaouia": "Zaouia Ksiba Thrayet",
    "thrayet": "Zaouia Ksiba Thrayet",
}


st.set_page_config(page_title="Smart City Sousse", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background: #17181d;
            color: #f5f5f5;
        }
        [data-testid="stHeader"] {
            background: #17181d;
        }
        [data-testid="stSidebar"] {
            display: none;
        }
        .main .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 95rem;
        }
        h1, h2, h3, p, div, span, label {
            color: #f5f5f5;
        }
        .metric-card {
            background-color: #262730;
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid #4b4f59;
            text-align: center;
            min-height: 96px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #00cc96;
            line-height: 1.1;
        }
        .metric-label {
            margin-top: 0.35rem;
            font-size: 0.95rem;
            color: #d6d6d6;
        }
        .metric-note {
            margin-top: 0.35rem;
            color: #9ca3af;
            font-size: 0.82rem;
        }
        .subtle-copy {
            color: #b3b3b3;
            font-size: 0.95rem;
        }
        .stButton > button {
            background: #252e3b;
            color: #f5f5f5;
            border: 1px solid #4b5563;
            border-radius: 10px;
            min-height: 2.8rem;
            padding: 0.5rem 0.9rem;
            font-weight: 600;
        }
        .stButton > button:hover {
            border-color: #7c8799;
            color: #ffffff;
        }
        .stButton > button:focus {
            box-shadow: none;
            border-color: #7c8799;
        }
        [data-testid="stDataFrame"] {
            border: 1px solid #31333f;
            border-radius: 10px;
            overflow: hidden;
        }
        hr {
            border-color: #31333f;
        }
        div[data-baseweb="tab-list"] {
            gap: 0.6rem;
            border-bottom: 1px solid #31333f;
            padding-bottom: 0.3rem;
        }
        button[data-baseweb="tab"] {
            background: transparent;
            border: none;
            border-radius: 0;
            color: #c9d1d9;
            padding: 0.2rem 0;
            margin-right: 0.8rem;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #ff4b4b;
            border-bottom: 2px solid #ff4b4b;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def ensure_columns(dataframe, columns):
    dataframe = dataframe.copy()
    for column in columns:
        if column not in dataframe.columns:
            dataframe[column] = pd.Series(dtype="object")
    return dataframe


def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def stable_index(value, step, modulo):
    digest = hashlib.sha256(f"{value}:{step}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % modulo


def resolve_district_from_text(text):
    lowered = str(text).lower()
    for alias, district in DISTRICT_ALIASES.items():
        if alias in lowered:
            return district
    for district in DISTRICT_CENTERS:
        if district.lower() in lowered:
            return district
    return DEFAULT_DISTRICT


def apply_dark_chart_theme(figure, height=420, horizontal_legend=False):
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="#17181d",
        plot_bgcolor="#17181d",
        font=dict(color="#f5f5f5", size=13),
        margin=dict(l=18, r=18, t=60, b=18),
        height=height,
        legend=(
            dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                title=None,
            )
            if horizontal_legend
            else dict(title=None)
        ),
    )
    figure.update_xaxes(gridcolor="#31333f", zerolinecolor="#31333f")
    figure.update_yaxes(gridcolor="#31333f", zerolinecolor="#31333f")
    return figure


@st.cache_data(ttl=5, show_spinner=False)
def fetch_resource(endpoint):
    response = requests.get(f"{API_URL}{endpoint}/", timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, list):
        return pd.DataFrame(payload)
    return pd.DataFrame([payload])


def load_datasets():
    datasets = {}
    for endpoint in ("capteurs", "interventions", "citoyens", "trajets", "vehicules"):
        try:
            datasets[endpoint] = fetch_resource(endpoint)
        except requests.RequestException as exc:
            st.error(f"Impossible de charger '{endpoint}' depuis l'API: {exc}")
            datasets[endpoint] = pd.DataFrame()
    return datasets


def prepare_dataframes(datasets):
    capteurs = ensure_columns(
        datasets["capteurs"],
        ["id_capteur", "type_capteur", "latitude", "longitude", "statut", "quartier"],
    )
    interventions = ensure_columns(
        datasets["interventions"],
        ["cout", "date_heure", "type_intervention"],
    )
    citoyens = ensure_columns(
        datasets["citoyens"],
        ["nom", "email", "preferences_mobilite", "score_ecologique"],
    )
    trajets = ensure_columns(
        datasets["trajets"],
        ["origine", "destination", "duree", "economie_co2"],
    )
    vehicules = ensure_columns(
        datasets["vehicules"],
        ["plaque_immatriculation"],
    )

    if not capteurs.empty:
        capteurs["latitude"] = safe_numeric(capteurs["latitude"])
        capteurs["longitude"] = safe_numeric(capteurs["longitude"])

    if not interventions.empty:
        interventions["cout"] = safe_numeric(interventions["cout"])
        interventions["date_heure"] = pd.to_datetime(interventions["date_heure"], errors="coerce")

    if not citoyens.empty:
        citoyens["score_ecologique"] = safe_numeric(citoyens["score_ecologique"])

    if not trajets.empty:
        trajets["economie_co2"] = safe_numeric(trajets["economie_co2"])

    return capteurs, interventions, citoyens, trajets, vehicules


def metric_card(value, label, note=""):
    note_html = f'<div class="metric-note">{note}</div>' if note else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_top_bar(capteurs, interventions, citoyens, trajets):
    col1, col2, col3, col4 = st.columns(4)

    active_sensors = capteurs[capteurs["statut"] == "actif"].shape[0] if not capteurs.empty else 0
    total_sensors = capteurs.shape[0] if not capteurs.empty else 0
    maintenance_cost = interventions["cout"].sum() if not interventions.empty else 0
    ecological_score = citoyens["score_ecologique"].mean() if not citoyens.empty else 0
    saved_co2 = trajets["economie_co2"].sum() if not trajets.empty else 0

    with col1:
        metric_card(f"{active_sensors}/{total_sensors}", "Capteurs Actifs")
    with col2:
        metric_card(f"{maintenance_cost:,.0f} TND", "Coût Maintenance (Annuel)")
    with col3:
        metric_card(f"{ecological_score:.1f}", "Score Écologique Moyen")
    with col4:
        metric_card(f"{saved_co2:,.1f} kg", "CO2 Économisé (Trajets)")


def display_map(capteurs, vehicules, simulation_step):
    city_map = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles="CartoDB dark_matter")

    if not capteurs.empty:
        for _, row in capteurs.iterrows():
            if pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
                continue

            popup = (
                f"<b>Type:</b> {row['type_capteur']}<br>"
                f"<b>Statut:</b> {STATUS_LABELS.get(row['statut'], row['statut'])}<br>"
                f"<b>Quartier:</b> {row['quartier']}"
            )
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                tooltip=popup,
                icon=folium.Icon(
                    color=STATUS_FOLIUM_COLORS.get(row["statut"], "blue"),
                    icon=SENSOR_ICONS.get(row["type_capteur"], "info-circle"),
                    prefix="fa",
                ),
            ).add_to(city_map)

    if not vehicules.empty:
        districts = list(DISTRICT_CENTERS.keys())
        for _, row in vehicules.iterrows():
            district = districts[stable_index(row["plaque_immatriculation"], simulation_step, len(districts))]
            base_lat, base_lon = DISTRICT_CENTERS[district]
            lat_shift = (stable_index(f"{row['plaque_immatriculation']}:lat", simulation_step, 100) - 50) / 8000
            lon_shift = (stable_index(f"{row['plaque_immatriculation']}:lon", simulation_step, 100) - 50) / 8000
            folium.Marker(
                location=[base_lat + lat_shift, base_lon + lon_shift],
                tooltip=f"Véhicule {row['plaque_immatriculation']}",
                icon=folium.Icon(color="blue", icon="car", prefix="fa"),
            ).add_to(city_map)

    st_folium(city_map, height=500, use_container_width=True, returned_objects=[])


def display_zone_table(capteurs):
    if capteurs.empty:
        st.info("Aucune donnée capteur disponible.")
        return

    total_counts = capteurs.groupby("quartier").size().reset_index(name="total")
    failure_counts = (
        capteurs[capteurs["statut"] != "actif"].groupby("quartier").size().reset_index(name="failed")
    )
    merged = total_counts.merge(failure_counts, on="quartier", how="left").fillna(0)
    merged["failure_rate"] = merged["failed"] / merged["total"]
    merged = merged.sort_values("failure_rate", ascending=False)
    merged["Taux Panne"] = (merged["failure_rate"] * 100).round(0).astype(int).astype(str) + "%"

    st.dataframe(
        merged[["quartier", "Taux Panne"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "quartier": "Zone",
            "Taux Panne": st.column_config.TextColumn("Taux Panne"),
        },
    )


def display_pollution_tab(capteurs):
    st.caption("Ces statistiques représentent les dernières 24 heures.")
    air_sensors = capteurs[capteurs["type_capteur"] == "qualité_air"].copy()
    if air_sensors.empty:
        st.info("Aucun capteur de qualité de l'air disponible.")
        return

    def simulate_aqi(row):
        base = 50
        if row["quartier"] == "Sousse Ville":
            base = 120
        elif row["quartier"] == "Sousse Riadh":
            base = 100
        return base + stable_index(row["id_capteur"], 0, 41) - 20

    air_sensors["AQI"] = air_sensors.apply(simulate_aqi, axis=1)
    district_aqi = air_sensors.groupby("quartier", as_index=False)["AQI"].mean().sort_values("AQI", ascending=False)
    figure = px.bar(
        district_aqi,
        x="quartier",
        y="AQI",
        color="AQI",
        title="Indice AQI moyen par quartier",
        color_continuous_scale="RdYlGn_r",
    )
    st.plotly_chart(apply_dark_chart_theme(figure, height=460), use_container_width=True)


def display_availability_tab(capteurs):
    if capteurs.empty:
        st.info("Aucune donnée capteur disponible.")
        return

    col1, col2 = st.columns([1, 2])

    with col1:
        global_status = capteurs.groupby("statut").size().reset_index(name="count")
        donut = px.pie(
            global_status,
            values="count",
            names="statut",
            title="État Global",
            hole=0.4,
            color="statut",
            color_discrete_map=STATUS_HEX_COLORS,
        )
        donut.update_traces(textinfo="percent")
        st.plotly_chart(apply_dark_chart_theme(donut, height=420), use_container_width=True)

    with col2:
        availability = capteurs.groupby(["quartier", "statut"]).size().reset_index(name="count")
        totals = capteurs.groupby("quartier").size().reset_index(name="total")
        availability = availability.merge(totals, on="quartier")
        availability["percentage"] = (availability["count"] / availability["total"] * 100).round(1)

        active_rows = availability[availability["statut"] == "actif"]
        district_order = active_rows.sort_values("percentage", ascending=False)["quartier"].tolist()
        for district in availability["quartier"].unique().tolist():
            if district not in district_order:
                district_order.append(district)

        stacked = px.bar(
            availability,
            x="quartier",
            y="percentage",
            color="statut",
            title="Détail par Arrondissement (%)",
            text="percentage",
            category_orders={"quartier": district_order},
            color_discrete_map=STATUS_HEX_COLORS,
        )
        stacked.update_traces(texttemplate="%{text}%", textposition="inside")
        st.plotly_chart(apply_dark_chart_theme(stacked, height=420), use_container_width=True)


def display_citizens_tab(citoyens):
    if citoyens.empty:
        st.info("Aucune donnée citoyen disponible.")
        return

    top_citizens = citoyens.sort_values("score_ecologique", ascending=False).drop_duplicates(subset=["nom"]).head(10)
    figure = px.bar(
        top_citizens.sort_values("score_ecologique", ascending=True),
        x="score_ecologique",
        y="nom",
        orientation="h",
        color="score_ecologique",
        title="Classement (Score Écologique)",
        color_continuous_scale="Teal",
    )
    st.plotly_chart(apply_dark_chart_theme(figure, height=380), use_container_width=True)
    st.dataframe(
        top_citizens[["nom", "email", "preferences_mobilite", "score_ecologique"]],
        use_container_width=True,
        hide_index=True,
    )


def display_interventions_tab(interventions):
    if interventions.empty:
        st.info("Aucune intervention disponible.")
        return

    predictive = interventions[interventions["type_intervention"] == "prédictive"].copy()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Nombre (Prédictif)", predictive.shape[0])
    with col2:
        st.metric("Gain Est.", f"{predictive['cout'].sum() * 1.5:,.0f} TND")

    if predictive.empty:
        return

    predictive["date"] = predictive["date_heure"].dt.date
    daily_cost = predictive.groupby("date", as_index=False)["cout"].sum()
    figure = px.line(
        daily_cost,
        x="date",
        y="cout",
        title="Tendances des Coûts",
    )
    figure.update_traces(line_color="#7cc0ff", line_width=3)
    st.plotly_chart(apply_dark_chart_theme(figure, height=420), use_container_width=True)


def display_trips_tab(trajets, top_n=5):
    if trajets.empty:
        st.info("Aucun trajet disponible.")
        return

    top_trips = trajets.sort_values("economie_co2", ascending=False).head(top_n).copy()
    st.dataframe(
        top_trips[["origine", "destination", "duree", "economie_co2"]],
        use_container_width=True,
        hide_index=False,
    )

    trip_map = folium.Map(location=[35.83, 10.61], zoom_start=11, tiles="CartoDB dark_matter")
    route_colors = ["green", "lime", "yellow", "orange", "red"]

    for index, (_, row) in enumerate(top_trips.iterrows()):
        origin_district = resolve_district_from_text(row["origine"])
        destination_district = resolve_district_from_text(row["destination"])

        start_lat, start_lon = DISTRICT_CENTERS[origin_district]
        end_lat, end_lon = DISTRICT_CENTERS[destination_district]

        start_lat += (stable_index(f"{row['origine']}:start_lat", 0, 100) - 50) / 7000
        start_lon += (stable_index(f"{row['origine']}:start_lon", 0, 100) - 50) / 7000
        end_lat += (stable_index(f"{row['destination']}:end_lat", 0, 100) - 50) / 7000
        end_lon += (stable_index(f"{row['destination']}:end_lon", 0, 100) - 50) / 7000

        folium.Marker(
            [start_lat, start_lon],
            tooltip=f"Départ: {row['origine']}",
            icon=folium.Icon(color="green", icon="play", prefix="fa"),
        ).add_to(trip_map)
        folium.Marker(
            [end_lat, end_lon],
            tooltip=f"Arrivée: {row['destination']}",
            icon=folium.Icon(color="red", icon="stop", prefix="fa"),
        ).add_to(trip_map)
        folium.PolyLine(
            [(start_lat, start_lon), (end_lat, end_lon)],
            color=route_colors[index % len(route_colors)],
            weight=4,
            tooltip=f"Trajet {index + 1}: {row['economie_co2']} kg CO2",
        ).add_to(trip_map)

    st_folium(trip_map, height=400, use_container_width=True, returned_objects=[])


def display_analytics(capteurs, interventions, citoyens, trajets):
    st.subheader("Analyses Approfondies")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Pollution", "Disponibilité", "Citoyens", "Interventions", "Trajets"]
    )

    with tab1:
        display_pollution_tab(capteurs)
    with tab2:
        display_availability_tab(capteurs)
    with tab3:
        display_citizens_tab(citoyens)
    with tab4:
        display_interventions_tab(interventions)
    with tab5:
        display_trips_tab(trajets)


def trigger_simulation():
    try:
        response = requests.post(f"{API_URL}simulate/", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        fetch_resource.clear()
        st.session_state.sim_step += 1
        st.rerun()
    except requests.RequestException as exc:
        st.error(f"Échec du déclenchement de la simulation: {exc}")


def main():
    if "sim_step" not in st.session_state:
        st.session_state.sim_step = 0

    datasets = load_datasets()
    capteurs, interventions, citoyens, trajets, vehicules = prepare_dataframes(datasets)

    st.title("Smart City Sousse")
    button_col, info_col = st.columns([1, 4])
    with button_col:
        if st.button("Actualiser (Smart Sim)", use_container_width=True):
            trigger_simulation()
    with info_col:
        st.markdown('<div class="subtle-copy">Tableau de bord Smart City pour le gouvernorat de Sousse.</div>', unsafe_allow_html=True)

    st.write("")
    display_top_bar(capteurs, interventions, citoyens, trajets)
    st.divider()

    map_col, zone_col = st.columns([3, 1])
    with map_col:
        st.subheader("Carte en Temps Réel (Gouvernorat de Sousse)")
        display_map(capteurs, vehicules, st.session_state.sim_step)
    with zone_col:
        st.subheader("État des Zones")
        display_zone_table(capteurs)

    st.divider()
    display_analytics(capteurs, interventions, citoyens, trajets)


if __name__ == "__main__":
    main()
