import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import plotly.express as px
import plotly.graph_objects as go
import random

# Configuration
API_URL = "http://127.0.0.1:8000/api/"
st.set_page_config(page_title="Smart City Sousse", layout="wide")

# --- CSS Styling ---
# Anchors for valid land placement (Vehicles)
DISTRICT_ANCHORS = [
    (35.8245, 10.6345), # Medina
    (35.8360, 10.5900), # Sahloul
    (35.8450, 10.6200), # Khezama
    (35.8180, 10.5500), # Kalaa Sghira
    (35.8550, 10.6050), # Hammam Sousse
    (35.8050, 10.6100), # Cité Riadh
]

st.markdown("""
<style>
    .metric-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #333;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #00d2ff;
    }
    .metric-label {
        font-size: 14px;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Fetching ---
@st.cache_data(ttl=60) # Refresh every 60 seconds
def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}/")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error(f"Failed to fetch {endpoint}: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return pd.DataFrame()

# --- Load Data ---
st.title("🏙️ Smart City Sousse - Analytics Platform")
st.markdown("Real-time monitoring of **Neo-Sousse 2030**")

col1, col2, col3, col4 = st.columns(4)

df_sensors = fetch_data("capteurs")
df_interventions = fetch_data("interventions")
df_citizens = fetch_data("citoyens")
df_trips = fetch_data("trajets")
df_vehicles = fetch_data("vehicules")

# --- Data Type Conversions ---
if not df_interventions.empty:
    df_interventions['cout'] = pd.to_numeric(df_interventions['cout'], errors='coerce').fillna(0)
    df_interventions['impact_co2'] = pd.to_numeric(df_interventions['impact_co2'], errors='coerce').fillna(0)
    df_interventions['duree'] = pd.to_numeric(df_interventions['duree'], errors='coerce').fillna(0)

if not df_trips.empty:
    df_trips['economie_co2'] = pd.to_numeric(df_trips['economie_co2'], errors='coerce').fillna(0)

if not df_citizens.empty:
    df_citizens['score_ecologique'] = pd.to_numeric(df_citizens['score_ecologique'], errors='coerce').fillna(0)

if not df_sensors.empty:
    df_sensors['latitude'] = pd.to_numeric(df_sensors['latitude'], errors='coerce')
    df_sensors['longitude'] = pd.to_numeric(df_sensors['longitude'], errors='coerce')

# --- Key Metrics ---
with col1:
    if not df_sensors.empty:
        active_sensors = df_sensors[df_sensors['statut'] == 'actif'].shape[0]
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{active_sensors}/{df_sensors.shape[0]}</div><div class="metric-label">Capteurs Actifs</div></div>""", unsafe_allow_html=True)

with col2:
    if not df_interventions.empty:
        total_cost = df_interventions['cout'].sum()
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{total_cost:,.0f} TND</div><div class="metric-label">Coût Maintenance (Annuel)</div></div>""", unsafe_allow_html=True)

with col3:
    if not df_citizens.empty:
        avg_score = df_citizens['score_ecologique'].mean()
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{avg_score:.1f}</div><div class="metric-label">Score Écologique Moyen</div></div>""", unsafe_allow_html=True)

