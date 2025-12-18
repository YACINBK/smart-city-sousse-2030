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
# Anchors for valid land placement (Vehicles)
DISTRICT_ANCHORS = [
    (35.8245, 10.6345), # Medina
    (35.8360, 10.5900), # Sahloul
    (35.8450, 10.6200), # Khezama
    (35.8180, 10.5500), # Kalaa Sghira
    (35.8550, 10.6050), # Hammam Sousse
    (35.8050, 10.6100), # Cité Riadh
    (35.8750, 10.5400), # Kalaa Kebira
]

# ... (styles)

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
        return pd.DataFrame()

# --- Fragment: Key Metrics ---
@st.fragment
def display_metrics():
    col1, col2, col3, col4 = st.columns(4)

    df_sensors = fetch_data("capteurs")
    df_interventions = fetch_data("interventions")
    df_citizens = fetch_data("citoyens")
    df_trips = fetch_data("trajets")

    # Conversions
    if not df_interventions.empty:
        df_interventions['cout'] = pd.to_numeric(df_interventions['cout'], errors='coerce').fillna(0)
    if not df_trips.empty:
        df_trips['economie_co2'] = pd.to_numeric(df_trips['economie_co2'], errors='coerce').fillna(0)
    if not df_citizens.empty:
        df_citizens['score_ecologique'] = pd.to_numeric(df_citizens['score_ecologique'], errors='coerce').fillna(0)
    if not df_sensors.empty:
        df_sensors['latitude'] = pd.to_numeric(df_sensors['latitude'], errors='coerce')
        df_sensors['longitude'] = pd.to_numeric(df_sensors['longitude'], errors='coerce')

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
def display_map():
    st.subheader("📍 Carte en Temps Réel (Gouvernorat de Sousse)")
    
    df_sensors = fetch_data("capteurs")
    df_vehicles = fetch_data("vehicules")
    
    if not df_sensors.empty:
        df_sensors['latitude'] = pd.to_numeric(df_sensors['latitude'], errors='coerce')
        df_sensors['longitude'] = pd.to_numeric(df_sensors['longitude'], errors='coerce')

    # Zoom out to see the whole governorate
    m = folium.Map(location=[35.9500, 10.5000], zoom_start=10, tiles="CartoDB dark_matter")

    # Add Sensors
    if not df_sensors.empty:
        for _, row in df_sensors.iterrows():
            color = "green" if row['statut'] == 'actif' else "red" if row['statut'] == 'hors_service' else "orange"
            
            if row['type_capteur'] == 'qualité_air': icon = "leaf"
            elif row['type_capteur'] == 'trafic': icon = "road"
            elif row['type_capteur'] == 'énergie': icon = "bolt"
            elif row['type_capteur'] == 'déchets': icon = "trash"
            elif row['type_capteur'] == 'éclairage': icon = "lightbulb-o"
            else: icon = "info-circle"
            
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                tooltip=f"<b>Type:</b> {row['type_capteur']}<br><b>Statut:</b> {row['statut']}<br><b>ID:</b> {row['id_capteur']}",
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(m)

    # Add Simulated Vehicles
    if not df_vehicles.empty:
        for _, row in df_vehicles.iterrows():
            anchor = random.choice(DISTRICT_ANCHORS)
            # Gaussian distribution for vehicles too
            lat = random.gauss(anchor[0], 0.015)
            lon = random.gauss(anchor[1], 0.015)
            
            folium.Marker(
                location=[lat, lon],
                tooltip=f"Véhicule {row['plaque_immatriculation']}",
                icon=folium.Icon(color="blue", icon="car", prefix="fa")
            ).add_to(m)

    st_folium(m, width=1200, height=350, returned_objects=[])

# --- Load Data ---
st.title("🏙️ Smart City Sousse - Analytics Platform")
st.markdown("Real-time monitoring of **Neo-Sousse 2030**")

if st.button("🔄 Actualiser les Données"):
    st.rerun()

