import psycopg2
from faker import Faker
import random
import uuid
import os

# Configuration
# Tries to get from env vars (for Docker), defaults to localhost (for local run)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5433")  # Default to new port 5433
DB_NAME = os.environ.get("DB_NAME", "smartcity")
DB_USER = os.environ.get("DB_USER", "smartuser")
DB_PASS = os.environ.get("DB_PASS", "smartpass")

fake = Faker("fr_FR")  # Use French locale


def get_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def generate_data():
    conn = get_connection()
    if not conn:
        return

    cur = conn.cursor()

    print("Generating data...")

    # 1. Technicians
    technician_ids = []
    print("- Generating Technicians...")
    for _ in range(10):
        t_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO techniciens (id_technicien, nom, specialite, certifie) VALUES (%s, %s, %s, %s)",
            (
                t_id,
                fake.name(),
                random.choice(["Électrique", "Réseau", "Mécanique", "Capteurs"]),
                True,
            ),
        )
        technician_ids.append(t_id)

    # 2. Sensors (Capteurs)
    sensor_ids = []
    print("- Generating Sensors...")
    sensor_types = ["qualité_air", "trafic", "énergie", "déchets", "éclairage"]
    for _ in range(50):
        s_id = str(uuid.uuid4())
        cur.execute(
            """INSERT INTO capteurs 
            (id_capteur, type_capteur, latitude, longitude, statut, proprietaire_type, nom_proprietaire, adresse_proprietaire, telephone_proprietaire, email_proprietaire, date_installation) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                s_id,
                random.choice(sensor_types),
                fake.latitude(),
                fake.longitude(),
                random.choice(["actif", "en_maintenance", "hors_service"]),
                random.choice(["municipalité", "privé"]),
                fake.company(),
                fake.address(),
                fake.phone_number(),
                fake.company_email(),
                fake.date_between(start_date="-2y", end_date="today"),
            ),
        )
        sensor_ids.append(s_id)

    # 3. Interventions
    print("- Generating Interventions...")
    for _ in range(50):
        t1 = random.choice(technician_ids)
        t2 = random.choice(technician_ids)
        while t1 == t2:  # Ensure different validator
            t2 = random.choice(technician_ids)

        cur.execute(
            """INSERT INTO interventions 
            (id_capteur, date_heure, type_intervention, duree_minutes, cout, impact_environnemental_co2, id_technicien_intervenant, id_technicien_validateur) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                random.choice(sensor_ids),
                fake.date_time_this_year(),
                random.choice(["prédictive", "corrective", "curative"]),
                random.randint(15, 240),
                round(random.uniform(50.0, 500.0), 2),
                round(random.uniform(0.5, 50.0), 2),
                t1,
                t2,
            ),
        )

    # 4. Citizens
    print("- Generating Citizens...")
    for _ in range(100):
        cur.execute(
            """INSERT INTO citoyens 
            (nom, adresse, email, telephone, score_ecologique, preferences_mobilite) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                fake.name(),
                fake.address(),
                fake.unique.email(),
                fake.phone_number(),
                random.randint(0, 100),
                random.choice(
                    ["Vélo", "Marche", "Transports en commun", "Véhicule électrique"]
                ),
            ),
        )

    # 5. Vehicles
    vehicle_ids = []
    print("- Generating Vehicles...")
    for _ in range(20):
        v_id = fake.license_plate()
        cur.execute(
            "INSERT INTO vehicules (immatriculation, type_vehicule, energie_utilisee) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            (v_id, random.choice(["Bus", "Navette", "Voiture"]), "Électrique"),
        )
        vehicle_ids.append(v_id)

    # 6. Trips (Trajets)
    print("- Generating Trips...")
    for _ in range(50):
        if not vehicle_ids:
            break
        start = fake.date_time_this_month()
        end = fake.date_time_between(start_date=start, end_date="+2h")

        cur.execute(
            """INSERT INTO trajets 
            (immatriculation, origine, destination, date_depart, date_arrivee, economie_co2) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                random.choice(vehicle_ids),
                fake.secondary_address(),
                fake.secondary_address(),
                start,
                end,
                round(random.uniform(1.0, 15.0), 2),
            ),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("Data generation complete!")


if __name__ == "__main__":
    generate_data()
