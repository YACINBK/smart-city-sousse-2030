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
st.markdown("""
<style>
    .metric-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #4F4F4F;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .metric-value { font-size: 24px; font-weight: bold; color: #00CC96; }
    .metric-label { font-size: 14px; color: #E0E0E0; font-family: sans-serif; }
</style>
""", unsafe_allow_html=True)

# Anchors for valid land placement (Vehicles)
DISTRICT_ANCHORS = [
    (36.130, 10.380), # Ennfidha
    (36.030, 10.500), # Hergla
    (35.950, 10.470), # Sidi Bou Ali
    (35.920, 10.300), # Kondar
    (35.870, 10.560), # Akouda
    (35.8750, 10.5400), # Kalaa Kebira
    (35.8550, 10.6050), # Hammam Sousse
    (35.825, 10.635), # Sousse Ville
    (35.810, 10.620), # Sousse Jawhara
    (35.800, 10.600), # Sousse Riadh
    (35.800, 10.640), # Sidi Abdelhamid
    (35.8180, 10.5500), # Kalaa Sghira
    (35.780, 10.630), # Zaouia Ksiba Thrayet
    (35.730, 10.580), # Msaken
    (35.670, 10.320), # Sidi El Heni
]

# --- Data Fetching ---
def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}/")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return pd.DataFrame()

# --- Fragment: Top Metrics ---
@st.fragment
def display_metrics():
    col1, col2, col3, col4 = st.columns(4)

    df_sensors = fetch_data("capteurs")
    df_interventions = fetch_data("interventions")
    df_citizens = fetch_data("citoyens")
    df_trips = fetch_data("trajets")

    if not df_interventions.empty:
        df_interventions['cout'] = pd.to_numeric(df_interventions['cout'], errors='coerce').fillna(0)
    if not df_trips.empty:
        df_trips['economie_co2'] = pd.to_numeric(df_trips['economie_co2'], errors='coerce').fillna(0)
    if not df_citizens.empty:
        df_citizens['score_ecologique'] = pd.to_numeric(df_citizens['score_ecologique'], errors='coerce').fillna(0)

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

# --- Fragment: Map ---
@st.fragment
def display_map_only():
    st.subheader("📍 Carte en Temps Réel (Gouvernorat de Sousse)")
    
    df_sensors = fetch_data("capteurs")
    df_vehicles = fetch_data("vehicules")
    
    if not df_sensors.empty:
        df_sensors['latitude'] = pd.to_numeric(df_sensors['latitude'], errors='coerce')
        df_sensors['longitude'] = pd.to_numeric(df_sensors['longitude'], errors='coerce')

    m = folium.Map(location=[35.8500, 10.6000], zoom_start=10, tiles="CartoDB dark_matter")

    if not df_sensors.empty:
        for _, row in df_sensors.iterrows():
            color = "green" if row['statut'] == 'actif' else "red" if row['statut'] == 'hors_service' else "orange"
            
            if row['type_capteur'] == 'qualité_air': icon = "leaf"
            elif row['type_capteur'] == 'trafic': icon = "road"
            elif row['type_capteur'] == 'énergie': icon = "bolt"
            elif row['type_capteur'] == 'déchets': icon = "trash"
            elif row['type_capteur'] == 'éclairage': icon = "lightbulb"
            else: icon = "info-circle"
            
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                tooltip=f"<b>Type:</b> {row['type_capteur']}<br><b>Statut:</b> {row['statut']}<br><b>ID:</b> {row['id_capteur']}",
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(m)

    if not df_vehicles.empty:
        # Get simulation step for movement
        step = st.session_state.get('sim_step', 0)
        
        for _, row in df_vehicles.iterrows():
            # Smart Movement: Change anchor/offset based on simulation step
            # Use hash of plate + step to deterministically move them per click
            move_seed = hash(row['plaque_immatriculation'] + str(step))
            
            # Pick a new district anchor based on the seed
            anchor_idx = move_seed % len(DISTRICT_ANCHORS)
            anchor = DISTRICT_ANCHORS[anchor_idx]
            
            # Calculate small offset (jitter)
            lat_off = (move_seed % 100 - 50) / 8000.0
            lon_off = ((move_seed >> 2) % 100 - 50) / 8000.0
            
            folium.Marker(
                location=[anchor[0] + lat_off, anchor[1] + lon_off],
                tooltip=f"Véhicule {row['plaque_immatriculation']}",
                icon=folium.Icon(color="blue", icon="car", prefix="fa")
            ).add_to(m)

    st_folium(m, height=500, use_container_width=True, returned_objects=[])

