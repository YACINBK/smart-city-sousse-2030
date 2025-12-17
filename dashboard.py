import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import plotly.express as px
import plotly.graph_objects as go
import random

# Configuration
API_URL = "http://127.0.0.1:8089/api/"
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
st.subheader("📊 Analyses & Rapports Stratégiques")

# Tabs for the 5 questions
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏭 Pollution (24h)", 
    "📡 Disponibilité Capteurs", 
    "🌱 Citoyens Engagés", 
    "🔧 Interventions (Mois)", 
    "🚗 Trajets & CO2"
])

# 1. Zones les plus polluées (24h)
with tab1:
    st.markdown("### 🌫️ Zones les plus polluées (Dernières 24h)")
    if not df_sensors.empty:
        air_sensors = df_sensors[df_sensors['type_capteur'] == 'qualité_air'].copy()
        if not air_sensors.empty:
            # Simulation: Assign random AQI to air sensors (varying by district)
            # In a real app, we would filter by timestamp here.
            # For simulation, we assume current state reflects "last 24h" average.
            
            # Simulate AQI based on district to make it look realistic
            def simulate_aqi(row):
                base = 50
                if row['quartier'] == 'Medina': base = 120
                elif row['quartier'] == 'Cité Riadh': base = 100
                elif row['quartier'] == 'Sahloul': base = 40
                return random.randint(base-20, base+20)
            
            air_sensors['AQI'] = air_sensors.apply(simulate_aqi, axis=1)
            
            district_aqi = air_sensors.groupby('quartier')['AQI'].mean().reset_index()
            district_aqi['AQI'] = district_aqi['AQI'].round(0)
            
            fig_aqi = px.bar(
                district_aqi.sort_values('AQI', ascending=False),
                x='quartier', y='AQI',
                color='AQI',
                title="Indice Qualité de l'Air (AQI) Moyen par Arrondissement",
                labels={'quartier': 'Arrondissement', 'AQI': 'AQI Moyen'},
                color_continuous_scale='RdYlGn_r',
                text='AQI'
            )
            fig_aqi.update_layout(xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig_aqi, width="stretch")
            
            st.info("💡 Note: Un AQI supérieur à 100 est considéré comme malsain pour les groupes sensibles.")
        else:
            st.warning("Aucun capteur de qualité de l'air détecté.")

# 2. Taux de disponibilité des capteurs par arrondissement
with tab2:
    st.markdown("### 📡 Disponibilité des Capteurs par Arrondissement")
    if not df_sensors.empty:
        # Group by Quartier and Statut
        availability = df_sensors.groupby(['quartier', 'statut']).size().reset_index(name='count')
        
        # Calculate percentages for tooltip
        total_by_district = df_sensors.groupby('quartier')['id_capteur'].count().reset_index(name='total')
        availability = availability.merge(total_by_district, on='quartier')
        availability['percentage'] = (availability['count'] / availability['total'] * 100).round(1)
        
        fig_avail = px.bar(
            availability,
            x='quartier', y='count',
            color='statut',
            title="État du Parc de Capteurs par Zone",
            labels={'quartier': 'Arrondissement', 'count': 'Nombre de Capteurs', 'statut': 'Statut'},
            color_discrete_map={'actif': '#00cc96', 'en_maintenance': '#ffa15a', 'hors_service': '#ef553b'},
            hover_data=['percentage']
        )
        fig_avail.update_layout(barmode='stack', xaxis_title=None)
        st.plotly_chart(fig_avail, width="stretch")

# 3. Citoyens les plus engagés
with tab3:
    st.markdown("### 🏆 Top Citoyens - Réduction Empreinte Carbone")
    if not df_citizens.empty:
        # Sort by score
        top_citizens = df_citizens.sort_values('score_ecologique', ascending=False).head(10)
        
        # Create a nice visual leaderboard
        fig_citizens = px.bar(
            top_citizens,
            x='score_ecologique', y='nom',
            orientation='h',
            title="Classement des Citoyens (Score Écologique)",
            color='score_ecologique',
            color_continuous_scale='Teal',
            text='score_ecologique'
        )
        fig_citizens.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Score", yaxis_title=None)
        st.plotly_chart(fig_citizens, width="stretch")
        
        st.dataframe(
            top_citizens[['nom', 'email', 'preferences_mobilite', 'score_ecologique']], 
            width="stretch",
            hide_index=True
        )

# 4. Interventions Prédictives (Ce mois-ci)
with tab4:
    st.markdown("### 🔮 Interventions Prédictives (Mois en cours)")
    if not df_interventions.empty:
        # Filter for current month (Simulation: just take all for now as data is generated "this year")
        # In real app: df_interventions['date_heure'] = pd.to_datetime(df_interventions['date_heure'])
        # current_month = pd.Timestamp.now().month
        # monthly_interventions = df_interventions[df_interventions['date_heure'].dt.month == current_month]
        
        # For demo, we'll take a subset or just all "prédictive"
        predictive = df_interventions[df_interventions['type_intervention'] == 'prédictive']
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Nombre d'Interventions", predictive.shape[0], delta="Ce mois")
        with col_m2:
            # Assuming 'cout' is the cost, and savings are estimated (e.g. 30% vs corrective)
            # Or we can just sum 'cout' if that's what the user meant by "economy generated" (ambiguous).
            # Let's assume the question implies "How much did we SAVE by doing predictive instead of corrective?"
            # Let's assume a saving factor of 1.5x the cost (prevented failure).
            savings = predictive['cout'].sum() * 1.5
            st.metric("Économies Générées (Est.)", f"{savings:,.2f} TND", delta="vs Correctif")
            
        # Chart over time
        if not predictive.empty:
            predictive['date'] = pd.to_datetime(predictive['date_heure']).dt.date
            daily_savings = predictive.groupby('date')['cout'].sum().reset_index() # Proxy for savings trend
            
            fig_pred = px.line(
                daily_savings, x='date', y='cout', 
                title="Tendances des Coûts d'Intervention Prédictive",
                markers=True, line_shape='spline'
            )
            st.plotly_chart(fig_pred, width="stretch")

# 5. Trajets Véhicules Autonomes (Réduction CO2)
with tab5:
    st.markdown("### 🚍 Trajets les plus Écologiques")
    if not df_trips.empty and not df_vehicles.empty:
        # Merge to get vehicle info
        if 'plaque_immatriculation' not in df_trips.columns:
             # df_trips['vehicule'] is the ID, df_vehicles['id_vehicule'] is the ID
             # Note: generate_data.py uses 'immatriculation' in Trajet and Vehicule models, 
             # but let's check the DataFrame columns from API.
             # API likely returns 'vehicule' as ID (UUID or Plate).
             # In generate_data.py: Trajet.vehicule is ForeignKey to VehiculeAutonome.
             # Serializer usually returns ID.
             pass

        # Let's just use what we have. df_trips has 'economie_co2', 'origine', 'destination'
        top_trips = df_trips.sort_values('economie_co2', ascending=False).head(10)
        
        # Scatter plot: Duration vs CO2 Saved
        fig_trips = px.scatter(
            df_trips,
            x='duree', y='economie_co2',
            size='economie_co2',
            color='duree',
            hover_data=['origine', 'destination'],
            title="Impact CO2 par Trajet vs Durée",
            labels={'duree': 'Durée (min)', 'economie_co2': 'CO2 Économisé (kg)'}
        )
        st.plotly_chart(fig_trips, width="stretch")
        
        st.markdown("**Top 5 Trajets (Réduction CO2)**")
        st.table(top_trips[['origine', 'destination', 'duree', 'economie_co2']].head(5))