with col4:
    if not df_trips.empty:
        total_co2 = df_trips['economie_co2'].sum()
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{total_co2:,.1f} kg</div><div class="metric-label">CO2 Économisé (Trajets)</div></div>""", unsafe_allow_html=True)

st.divider()

# --- 1. Map Visualization (Sousse) ---
st.subheader("📍 Carte en Temps Réel (Sousse)")

m = folium.Map(location=[35.8300, 10.6100], zoom_start=14, tiles="CartoDB dark_matter")

# Add Sensors
if not df_sensors.empty:
    for _, row in df_sensors.iterrows():
        color = "green" if row['statut'] == 'actif' else "red" if row['statut'] == 'hors_service' else "orange"
        color = "green" if row['statut'] == 'actif' else "red" if row['statut'] == 'hors_service' else "orange"
        
        # Unique icons for each type
        if row['type_capteur'] == 'qualité_air':
            icon = "leaf"
        elif row['type_capteur'] == 'trafic':
            icon = "road"
        elif row['type_capteur'] == 'énergie':
            icon = "bolt"
        elif row['type_capteur'] == 'déchets':
            icon = "trash"
        elif row['type_capteur'] == 'éclairage':
            icon = "lightbulb"
        else:
            icon = "info-circle"
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            tooltip=f"<b>Type:</b> {row['type_capteur']}<br><b>Statut:</b> {row['statut']}<br><b>ID:</b> {row['id_capteur']}",
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(m)

# Add Simulated Vehicles (Random movement simulation for 'Real-time' feel)
if not df_vehicles.empty:
    for _, row in df_vehicles.iterrows():
        # Pick a random district anchor + small offset to ensure LAND placement
        anchor = random.choice(DISTRICT_ANCHORS)
        lat = anchor[0] + random.uniform(-0.005, 0.005)
        lon = anchor[1] + random.uniform(-0.005, 0.005)
        
        folium.Marker(
            location=[lat, lon],
            tooltip=f"Véhicule {row['plaque_immatriculation']}",
            icon=folium.Icon(color="blue", icon="car", prefix="fa")
        ).add_to(m)

st_folium(m, width=1200, height=350, returned_objects=[])

# --- 2. Business Questions & Analytics ---
st.divider()
st.subheader("📊 Analyses & Rapports")

tab1, tab2, tab3 = st.tabs(["🌍 Environnement & Capteurs", "🔧 Maintenance & Coûts", "👥 Citoyens & Mobilité"])

with tab1:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### Zones les plus polluées (24h)")
        # Simulation: Assign random AQI to air sensors
        if not df_sensors.empty:
            air_sensors = df_sensors[df_sensors['type_capteur'] == 'qualité_air'].copy()
            if not air_sensors.empty:
                # Group by Quartier to show regional quality
                air_sensors['AQI'] = [random.randint(20, 150) for _ in range(len(air_sensors))]
                
                # Aggregate by Quartier
                district_aqi = air_sensors.groupby('quartier')['AQI'].mean().reset_index()
                district_aqi['AQI'] = district_aqi['AQI'].round(0)
                
                fig_aqi = px.bar(
                    district_aqi.sort_values('AQI', ascending=False),
                    x='quartier', y='AQI',
                    color='AQI',
                    title="Qualité de l'Air Moyenne par Quartier (AQI)",
                    labels={'quartier': 'Quartier', 'AQI': 'Indice Qualité Air Moyen'},
                    color_continuous_scale='RdYlGn_r'
                )
                st.plotly_chart(fig_aqi, use_container_width=True)
            else:
                st.info("Aucun capteur de qualité de l'air trouvé.")

    with col_b:
        st.markdown("### Disponibilité des Capteurs")
        if not df_sensors.empty:
            status_counts = df_sensors['statut'].value_counts().reset_index()
            status_counts.columns = ['Statut', 'Nombre']
            fig_status = px.pie(status_counts, values='Nombre', names='Statut', hole=0.4, title="État du Parc de Capteurs")
            st.plotly_chart(fig_status, use_container_width=True)

with tab2:
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.markdown("### Interventions Prédictives")
        if not df_interventions.empty:
            predictive = df_interventions[df_interventions['type_intervention'] == 'prédictive']
            st.metric("Nombre d'interventions prédictives", predictive.shape[0])
            st.metric("Coût Total Prédictif", f"{predictive['cout'].sum():,.2f} TND")
            
            fig_type = px.histogram(df_interventions, x='type_intervention', y='cout', title="Coût par Type d'Intervention", color='type_intervention')
            st.plotly_chart(fig_type, use_container_width=True)

    with col_d:
        st.markdown("### Impact CO2 des Interventions")
        if not df_interventions.empty:
            fig_co2_int = px.scatter(
                df_interventions, 
                x='duree', 
                y='impact_co2', 
                size='cout', 
                color='type_intervention', 
                hover_data=['date_heure'],
                title="Impact CO2 vs Durée (min) & Coût",
                labels={'duree': 'Durée (minutes)', 'impact_co2': 'Impact CO2 (kg)', 'cout': 'Coût (TND)'}
            )
            st.plotly_chart(fig_co2_int, use_container_width=True)

with tab3:
    col_e, col_f = st.columns(2)
    
    with col_e:
        st.markdown("### Top Citoyens Engagés (Score Écologique)")
        if not df_citizens.empty:
            top_citizens = df_citizens.sort_values('score_ecologique', ascending=False).head(10)
            st.dataframe(top_citizens[['nom', 'email', 'score_ecologique', 'preferences_mobilite']], use_container_width=True)

    with col_f:
        st.markdown("### Véhicules Autonomes - Économie CO2")
        if not df_trips.empty:
            # Merge with vehicles to get plates
            if 'plaque_immatriculation' not in df_trips.columns and not df_vehicles.empty:
                # df_trips['vehicule'] is the ID, df_vehicles['id_vehicule'] is the ID
                df_merged = df_trips.merge(df_vehicles, left_on='vehicule', right_on='id_vehicule', how='left')
                trip_stats = df_merged.groupby('plaque_immatriculation')['economie_co2'].sum().reset_index().sort_values('economie_co2', ascending=False)
                fig_trips = px.bar(trip_stats.head(10), x='plaque_immatriculation', y='economie_co2', title="Top Véhicules (Économie CO2 Totale)")
            else:
                 # Fallback if merge fails
                trip_stats = df_trips.groupby('vehicule')['economie_co2'].sum().reset_index().sort_values('economie_co2', ascending=False)
                fig_trips = px.bar(trip_stats.head(10), x='vehicule', y='economie_co2', title="Top Véhicules (Économie CO2 Totale)")
            st.plotly_chart(fig_trips, use_container_width=True)
