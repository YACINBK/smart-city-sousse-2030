import os
import django
import random
import uuid
import math
from faker import Faker
from datetime import timedelta

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcity_backend.settings")
django.setup()

from smartcity_backend.api.models import (
    Technicien, Capteur, Intervention, Citoyen, VehiculeAutonome, Trajet, Proprietaire
)

fake = Faker("fr_FR")

# Custom Tunisian Data Providers
TUNISIAN_FIRST_NAMES = [
    "Mohamed", "Ahmed", "Youssef", "Aziz", "Mehdi", "Oussema", "Yassine", "Amine", "Bilel", "Hamza",
    "Mariem", "Fatma", "Sarra", "Nour", "Emna", "Aya", "Tasnim", "Farah", "Yasmine", "Hiba"
]
TUNISIAN_LAST_NAMES = [
    "Ben Ali", "Trabelsi", "Gharbi", "Dridi", "Hammami", "Mejri", "Jaziri", "Ayari", "Riahi", "Oueslati",
    "Ben Amor", "Bouazizi", "Mebarki", "Saidi", "Chebbi"
]
SOUSSE_STREETS = [
    "Av. Habib Bourguiba", "Av. Hedi Chaker", "Rue de l'Indépendance", "Rue de Constantine", 
    "Av. des Orangers", "Rue Ibn Khaldoun", "Route de Tunis", "Boulevard du 14 Janvier",
    "Rue de la République", "Av. Leopold Senghor"
]

# Center Coordinates for Sousse Municipalities (Lat, Lon)
# Bouficha removed as requested.
# Coords adjusted to avoid water bodies (Sebkhet, Sea)
DISTRICT_CENTERS = {
    "Ennfidha": (36.130, 10.380),
    "Hergla": (36.030, 10.500), # Moved slightly West
    "Sidi Bou Ali": (35.950, 10.470),
    "Kondar": (35.920, 10.300),
    "Akouda": (35.870, 10.560),
    "Kalaa Kebira": (35.870, 10.530),
    "Hammam Sousse": (35.860, 10.590), # Moved slightly West
    "Sousse Ville": (35.825, 10.635),
    "Sousse Jawhara": (35.810, 10.620),
    "Sousse Riadh": (35.800, 10.600),
    "Sidi Abdelhamid": (35.800, 10.640), # Moved slightly West
    "Kalaa Sghira": (35.820, 10.550),
    "Zaouia Ksiba Thrayet": (35.780, 10.630),
    "Msaken": (35.730, 10.580),
    "Sidi El Heni": (35.670, 10.320), # Moved East of Sebkhet
}

def get_tunisian_name():
    return f"{random.choice(TUNISIAN_FIRST_NAMES)} {random.choice(TUNISIAN_LAST_NAMES)}"

def get_tunisian_phone():
    return f"+216 {random.choice([2, 5, 9, 4])}{random.randint(0, 9)} {random.randint(100, 999)} {random.randint(100, 999)}"

def get_sousse_address():
    return f"{random.randint(1, 150)}, {random.choice(SOUSSE_STREETS)}, {random.choice(['Sousse', 'Hammam Sousse', 'Kantaoui'])}"

def get_gaussian_coords(district):
    if district not in DISTRICT_CENTERS:
        district = "Sousse Ville"
    center_lat, center_lon = DISTRICT_CENTERS[district]
    
    # Reduced sigma to 0.01 to keep points tighter to centers and avoid water
    lat = random.gauss(center_lat, 0.01)
    lon = random.gauss(center_lon, 0.01)
    return lat, lon

def calculate_duration(lat1, lon1, lat2, lon2):
    # Haversine approx (or simple Euclidean for short distances)
    # 1 deg lat ~= 111 km
    dist_km = math.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 111
    speed_kmh = random.uniform(20, 60) # Increased max speed for inter-city
    return int((dist_km / speed_kmh) * 60)