# --- Fragment: Sidebar Table ---
@st.fragment
def display_sidebar_table():
    st.subheader("⚠️ État des Zones")
    
    df_sensors = fetch_data("capteurs")
    
    if not df_sensors.empty:
        total_counts = df_sensors.groupby('quartier').size().reset_index(name='total')
        failure_counts = df_sensors[df_sensors['statut'] != 'actif'].groupby('quartier').size().reset_index(name='failed')
        
        merged = total_counts.merge(failure_counts, on='quartier', how='left').fillna(0)
        merged['failure_rate'] = (merged['failed'] / merged['total'])
        
        # Sort by Failure Rate Descending (Worst First)
        merged_sorted = merged.sort_values('failure_rate', ascending=False)
        merged_sorted['Pannes'] = (merged_sorted['failure_rate'] * 100).astype(int).astype(str) + "%"
        
        st.dataframe(
            merged_sorted[['quartier', 'Pannes']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "quartier": "Zone",
                "Pannes": st.column_config.TextColumn("Taux Panne"),
            }
        )

# --- Fragment: Analytics ---
@st.fragment
def display_analytics():
    st.divider()
    st.subheader("Analyses Approfondies")
    
    df_sensors = fetch_data("capteurs")
    df_interventions = fetch_data("interventions")
    df_citizens = fetch_data("citoyens")
    df_trips = fetch_data("trajets")
    
    if not df_interventions.empty:
        df_interventions['cout'] = pd.to_numeric(df_interventions['cout'], errors='coerce').fillna(0)
    if not df_trips.empty:
        df_trips['economie_co2'] = pd.to_numeric(df_trips['economie_co2'], errors='coerce').fillna(0)
    if not df_citizens.empty:
        df_citizens['score_ecologique'] = pd.to_numeric(df_citizens['score_ecologique'], errors='coerce').fillna(0)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏭 Pollution", "📡 Disponibilité", "🌱 Citoyens", "🔧 Interventions", "🚗 Trajets"
    ])

    with tab1: # Pollution
        st.caption("ℹ️ Ces statistiques représentent les dernières 24 heures.")
        if not df_sensors.empty:
            air_sensors = df_sensors[df_sensors['type_capteur'] == 'qualité_air'].copy()
            if not air_sensors.empty:
                def simulate_aqi(row):
                    base = 50
                    if row['quartier'] == 'Medina': base = 120
                    elif row['quartier'] == 'Cité Riadh': base = 100
                    return base + (hash(str(row['id_capteur'])) % 41 - 20)
                air_sensors['AQI'] = air_sensors.apply(simulate_aqi, axis=1)
                district_aqi = air_sensors.groupby('quartier')['AQI'].mean().reset_index()
                fig_aqi = px.bar(district_aqi.sort_values('AQI', ascending=False), x='quartier', y='AQI', color='AQI', color_continuous_scale='RdYlGn_r')
                st.plotly_chart(fig_aqi, use_container_width=True)

    with tab2: # Availability
        st.markdown("### Disponibilité des Capteurs (Global & Par Zone)")
        if not df_sensors.empty:
            col_graph1, col_graph2 = st.columns([1, 2])
            
            with col_graph1: # Global Pie
                global_status = df_sensors.groupby('statut').size().reset_index(name='count')
                fig_pie = px.pie(
                    global_status, 
                    values='count', names='statut', title="État Global",
                    color='statut', color_discrete_map={'actif': '#00cc96', 'en_maintenance': '#ffa15a', 'hors_service': '#ef553b'},
                    hole=0.4
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col_graph2: # District Bar
                availability = df_sensors.groupby(['quartier', 'statut']).size().reset_index(name='count')
                total_per_dist = df_sensors.groupby('quartier').size().reset_index(name='total')
                availability = availability.merge(total_per_dist, on='quartier')
                availability['percentage'] = (availability['count'] / availability['total'] * 100).round(1)
                
                # Sort by highest active %
                actif_rows = availability[availability['statut'] == 'actif']
                sorted_districts = actif_rows.sort_values('percentage', ascending=False)['quartier'].tolist()
                all_d = availability['quartier'].unique().tolist()
                for d in all_d: 
                    if d not in sorted_districts: sorted_districts.append(d)

                fig_avail = px.bar(
                    availability, x='quartier', y='percentage', color='statut',
                    title="Détail par Arrondissement (%)",
                    text='percentage',
                    color_discrete_map={'actif': '#00cc96', 'en_maintenance': '#ffa15a', 'hors_service': '#ef553b'},
                    category_orders={'quartier': sorted_districts}
                )
                fig_avail.update_traces(texttemplate='%{text}%', textposition='inside')
                st.plotly_chart(fig_avail, use_container_width=True)

    with tab3: # Citizens
        st.markdown("### Top Citoyens")
        if not df_citizens.empty:
            unique_citizens = df_citizens.sort_values('score_ecologique', ascending=False).drop_duplicates(subset=['nom'])
            top_citizens = unique_citizens.head(10)
            
            fig_citizens = px.bar(
                top_citizens.sort_values('score_ecologique', ascending=True),
                x='score_ecologique', y='nom', orientation='h', color='score_ecologique',
                title="Classement (Score Écologique)", color_continuous_scale='Teal'
            )
            st.plotly_chart(fig_citizens, use_container_width=True)
            st.dataframe(top_citizens[['nom', 'email', 'preferences_mobilite', 'score_ecologique']], use_container_width=True, hide_index=True)

    with tab4: # Interventions
        st.markdown("### Interventions")
        if not df_interventions.empty:
            predictive = df_interventions[df_interventions['type_intervention'] == 'prédictive']
            col_m1, col_m2 = st.columns(2)
            with col_m1: st.metric("Nombre (Prédictif)", predictive.shape[0])
            with col_m2: st.metric("Gain Est.", f"{predictive['cout'].sum() * 1.5:,.0f} TND")
            
            if not predictive.empty:
                predictive['date'] = pd.to_datetime(predictive['date_heure']).dt.date
                daily_savings = predictive.groupby('date')['cout'].sum().reset_index()
                fig_pred = px.line(daily_savings, x='date', y='cout', title="Tendances des Coûts")
                st.plotly_chart(fig_pred, use_container_width=True)

    with tab5: # Trips
        st.markdown("### Trajets Écologiques")
        if not df_trips.empty:
            top_trips = df_trips.sort_values('economie_co2', ascending=False).head(5)
            st.dataframe(top_trips[['origine', 'destination', 'duree', 'economie_co2']], use_container_width=True)
            
            m_trips = folium.Map(location=[35.83, 10.61], zoom_start=11, tiles="CartoDB dark_matter")
            colors = ['green', 'lime', 'yellow', 'orange', 'red']
            
            for i, (_, row) in enumerate(top_trips.iterrows()):
                try:
                    def get_coords_fuzzy(address_str):
                        address_lower = address_str.lower()
                        district_map = {
                            "ennfidha": (36.130, 10.380), "hergla": (36.030, 10.500), 
                            "sidi bou ali": (35.950, 10.470), "kondar": (35.920, 10.300), 
                            "akouda": (35.870, 10.560), "kalaa kebira": (35.8750, 10.5400), 
                            "hammam sousse": (35.8550, 10.6050), "sousse ville": (35.825, 10.635), 
                            "medina": (35.825, 10.635), "jawhara": (35.810, 10.620), "sousse jawhara": (35.810, 10.620),
                            "riadh": (35.800, 10.600), "sousse riadh": (35.800, 10.600), "cité riadh": (35.800, 10.600),
                            "sidi abdelhamid": (35.800, 10.640), "kalaa sghira": (35.8180, 10.5500), 
                            "zaouia": (35.780, 10.630), "ksiba": (35.780, 10.630), "thrayet": (35.780, 10.630),
                            "msaken": (35.730, 10.580), "sidi el heni": (35.670, 10.320)
                        }
                        for name, coords in district_map.items():
                            if name in address_lower: return coords
                        return (35.825, 10.635)

                    start_coords = get_coords_fuzzy(row['origine'])
                    end_coords = get_coords_fuzzy(row['destination'])
                    
                    # Independent Jitter
                    h_s = hash(row['origine'])
                    start_coords = (start_coords[0] + (h_s % 100 - 50)/7000.0, start_coords[1] + ((h_s >> 2) % 100 - 50)/7000.0)
                    h_e = hash(row['destination'])
                    end_coords = (end_coords[0] + (h_e % 100 - 50)/7000.0, end_coords[1] + ((h_e >> 2) % 100 - 50)/7000.0)
                    
                    folium.Marker(start_coords, icon=folium.Icon(color="green", icon="play", prefix='fa'), tooltip=f"Départ: {row['origine']}").add_to(m_trips)
                    folium.Marker(end_coords, icon=folium.Icon(color="red", icon="stop", prefix='fa'), tooltip=f"Arrivée: {row['destination']}").add_to(m_trips)
                    folium.PolyLine([start_coords, end_coords], color=colors[i%5], weight=4, tooltip=f"Trajet {i+1}: {row['economie_co2']}kg CO2").add_to(m_trips)
                except: pass
            
            st_folium(m_trips, height=400, use_container_width=True)

# --- Main Layout ---
if 'sim_step' not in st.session_state:
    st.session_state.sim_step = 0

st.title("Smart City Sousse")

if st.button("🔄 Actualiser (Smart Sim)"):
    # Trigger Backend Simulation Step
    try:
        requests.post(f"{API_URL}simulate/")
        st.toast("Simulation Step Triggered! 🚦")
        st.session_state.sim_step += 1 # Advance vehicle step
    except:
        st.error("Failed to trigger simulation.")
    st.rerun()

# 1. Stats at Top
display_metrics()

# 2. Main content: Map + Sidebar Table
col_map, col_table = st.columns([3, 1])

with col_map:
    display_map_only()

with col_table:
    display_sidebar_table()

# 3. Analytics
display_analytics()
