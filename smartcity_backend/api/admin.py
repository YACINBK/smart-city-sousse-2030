from django.contrib import admin

from .models import (
    Capteur,
    Citoyen,
    Consultation,
    Intervention,
    Participation,
    Proprietaire,
    Technicien,
    Trajet,
    VehiculeAutonome,
)


@admin.register(Proprietaire)
class ProprietaireAdmin(admin.ModelAdmin):
    list_display = ("nom", "type_proprietaire", "email", "telephone")
    search_fields = ("nom", "email")


@admin.register(Capteur)
class CapteurAdmin(admin.ModelAdmin):
    list_display = ("id_capteur", "type_capteur", "quartier", "statut", "date_installation")
    list_filter = ("type_capteur", "statut", "quartier")
    search_fields = ("quartier",)


@admin.register(Technicien)
class TechnicienAdmin(admin.ModelAdmin):
    list_display = ("nom", "certification")
    list_filter = ("certification",)
    search_fields = ("nom",)


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ("id_intervention", "capteur", "type_intervention", "date_heure", "cout")
    list_filter = ("type_intervention",)
    search_fields = ("capteur__quartier", "capteur__type_capteur")
    autocomplete_fields = ("capteur", "techniciens")


@admin.register(Citoyen)
class CitoyenAdmin(admin.ModelAdmin):
    list_display = ("nom", "email", "score_ecologique")
    search_fields = ("nom", "email")
    list_filter = ("preferences_mobilite",)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("titre", "statut", "date_debut", "date_fin")
    list_filter = ("statut",)
    search_fields = ("titre", "description")


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("citoyen", "consultation", "date_participation")
    autocomplete_fields = ("citoyen", "consultation")


@admin.register(VehiculeAutonome)
class VehiculeAutonomeAdmin(admin.ModelAdmin):
    list_display = ("plaque_immatriculation", "type_vehicule", "energie_utilisee")
    list_filter = ("type_vehicule", "energie_utilisee")
    search_fields = ("plaque_immatriculation",)


@admin.register(Trajet)
class TrajetAdmin(admin.ModelAdmin):
    list_display = ("vehicule", "origine", "destination", "duree", "economie_co2")
    search_fields = ("origine", "destination", "vehicule__plaque_immatriculation")
    autocomplete_fields = ("vehicule",)
