# Smart City Sousse 2030

Smart City Sousse 2030 is an academic databases project built around a smart-city scenario for the governorate of Sousse. The system combines a Django backend, a REST API, generated urban data, and a Streamlit dashboard for monitoring sensors, maintenance activity, citizens, and ecological mobility.

## Stack

- Django and Django REST Framework
- Streamlit, Plotly, and Folium
- SQLite
- Faker for synthetic data generation

## Main Features

- relational data model for sensors, interventions, citizens, consultations, vehicles, and trips
- REST API for all main entities
- synthetic data generation for demos and testing
- real-time simulation step for sensor status changes and trip creation
- dashboard with live map, KPIs, and analytics views

## Screenshots

![Dashboard overview](docs/screenshots/dashboard_overview.png)

![Analytics view](docs/screenshots/analytics_view.png)

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python scripts/generate_data.py
./launch.sh
```

Open:

- Dashboard: `http://127.0.0.1:8501`
- API: `http://127.0.0.1:8000/api/`
- Admin: `http://127.0.0.1:8000/admin/`


## Project Structure

```text
smart-city-sousse-2030/
├── dashboard.py
├── docs/
│   ├── references/
│   ├── reports/
│   └── screenshots/
├── launch.sh
├── logs/
├── scripts/
│   ├── generate_data.py
│   ├── simulate_realtime.py
│   └── test_debug.py
└── smartcity_backend/
    ├── settings.py
    ├── urls.py
    └── api/
        ├── models.py
        ├── serializers.py
        ├── services.py
        ├── tests.py
        ├── urls.py
        └── views.py
```

## Database Scope

Core entities:

- `Capteur`
- `Intervention`
- `Technicien`
- `Citoyen`
- `Consultation`
- `Participation`
- `VehiculeAutonome`
- `Trajet`

The backend includes indexes, integrity constraints, and validation rules to make the database model more consistent and usable for coursework. Academic reports, references, and screenshots are grouped under `docs/`.


## Authors

- Yacin Ben Kacem
- Oussema Ben Ameur

## Note

This repository is intended for academic use in a databases course.
