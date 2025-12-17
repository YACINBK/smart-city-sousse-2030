from rest_framework import serializers
from .models import (
    Proprietaire, Capteur, Technicien, Intervention, 
    Citoyen, Consultation, VehiculeAutonome, Trajet,
    InterventionTechnicien, Participation
)

class ProprietaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proprietaire
        fields = '__all__'

class CapteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capteur
        fields = '__all__'

class TechnicienSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technicien
        fields = '__all__'

class InterventionSerializer(serializers.ModelSerializer):
    techniciens = TechnicienSerializer(many=True, read_only=True)
    
    class Meta:
        model = Intervention
        fields = '__all__'

class CitoyenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citoyen
        fields = '__all__'

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = '__all__'

class VehiculeAutonomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculeAutonome
        fields = '__all__'

class TrajetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trajet
        fields = '__all__'