# --- Fragment: Analytics ---
@st.fragment
def display_analytics():
    st.divider()
    st.subheader("📊 Analyses & Rapports Stratégiques")
    
    df_sensors = fetch_data("capteurs")
    df_interventions = fetch_data("interventions")
    df_citizens = fetch_data("citoyens")
    df_trips = fetch_data("trajets")
    df_vehicles = fetch_data("vehicules")

    # Conversions
    if not df_interventions.empty:
        df_interventions['cout'] = pd.to_numeric(df_interventions['cout'], errors='coerce').fillna(0)
        df_interventions['impact_co2'] = pd.to_numeric(df_interventions['impact_co2'], errors='coerce').fillna(0)
        df_interventions['duree'] = pd.to_numeric(df_interventions['duree'], errors='coerce').fillna(0)
    if not df_trips.empty:
        df_trips['economie_co2'] = pd.to_numeric(df_trips['economie_co2'], errors='coerce').fillna(0)
    if not df_citizens.empty:
        df_citizens['score_ecologique'] = pd.to_numeric(df_citizens['score_ecologique'], errors='coerce').fillna(0)


    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏭 Pollution (24h)", 
        "📡 Disponibilité Capteurs", 
        "🌱 Citoyens Engagés", 
        "🔧 Interventions (Mois)", 
        "🚗 Trajets & CO2"
    ])

    # 1. Pollution
    with tab1:
        st.markdown("### 🌫️ Zones les plus polluées (Dernières 24h)")
        if not df_sensors.empty:
            air_sensors = df_sensors[df_sensors['type_capteur'] == 'qualité_air'].copy()
            if not air_sensors.empty:
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
                    color_continuous_scale='RdYlGn_r'
                )
                st.plotly_chart(fig_aqi, width="stretch")
            else:
                st.warning("Aucun capteur de qualité de l'air détecté.")

    # 2. Availability
    with tab2:
        st.markdown("### 📡 Disponibilité des Capteurs (%)")
        if not df_sensors.empty:
            # Calculate counts
            availability = df_sensors.groupby(['quartier', 'statut']).size().reset_index(name='count')
            # Calculate total per district
            total_per_district = df_sensors.groupby('quartier').size().reset_index(name='total')
            # Merge
            availability = availability.merge(total_per_district, on='quartier')
            # Calculate percentage
            availability['percentage'] = (availability['count'] / availability['total'] * 100).round(1)
            
            fig_avail = px.bar(
                availability,
                x='quartier', y='percentage',
                color='statut',
                title="Pourcentage de Disponibilité par Zone",
                text='percentage',
                color_discrete_map={'actif': '#00cc96', 'en_maintenance': '#ffa15a', 'hors_service': '#ef553b'}
            )
            fig_avail.update_traces(texttemplate='%{text}%', textposition='inside')
            st.plotly_chart(fig_avail, width="stretch")

    # 3. Citizens
    with tab3:
        st.markdown("### 🏆 Top Citoyens - Réduction Empreinte Carbone")
        if not df_citizens.empty:
            top_citizens = df_citizens.sort_values('score_ecologique', ascending=False).head(10)
            fig_citizens = px.bar(
                top_citizens,
                x='score_ecologique', y='nom',
                orientation='h',
                title="Classement des Citoyens (Score Écologique)",
                color='score_ecologique',
                color_continuous_scale='Teal'
            )
            fig_citizens.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_citizens, width="stretch")
            st.dataframe(top_citizens[['nom', 'email', 'preferences_mobilite', 'score_ecologique']], width="stretch", hide_index=True)

    # 4. Interventions
    with tab4:
        st.markdown("### 🔮 Interventions Prédictives (Mois en cours)")
        if not df_interventions.empty:
            predictive = df_interventions[df_interventions['type_intervention'] == 'prédictive']
            col_m1, col_m2 = st.columns(2)
            with col_m1: st.metric("Nombre d'Interventions", predictive.shape[0], delta="Ce mois")
            with col_m2: st.metric("Économies Générées (Est.)", f"{predictive['cout'].sum() * 1.5:,.2f} TND", delta="vs Correctif")
            
            if not predictive.empty:
                predictive['date'] = pd.to_datetime(predictive['date_heure']).dt.date
                daily_savings = predictive.groupby('date')['cout'].sum().reset_index()
                fig_pred = px.line(daily_savings, x='date', y='cout', title="Tendances des Coûts")
                st.plotly_chart(fig_pred, width="stretch")

    # 5. Trips
    with tab5:
        st.markdown("### 🚍 Leaderboard des Trajets Écologiques")
        if not df_trips.empty:
            # Leaderboard
            top_trips = df_trips.sort_values('economie_co2', ascending=False).head(5)
            st.dataframe(
                top_trips[['origine', 'destination', 'duree', 'economie_co2']], 
                width="stretch", 
                hide_index=True,
                column_config={
                    "duree": st.column_config.NumberColumn("Durée (min)"),
                    "economie_co2": st.column_config.ProgressColumn("CO2 Économisé (kg)", format="%.2f", min_value=0, max_value=15)
                }
            )
            
            st.markdown("#### 🗺️ Visualisation des Meilleurs Trajets")
            # Map for top trips
            m_trips = folium.Map(location=[35.8300, 10.6100], zoom_start=11, tiles="CartoDB dark_matter")
            
            colors = ['#00ff00', '#33ff33', '#66ff66', '#99ff99', '#ccffcc']
            
            for i, (_, row) in enumerate(top_trips.iterrows()):
                # Extract district from string "Address (District)"
                try:
                    origin_dist = row['origine'].split('(')[-1].strip(')')
                    dest_dist = row['destination'].split('(')[-1].strip(')')
                    
                    # Let's use a helper mapping based on the string
                    
                    def get_coords_from_name(name):
                        # Simple lookup in our known list
                        # This is a bit hacky but works for visualization
                        district_names = ["Ennfidha", "Hergla", "Sidi Bou Ali", "Kondar", "Akouda", "Kalaa Kebira", "Hammam Sousse", "Sousse Ville", "Sousse Jawhara", "Sousse Riadh", "Sidi Abdelhamid", "Kalaa Sghira", "Zaouia Ksiba Thrayet", "Msaken", "Sidi El Heni"]
                        for dist_name, coords in zip(district_names, DISTRICT_ANCHORS):
                            if dist_name in name: return coords
                        return (35.83, 10.63) # Default
                        
                    start_coords = get_coords_from_name(origin_dist)
                    end_coords = get_coords_from_name(dest_dist)
                    
                    # Add jitter to separate lines
                    start_coords = (start_coords[0] + random.uniform(-0.01, 0.01), start_coords[1] + random.uniform(-0.01, 0.01))
                    end_coords = (end_coords[0] + random.uniform(-0.01, 0.01), end_coords[1] + random.uniform(-0.01, 0.01))

                    folium.Marker(start_coords, icon=folium.Icon(color="green", icon="play", prefix='fa'), tooltip=f"Départ: {row['origine']}").add_to(m_trips)
                    folium.Marker(end_coords, icon=folium.Icon(color="red", icon="stop", prefix='fa'), tooltip=f"Arrivée: {row['destination']}").add_to(m_trips)
                    folium.PolyLine([start_coords, end_coords], color=colors[i], weight=4, tooltip=f"Trajet {i+1}: {row['economie_co2']}kg CO2").add_to(m_trips)
                    
                except Exception as e:
                    pass

            st_folium(m_trips, width=1200, height=400, returned_objects=[])

# --- Run Dashboard Components ---
display_metrics()
display_map()
display_analytics()
