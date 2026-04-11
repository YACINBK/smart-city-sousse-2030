import math
import random
from decimal import Decimal

from django.utils import timezone

from .constants import DEFAULT_DISTRICT, DISTRICT_CENTERS
from .models import Capteur, Intervention, Trajet, VehiculeAutonome


def normalize_district_name(district):
    if district in DISTRICT_CENTERS:
        return district
    return DEFAULT_DISTRICT


def get_gaussian_coords(district, sigma=0.01):
    center_lat, center_lon = DISTRICT_CENTERS[normalize_district_name(district)]
    return random.gauss(center_lat, sigma), random.gauss(center_lon, sigma)


def calculate_trip_duration(lat1, lon1, lat2, lon2, min_speed=20, max_speed=60):
    distance_km = math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 111
    speed_kmh = random.uniform(min_speed, max_speed)
    duration_minutes = int((distance_km / speed_kmh) * 60)
    return max(duration_minutes, 5)


def _status_weights_for_sensor(sensor):
    if sensor.quartier == "Sousse Ville":
        return [0.5, 0.25, 0.25]
    return [0.6, 0.2, 0.2]


def simulate_system_step():
    changed_sensors = []
    sensors = list(Capteur.objects.all())

    for sensor in sensors:
        if random.random() >= 0.20:
            continue

        new_status = random.choices(
            ["actif", "en_maintenance", "hors_service"],
            weights=_status_weights_for_sensor(sensor),
            k=1,
        )[0]
        if sensor.statut == new_status:
            continue

        sensor.statut = new_status
        changed_sensors.append(sensor)

    if changed_sensors:
        Capteur.objects.bulk_update(changed_sensors, ["statut"])

    trips_to_create = []
    vehicles = list(VehiculeAutonome.objects.all())
    district_names = list(DISTRICT_CENTERS.keys())
    if vehicles:
        for _ in range(random.randint(10, 25)):
            vehicle = random.choice(vehicles)
            origin_district = random.choice(district_names)
            destination_district = random.choice(district_names)
            trips_to_create.append(
                Trajet(
                    vehicule=vehicle,
                    origine=f"Simulated ({origin_district})",
                    destination=f"Simulated ({destination_district})",
                    duree=random.randint(10, 60),
                    economie_co2=Decimal(str(round(random.uniform(0.5, 5.0), 2))),
                )
            )

    if trips_to_create:
        Trajet.objects.bulk_create(trips_to_create)

    interventions_to_create = []
    repaired_sensors = []
    for sensor in Capteur.objects.filter(statut="hors_service"):
        if random.random() >= 0.4:
            continue

        interventions_to_create.append(
            Intervention(
                capteur=sensor,
                date_heure=timezone.now(),
                type_intervention="corrective",
                duree=random.randint(60, 180),
                cout=Decimal(str(round(random.uniform(200, 500), 2))),
                impact_co2=Decimal("5.50"),
            )
        )
        sensor.statut = "en_maintenance"
        repaired_sensors.append(sensor)

    if interventions_to_create:
        Intervention.objects.bulk_create(interventions_to_create)
    if repaired_sensors:
        Capteur.objects.bulk_update(repaired_sensors, ["statut"])

    return {
        "sensor_updates": len(changed_sensors),
        "trips_created": len(trips_to_create),
        "interventions_created": len(interventions_to_create),
        "timestamp": timezone.now(),
    }
