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
