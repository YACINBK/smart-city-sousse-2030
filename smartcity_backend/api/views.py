from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import (
    Proprietaire, Capteur, Technicien, Intervention,
    Citoyen, Consultation, VehiculeAutonome, Trajet
)
from .serializers import (
    ProprietaireSerializer, CapteurSerializer, TechnicienSerializer,
    InterventionSerializer, CitoyenSerializer, ConsultationSerializer,
    VehiculeAutonomeSerializer, TrajetSerializer
)
from .services import simulate_system_step

class ProprietaireViewSet(viewsets.ModelViewSet):
    queryset = Proprietaire.objects.all()
    serializer_class = ProprietaireSerializer

class CapteurViewSet(viewsets.ModelViewSet):
    queryset = Capteur.objects.select_related("proprietaire").all()
    serializer_class = CapteurSerializer

class TechnicienViewSet(viewsets.ModelViewSet):
    queryset = Technicien.objects.all()
    serializer_class = TechnicienSerializer

class InterventionViewSet(viewsets.ModelViewSet):
    queryset = Intervention.objects.select_related("capteur").prefetch_related("techniciens")
    serializer_class = InterventionSerializer

class CitoyenViewSet(viewsets.ModelViewSet):
    queryset = Citoyen.objects.all()
    serializer_class = CitoyenSerializer

class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.prefetch_related("participants")
    serializer_class = ConsultationSerializer

class VehiculeAutonomeViewSet(viewsets.ModelViewSet):
    queryset = VehiculeAutonome.objects.all()
    serializer_class = VehiculeAutonomeSerializer

class TrajetViewSet(viewsets.ModelViewSet):
    queryset = Trajet.objects.select_related("vehicule")
    serializer_class = TrajetSerializer

@api_view(['POST'])
def simulate_step(request):
    summary = simulate_system_step()
    return Response(
        {
            "status": "Simulation step complete",
            "sensor_updates": summary["sensor_updates"],
            "trips_created": summary["trips_created"],
            "interventions_created": summary["interventions_created"],
            "timestamp": summary["timestamp"],
        }
    )