def generate_data():
    print("Generating data...")

    # 1. Technicians
    print("- Generating Technicians...")
    technicians = []
    for _ in range(10):
        t = Technicien.objects.create(
            nom=get_tunisian_name(),
            certification=True
        )
        technicians.append(t)

    # 2. Owners (Proprietaire)
    print("- Generating Owners...")
    owners = []
    for _ in range(5):
        o = Proprietaire.objects.create(
            nom=f"Société {random.choice(['Sousse', 'Sahel', 'Tunisie'])} {random.choice(['Tech', 'Immo', 'Services'])}" if random.random() > 0.5 else get_tunisian_name(),
            type_proprietaire=random.choice(['municipalité', 'privé']),
            adresse=get_sousse_address(),
            telephone=get_tunisian_phone(),
            email=f"contact@{fake.domain_name()}"
        )
        owners.append(o)

    # 3. Sensors (Capteurs)
    print("- Generating Sensors...")
    sensors = []
    sensor_types = ["qualité_air", "trafic", "énergie", "déchets", "éclairage"]
    districts = list(DISTRICT_CENTERS.keys())
    
    # Generate more sensors (100) to cover the larger area
    for _ in range(100):
        quartier = random.choice(districts)
        lat, lon = get_gaussian_coords(quartier)
        
        s = Capteur.objects.create(
            type_capteur=random.choice(sensor_types),
            latitude=lat,
            longitude=lon,
            statut=random.choice(["actif", "en_maintenance", "hors_service"]),
            quartier=quartier,
            date_installation=fake.date_between(start_date="-2y", end_date="today"),
            proprietaire=random.choice(owners)
        )
        sensors.append(s)

    # 4. Interventions
    print("- Generating Interventions...")
    for _ in range(50):
        intervention = Intervention.objects.create(
            capteur=random.choice(sensors),
            date_heure=fake.date_time_this_year(tzinfo=django.utils.timezone.get_current_timezone()),
            type_intervention=random.choice(["prédictive", "corrective", "curative"]),
            duree=random.randint(15, 240),
            cout=round(random.uniform(50.0, 500.0), 2),
            impact_co2=round(random.uniform(0.5, 50.0), 2)
        )
        
        t1 = random.choice(technicians)
        t2 = random.choice(technicians)
        while t1 == t2:
            t2 = random.choice(technicians)
            
        from smartcity_backend.api.models import InterventionTechnicien
        InterventionTechnicien.objects.create(intervention=intervention, technicien=t1, role='intervenant')
        InterventionTechnicien.objects.create(intervention=intervention, technicien=t2, role='validateur')

    # 5. Citizens
    print("- Generating Citizens...")
    for _ in range(100):
        name = get_tunisian_name()
        email_name = name.lower().replace(" ", ".")
        email = f"{email_name}.{random.randint(1000, 9999)}@{random.choice(['gmail.com', 'yahoo.fr', 'topnet.tn'])}"
        Citoyen.objects.create(
            nom=name,
            adresse=get_sousse_address(),
            email=email,
            telephone=get_tunisian_phone(),
            score_ecologique=random.randint(0, 100),
            preferences_mobilite=random.choice(["Vélo", "Marche", "Transports en commun", "Véhicule électrique"])
        )

    # 6. Vehicles
    print("- Generating Vehicles...")
    vehicles = []
    for _ in range(20):
        v_id = f"{random.randint(100, 300)} TU {random.randint(1000, 9999)}"
        v, created = VehiculeAutonome.objects.get_or_create(
            plaque_immatriculation=v_id,
            defaults={
                'type_vehicule': random.choice(["Bus", "Navette", "Voiture"]),
                'energie_utilisee': "Électrique"
            }
        )
        if created:
            vehicles.append(v)

    # 7. Trips (Trajets)
    print("- Generating Trips...")
    if vehicles:
        for _ in range(50):
            start = fake.date_time_this_month(tzinfo=django.utils.timezone.get_current_timezone())
            
            q_start = random.choice(districts)
            q_end = random.choice(districts)
            lat1, lon1 = get_gaussian_coords(q_start)
            lat2, lon2 = get_gaussian_coords(q_end)
            
            duration = calculate_duration(lat1, lon1, lat2, lon2)
            if duration < 5: duration = 5
            
            end = start + timedelta(minutes=duration)
            
            Trajet.objects.create(
                vehicule=random.choice(vehicles),
                origine=f"{get_sousse_address()} ({q_start})",
                destination=f"{get_sousse_address()} ({q_end})",
                duree=duration,
                economie_co2=round(random.uniform(1.0, 15.0), 2)
            )

    print("Data generation complete!")

if __name__ == "__main__":
    generate_data()
