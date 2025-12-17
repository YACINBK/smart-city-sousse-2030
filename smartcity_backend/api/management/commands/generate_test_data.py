from django.core.management.base import BaseCommand
from smartcity_backend.api.models import (
    Proprietaire, Capteur, Technicien, Intervention,
    Citoyen, VehiculeAutonome, Trajet, InterventionTechnicien,
    Participation, Consultation
)
from faker import Faker
import random
import uuid
from django.utils import timezone
import unidecode

class Command(BaseCommand):
    help = 'Generates Tunisian-specific synthetic data for the Smart City platform'

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning old data...")
        # Delete in order of dependencies (child first)
        Trajet.objects.all().delete()
        InterventionTechnicien.objects.all().delete()
        Intervention.objects.all().delete()
        Capteur.objects.all().delete()
        Proprietaire.objects.all().delete()
        Technicien.objects.all().delete()
        Participation.objects.all().delete()
        Consultation.objects.all().delete()
        Citoyen.objects.all().delete()
        VehiculeAutonome.objects.all().delete()

        self.stdout.write("Initializing data generation...")
        fake = Faker('fr_FR') # Base for generic text, but we use custom lists

        # --- Custom Data Sources ---
        TUNISIAN_FIRST_NAMES = [
            'Mohamed', 'Ahmed', 'Youssef', 'Aziz', 'Amine', 'Omar', 'Karim', 'Sami', 'Nizar', 'Walid',
            'Fatma', 'Myriam', 'Amel', 'Sarra', 'Yasmine', 'Hela', 'Nour', 'Rym', 'Leila', 'Safa'
        ]
        TUNISIAN_LAST_NAMES = [
            'Trabelsi', 'Gharbi', 'Ben Ali', 'Hammamy', 'Jaziri', 'Mabrouk', 'Zarrouk', 'Driss', 'Ben Amor', 'Sassi',
            'Bouazizi', 'Khemiri', 'Mejri', 'Chahed', 'Ghanem', 'Rezgui'
        ]
        SOUSSE_DISTRICTS = [
            'Sahloul', 'Khezama Est', 'Khezama Ouest', 'Hammam Sousse', 'Akouda', 'Kalaa Kebira', 'Kalaa Seghira',
            'La Medina', 'Bouhsina', 'Trocadero', 'Corniche', 'El Kantaoui', 'Sidi Boujaafar'
        ]

        def get_tunisian_name():
            return f"{random.choice(TUNISIAN_FIRST_NAMES)} {random.choice(TUNISIAN_LAST_NAMES)}"

        def get_tunisian_phone():
            prefix = random.choice(['50', '51', '52', '53', '54', '55', '56', '57', '58', '59', 
                                    '20', '21', '22', '23', '24', '25', '26', '27', '28', '29',
                                    '90', '91', '92', '93', '94', '95', '96', '97', '98', '99',
                                    '40', '41', '42', '43', '44', '45', '46', '47', '48', '49'])
            return f"+216 {prefix} {random.randint(100,999)} {random.randint(100,999)}"

        def get_sousse_address():
            street_type = random.choice(['Rue', 'Avenue', 'Boulevard', 'Impasse'])
            street_name = random.choice(['de la République', 'du 14 Janvier', 'Ibn Khaldoun', 'Hanniabal', 'Okba Ibn Nafaa', 'de l\'Indépendance', 'Taha Hussein', 'Imam Sahnoun'])
            district = random.choice(SOUSSE_DISTRICTS)
            zip_code = random.choice(['4000', '4051', '4011', '4002', '4089'])
            return f"{random.randint(1, 150)} {street_type} {street_name}, {district}, {zip_code} Sousse"

        def generate_email(name):
            normalized = unidecode.unidecode(name.lower().replace(' ', '.'))
            domain = random.choice(['gmail.com', 'yahoo.fr', 'topnet.tn', 'gnet.tn'])
            # Add random digits to ensure uniqueness
            return f"{normalized}.{random.randint(1, 9999)}@{domain}"

        # 1. Proprietaires
        self.stdout.write("- Generating Proprietaires...")
        proprietaires = []
        for _ in range(5):
            is_muni = random.choice([True, False])
            name = "Mairie de Sousse" if is_muni else f"Société {random.choice(['Tech', 'Eco', 'Light'])} {random.choice(['Sud', 'Sahel', 'Tunisie'])}"
            p = Proprietaire.objects.create(
                nom=name,
                type_proprietaire='municipalité' if is_muni else 'privé',
                adresse=get_sousse_address(),
                telephone=get_tunisian_phone(),
                email=generate_email(name)
            )
            proprietaires.append(p)

        # 2. Technicians
        self.stdout.write("- Generating Technicians...")
        technicians = []
        for _ in range(10):
            t = Technicien.objects.create(
                nom=get_tunisian_name(),
                certification=True
            )
            technicians.append(t)

        # 3. Sensors (Capteurs)
        self.stdout.write("- Generating Sensors...")
        sensors = []
        sensor_types = ['qualité_air', 'trafic', 'énergie', 'déchets', 'éclairage']
        # Sousse "District Anchors" to ensure land placement and distribution
        # (Lat, Lon) centers for main neighborhoods
        DISTRICT_ANCHORS = [
            (35.8245, 10.6345), # Medina / Centre Ville (Inland from port)
            (35.8360, 10.5900), # Sahloul (Safe inland)
            (35.8450, 10.6200), # Khezama (Residential)
            (35.8180, 10.5500), # Kalaa Sghira (Further west)
            (35.8550, 10.6050), # Hammam Sousse / Akouda border
            (35.8050, 10.6100), # Cité Riadh / Sud
        ]

        for _ in range(120):
            # Pick a random district
            anchor_lat, anchor_lon = random.choice(DISTRICT_ANCHORS)
            
            # Add small random offset (approx +/- 500m)
            # 0.005 degrees is roughly 500m
            lat = anchor_lat + random.uniform(-0.004, 0.004)
            lon = anchor_lon + random.uniform(-0.004, 0.004)

            # Weighted status: 80% Actif
            statut = random.choices(['actif', 'en_maintenance', 'hors_service'], weights=[80, 15, 5])[0]

            s = Capteur.objects.create(
                type_capteur=random.choice(sensor_types),
                latitude=lat,
                longitude=lon,
                statut=statut,
                date_installation=fake.date_between(start_date='-2y', end_date='today'),
                proprietaire=random.choice(proprietaires)
            )
            sensors.append(s)

        # 4. Interventions
        self.stdout.write("- Generating Interventions...")
        for _ in range(50):
            sensor = random.choice(sensors)
            t_worker = random.choice(technicians)
            t_validator = random.choice(technicians)
            while t_validator == t_worker:
                t_validator = random.choice(technicians)

            intervention = Intervention.objects.create(
                capteur=sensor,
                date_heure=timezone.make_aware(fake.date_time_this_year()),
                type_intervention=random.choice(['prédictive', 'corrective', 'curative']),
                duree=random.randint(15, 240),
                cout=round(random.uniform(50.0, 500.0), 2),
                impact_co2=round(random.uniform(0.5, 50.0), 2)
            )
            
            InterventionTechnicien.objects.create(intervention=intervention, technicien=t_worker, role='intervenant')
            InterventionTechnicien.objects.create(intervention=intervention, technicien=t_validator, role='validateur')

        # 5. Citizens
        self.stdout.write("- Generating Citizens...")
        for _ in range(100):
            name = get_tunisian_name()
            Citoyen.objects.create(
                nom=name,
                adresse=get_sousse_address(),
                email=generate_email(name),
                telephone=get_tunisian_phone(),
                score_ecologique=random.randint(0, 100),
                preferences_mobilite=random.choice(['Vélo', 'Marche', 'Transports en commun', 'Véhicule électrique'])
            )

        # 6. Vehicles
        self.stdout.write("- Generating Vehicles...")
        vehicles = []
        used_plates = set()
        
        while len(vehicles) < 20:
            # x TU y format
            x = random.randint(240, 259) # [240..259]
            y = random.randint(1, 9999)
            plate = f"{x} TU {y}"
            
            if plate not in used_plates:
                used_plates.add(plate)
                v = VehiculeAutonome.objects.create(
                    plaque_immatriculation=plate,
                    type_vehicule=random.choice(['Bus', 'Navette', 'Voiture']),
                    energie_utilisee='Électrique'
                )
                vehicles.append(v)

        # 7. Trips (Trajets)
        self.stdout.write("- Generating Trips...")
        for _ in range(50):
            if not vehicles: break
            Trajet.objects.create(
                vehicule=random.choice(vehicles),
                origine=get_sousse_address(),
                destination=get_sousse_address(),
                duree=random.randint(5, 60),
                economie_co2=round(random.uniform(1.0, 15.0), 2)
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated Tunisian synthetic data!'))
