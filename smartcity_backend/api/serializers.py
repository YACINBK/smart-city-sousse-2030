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
    def validate(self, attrs):
        date_debut = attrs.get("date_debut", getattr(self.instance, "date_debut", None))
        date_fin = attrs.get("date_fin", getattr(self.instance, "date_fin", None))
        if date_debut and date_fin and date_fin < date_debut:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin doit etre posterieure a la date de debut."}
            )
        return attrs

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
