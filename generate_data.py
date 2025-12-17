import os
import django
import random
import uuid
from faker import Faker
from datetime import timedelta

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcity_backend.settings")
django.setup()

from smartcity_backend.api.models import (
    Technicien, Capteur, Intervention, Citoyen, VehiculeAutonome, Trajet, Proprietaire
)

fake = Faker("fr_FR")

def generate_data():
    print("Generating data...")

    # 1. Technicians
    print("- Generating Technicians...")
    technicians = []
    for _ in range(10):
        t = Technicien.objects.create(
            nom=fake.name(),
            certification=True
        )
        technicians.append(t)

    # 2. Owners (Proprietaire) - Needed for Capteur
    print("- Generating Owners...")
    owners = []
    for _ in range(5):
        o = Proprietaire.objects.create(
            nom=fake.company(),
            type_proprietaire=random.choice(['municipalité', 'privé']),
            adresse=fake.address(),
            telephone=fake.phone_number(),
            email=fake.company_email()
        )
        owners.append(o)

    # 3. Sensors (Capteurs)
    print("- Generating Sensors...")
    sensors = []
    sensor_types = ["qualité_air", "trafic", "énergie", "déchets", "éclairage"]
    districts = ["Medina", "Sahloul", "Khezama", "Kalaa Sghira", "Hammam Sousse", "Cité Riadh"]
    for _ in range(50):
        # Sousse Bounding Box approx: 35.80-35.86, 10.58-10.66
        lat = random.uniform(35.8000, 35.8600)
        lon = random.uniform(10.5800, 10.6600)
        
        s = Capteur.objects.create(
            type_capteur=random.choice(sensor_types),
            latitude=lat,
            longitude=lon,
            statut=random.choice(["actif", "en_maintenance", "hors_service"]),
            quartier=random.choice(districts),
            date_installation=fake.date_between(start_date="-2y", end_date="today"),
            proprietaire=random.choice(owners)
        )
        sensors.append(s)

    # 4. Interventions
    print("- Generating Interventions...")
    for _ in range(50):
        # In Django ManyToMany with through model, we create Intervention first, then add techs
        intervention = Intervention.objects.create(
            capteur=random.choice(sensors),
            date_heure=fake.date_time_this_year(tzinfo=django.utils.timezone.get_current_timezone()),
            type_intervention=random.choice(["prédictive", "corrective", "curative"]),
            duree=random.randint(15, 240),
            cout=round(random.uniform(50.0, 500.0), 2),
            impact_co2=round(random.uniform(0.5, 50.0), 2)
        )
        
        # Add technicians
        t1 = random.choice(technicians)
        t2 = random.choice(technicians)
        while t1 == t2:
            t2 = random.choice(technicians)
            
        # We need to import the through model if we want to create it directly, 
        # or use the related manager. Let's use the through model for clarity if accessible,
        # but standard way is:
        from smartcity_backend.api.models import InterventionTechnicien
        InterventionTechnicien.objects.create(intervention=intervention, technicien=t1, role='intervenant')
        InterventionTechnicien.objects.create(intervention=intervention, technicien=t2, role='validateur')

    # 5. Citizens
    print("- Generating Citizens...")
    for _ in range(100):
        Citoyen.objects.create(
            nom=fake.name(),
            adresse=fake.address(),
            email=fake.unique.email(),
            telephone=fake.phone_number(),
            score_ecologique=random.randint(0, 100),
            preferences_mobilite=random.choice(["Vélo", "Marche", "Transports en commun", "Véhicule électrique"])
        )

    # 6. Vehicles
    print("- Generating Vehicles...")
    vehicles = []
    for _ in range(20):
        v_id = fake.license_plate()
        # Check if exists to avoid unique constraint error (though create usually fails)
        # Using get_or_create is safer
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
            end = start + timedelta(minutes=random.randint(10, 120))
            
            Trajet.objects.create(
                vehicule=random.choice(vehicles),
                origine=fake.address(),
                destination=fake.address(),
                duree=int((end - start).total_seconds() / 60), # Calculate duration
                economie_co2=round(random.uniform(1.0, 15.0), 2)
            )

    print("Data generation complete!")

if __name__ == "__main__":
    generate_data()
