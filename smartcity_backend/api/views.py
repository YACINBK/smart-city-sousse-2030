from rest_framework import viewsets
from .models import (
    Proprietaire, Capteur, Technicien, Intervention, 
    Citoyen, Consultation, VehiculeAutonome, Trajet
)
from .serializers import (
    ProprietaireSerializer, CapteurSerializer, TechnicienSerializer, 
    InterventionSerializer, CitoyenSerializer, ConsultationSerializer, 
    VehiculeAutonomeSerializer, TrajetSerializer
)

class ProprietaireViewSet(viewsets.ModelViewSet):
    queryset = Proprietaire.objects.all()
    serializer_class = ProprietaireSerializer

class CapteurViewSet(viewsets.ModelViewSet):
    queryset = Capteur.objects.all()
    serializer_class = CapteurSerializer

class TechnicienViewSet(viewsets.ModelViewSet):
    queryset = Technicien.objects.all()
    serializer_class = TechnicienSerializer

class InterventionViewSet(viewsets.ModelViewSet):
    queryset = Intervention.objects.all()
    serializer_class = InterventionSerializer

class CitoyenViewSet(viewsets.ModelViewSet):
    queryset = Citoyen.objects.all()
    serializer_class = CitoyenSerializer

class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer

class VehiculeAutonomeViewSet(viewsets.ModelViewSet):
    queryset = VehiculeAutonome.objects.all()
    serializer_class = VehiculeAutonomeSerializer

class TrajetViewSet(viewsets.ModelViewSet):
    queryset = Trajet.objects.all()
    serializer_class = TrajetSerializer

# --- Smart Simulation Logic (Added for On-Demand Button) ---
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
import random
import math

DISTRICT_CENTERS = {
    "Ennfidha": (36.130, 10.380), "Hergla": (36.030, 10.500), "Sidi Bou Ali": (35.950, 10.470),
    "Kondar": (35.920, 10.300), "Akouda": (35.870, 10.560), "Kalaa Kebira": (35.870, 10.530),
    "Hammam Sousse": (35.860, 10.590), "Sousse Ville": (35.825, 10.635), "Sousse Jawhara": (35.810, 10.620),
    "Sousse Riadh": (35.800, 10.600), "Sidi Abdelhamid": (35.800, 10.640), "Kalaa Sghira": (35.820, 10.550),
    "Zaouia Ksiba Thrayet": (35.780, 10.630), "Msaken": (35.730, 10.580), "Sidi El Heni": (35.670, 10.320),
}

def get_gaussian_coords(district):
    if district not in DISTRICT_CENTERS: district = "Sousse Ville"
    lat, lon = DISTRICT_CENTERS[district]
    return random.gauss(lat, 0.01), random.gauss(lon, 0.01)

@api_view(['POST'])
def simulate_step(request):
    """
    Triggers a 'Time Step' with HIGH INTENSITY.
    1. Updates ~10-15% of all sensors (Chaos & Repairs).
    2. Generates Heavy Traffic (10-25 Trips).
    3. Dispatches Repairs aggressively.
    """
    log = []
    
    # 1. Update Sensors (Global Flux)
    sensors = list(Capteur.objects.all())
    for s in sensors:
        # 20% chance to change status per sensor (Higher Chaos)
        if random.random() < 0.20:
            old = s.statut
            # Smart Weighting: Make it truly random/dynamic
            if s.quartier == 'Sousse Ville':
                # Volatile Center
                new_s = random.choices(['actif', 'en_maintenance', 'hors_service'], weights=[0.5, 0.25, 0.25])[0]
            else:
                new_s = random.choices(['actif', 'en_maintenance', 'hors_service'], weights=[0.6, 0.2, 0.2])[0]
            
            if old != new_s:
                s.statut = new_s
                s.save()

    # 2. Generate Heavy Traffic
    vehicles = list(VehiculeAutonome.objects.all())
    if vehicles:
        for _ in range(random.randint(10, 25)): # 10 to 25 trips
            v = random.choice(vehicles)
            q_start = random.choice(list(DISTRICT_CENTERS.keys()))
            q_end = random.choice(list(DISTRICT_CENTERS.keys()))
            
            Trajet.objects.create(
                vehicule=v, origine=f"Simulated ({q_start})", destination=f"Simulated ({q_end})",
                duree=random.randint(10, 60), economie_co2=round(random.uniform(0.5, 5.0), 2)
            )

    # 3. Auto-Intervention (Aggressive)
    broken_sensors = Capteur.objects.filter(statut='hors_service')
    for s in broken_sensors:
        if random.random() < 0.4: # 40% chance to dispatch fix
            Intervention.objects.create(
                capteur=s, date_heure=timezone.now(), type_intervention='corrective',
                duree=random.randint(60, 180), cout=random.uniform(200, 500), impact_co2=5.5
            )
            s.statut = 'en_maintenance'
            s.save()

    return Response({"status": "Simulation Step Complete", "log": "Intensity High"})
