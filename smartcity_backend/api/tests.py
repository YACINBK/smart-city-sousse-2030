from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from .models import (
    Capteur,
    Consultation,
    Intervention,
    InterventionTechnicien,
    Proprietaire,
    Technicien,
    Trajet,
    VehiculeAutonome,
)
from .services import simulate_system_step


class ConsultationModelTests(TestCase):
    def test_consultation_rejects_invalid_date_range(self):
        consultation = Consultation(
            titre="Projet test",
            description="Validation de dates",
            date_debut=date.today(),
            date_fin=date.today() - timedelta(days=1),
            statut="ouverte",
        )

        with self.assertRaises(ValidationError):
            consultation.full_clean()


class SimulationServiceTests(TestCase):
    def setUp(self):
        self.owner = Proprietaire.objects.create(
            nom="Mairie de Sousse",
            type_proprietaire="municipalité",
            adresse="Sousse",
            telephone="+216 20 000 000",
            email="mairie@example.com",
        )
        self.sensor = Capteur.objects.create(
            type_capteur="trafic",
            latitude=Decimal("35.825000"),
            longitude=Decimal("10.635000"),
            statut="actif",
            quartier="Sousse Ville",
            date_installation=date.today(),
            proprietaire=self.owner,
        )
        self.vehicle = VehiculeAutonome.objects.create(
            plaque_immatriculation="123 TU 4567",
            type_vehicule="Navette",
            energie_utilisee="Electrique",
        )

    @patch("smartcity_backend.api.services.random.uniform", side_effect=[1.2, 250.0])
    @patch(
        "smartcity_backend.api.services.random.choice",
        side_effect=lambda sequence: sequence[0],
    )
    @patch(
        "smartcity_backend.api.services.random.randint",
        side_effect=[1, 15, 120],
    )
    @patch(
        "smartcity_backend.api.services.random.choices",
        return_value=["hors_service"],
    )
    @patch(
        "smartcity_backend.api.services.random.random",
        side_effect=[0.1, 0.1],
    )
    def test_simulation_step_updates_sensor_and_creates_records(
        self,
        mock_random,
        mock_choices,
        mock_randint,
        mock_choice,
        mock_uniform,
    ):
        summary = simulate_system_step()

        self.sensor.refresh_from_db()

        self.assertEqual(summary["sensor_updates"], 1)
        self.assertEqual(summary["trips_created"], 1)
        self.assertEqual(summary["interventions_created"], 1)
        self.assertEqual(self.sensor.statut, "en_maintenance")
        self.assertEqual(Trajet.objects.count(), 1)
        self.assertEqual(Intervention.objects.count(), 1)


class ApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = Proprietaire.objects.create(
            nom="Societe Sahel Services",
            type_proprietaire="privé",
            adresse="Sousse",
            telephone="+216 50 111 111",
            email="contact@example.com",
        )
        self.sensor = Capteur.objects.create(
            type_capteur="qualité_air",
            latitude=Decimal("35.830000"),
            longitude=Decimal("10.620000"),
            statut="actif",
            quartier="Sousse Jawhara",
            date_installation=date.today(),
            proprietaire=self.owner,
        )

    def test_interventions_endpoint_returns_nested_technicians(self):
        intervention = Intervention.objects.create(
            capteur=self.sensor,
            date_heure="2026-01-01T10:00:00Z",
            type_intervention="corrective",
            duree=45,
            cout=Decimal("120.00"),
            impact_co2=Decimal("3.50"),
        )
        technician = Technicien.objects.create(nom="Ahmed Trabelsi", certification=True)
        InterventionTechnicien.objects.create(
            intervention=intervention,
            technicien=technician,
            role="intervenant",
        )

        response = self.client.get("/api/interventions/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["techniciens"][0]["nom"], "Ahmed Trabelsi")

    @patch("smartcity_backend.api.views.simulate_system_step")
    def test_simulate_endpoint_returns_summary(self, mock_simulate):
        mock_simulate.return_value = {
            "sensor_updates": 2,
            "trips_created": 3,
            "interventions_created": 1,
            "timestamp": "2026-04-11T12:00:00Z",
        }

        response = self.client.post("/api/simulate/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "Simulation step complete",
                "sensor_updates": 2,
                "trips_created": 3,
                "interventions_created": 1,
                "timestamp": "2026-04-11T12:00:00Z",
            },
        )
