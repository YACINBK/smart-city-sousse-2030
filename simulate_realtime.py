import os
import django
import time
import random
import math
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcity_backend.settings")
django.setup()

from smartcity_backend.api.models import Capteur, Intervention, Trajet, VehiculeAutonome, Technicien

# Center Coordinates for Sousse Municipalities (Lat, Lon)
# Bouficha removed as requested.
DISTRICT_CENTERS = {
    "Ennfidha": (36.130, 10.380),
    "Hergla": (36.030, 10.500),
    "Sidi Bou Ali": (35.950, 10.470),
    "Kondar": (35.920, 10.300),
    "Akouda": (35.870, 10.560),
    "Kalaa Kebira": (35.870, 10.530),
    "Hammam Sousse": (35.860, 10.590),
    "Sousse Ville": (35.825, 10.635),
    "Sousse Jawhara": (35.810, 10.620),
    "Sousse Riadh": (35.800, 10.600),
    "Sidi Abdelhamid": (35.800, 10.640),
    "Kalaa Sghira": (35.820, 10.550),
    "Zaouia Ksiba Thrayet": (35.780, 10.630),
    "Msaken": (35.730, 10.580),
    "Sidi El Heni": (35.670, 10.320),
}

def get_gaussian_coords(district):
    if district not in DISTRICT_CENTERS:
        district = "Sousse Ville"
    center_lat, center_lon = DISTRICT_CENTERS[district]
    lat = random.gauss(center_lat, 0.01)
    lon = random.gauss(center_lon, 0.01)
    return lat, lon

def calculate_duration(lat1, lon1, lat2, lon2):
    dist_km = math.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 111
    speed_kmh = random.uniform(20, 60)
    return int((dist_km / speed_kmh) * 60)

def simulate():
    print("Starting real-time simulation... Press Ctrl+C to stop.")
    
    while True:
        try:
            # 1. Update Sensor Status (Randomly flip 1 sensor)
            sensors = list(Capteur.objects.all())
            if sensors:
                sensor = random.choice(sensors)
                old_status = sensor.statut
                new_status = random.choice(["actif", "en_maintenance", "hors_service"])
                if old_status != new_status:
                    sensor.statut = new_status
                    sensor.save()
                    print(f"[SENSOR] {sensor.type_capteur} ({sensor.quartier}) changed to {new_status}")

            # 2. Add New Trip (20% chance)
            if random.random() < 0.2:
                vehicles = list(VehiculeAutonome.objects.all())
                if vehicles:
                    v = random.choice(vehicles)
                    start = timezone.now()
                    
                    q_start = random.choice(list(DISTRICT_CENTERS.keys()))
                    q_end = random.choice(list(DISTRICT_CENTERS.keys()))
                    lat1, lon1 = get_gaussian_coords(q_start)
                    lat2, lon2 = get_gaussian_coords(q_end)
                    
                    duration = calculate_duration(lat1, lon1, lat2, lon2)
                    if duration < 5: duration = 5
                    
                    Trajet.objects.create(
                        vehicule=v,
                        origine=f"Simulated ({q_start})",
                        destination=f"Simulated ({q_end})",
                        duree=duration,
                        economie_co2=round(random.uniform(0.5, 5.0), 2)
                    )
                    print(f"[TRIP] New trip for {v.plaque_immatriculation} ({duration} min)")

            # 3. Add New Intervention (10% chance)
            if random.random() < 0.1:
                if sensors:
                    s = random.choice(sensors)
                    # Create intervention
                    Intervention.objects.create(
                        capteur=s,
                        date_heure=timezone.now(),
                        type_intervention="corrective",
                        duree=random.randint(30, 120),
                        cout=random.uniform(100, 300),
                        impact_co2=random.uniform(1, 10)
                    )
                    print(f"[INTERVENTION] New intervention on {s.type_capteur}")

            time.sleep(2) # Update every 2 seconds

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    simulate()
