from django.db import models
import uuid

class Proprietaire(models.Model):
    TYPE_CHOICES = [
        ('municipalité', 'Municipalité'),
        ('privé', 'Privé'),
    ]
    id_proprietaire = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    type_proprietaire = models.CharField(max_length=20, choices=TYPE_CHOICES)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.nom

class Capteur(models.Model):
    TYPE_CHOICES = [
        ('qualité_air', 'Qualité Air'),
        ('trafic', 'Trafic'),
        ('énergie', 'Énergie'),
        ('déchets', 'Déchets'),
        ('éclairage', 'Éclairage'),
    ]
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('en_maintenance', 'En Maintenance'),
        ('hors_service', 'Hors Service'),
    ]
    id_capteur = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_capteur = models.CharField(max_length=50, choices=TYPE_CHOICES)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES)
    date_installation = models.DateField()
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.CASCADE, related_name='capteurs')

    def __str__(self):
        return f"{self.type_capteur} ({self.statut})"

class Technicien(models.Model):
    id_technicien = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    certification = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

class Intervention(models.Model):
    TYPE_CHOICES = [
        ('prédictive', 'Prédictive'),
        ('corrective', 'Corrective'),
        ('curative', 'Curative'),
    ]
    id_intervention = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    capteur = models.ForeignKey(Capteur, on_delete=models.CASCADE, related_name='interventions')
    date_heure = models.DateTimeField()
    type_intervention = models.CharField(max_length=20, choices=TYPE_CHOICES)
    duree = models.IntegerField(help_text="Durée en minutes")
    cout = models.DecimalField(max_digits=10, decimal_places=2)
    impact_co2 = models.DecimalField(max_digits=10, decimal_places=2, help_text="Impact CO2 en kg")
    
    # ManyToMany with Technicians through a custom table to handle roles
    techniciens = models.ManyToManyField(Technicien, through='InterventionTechnicien')

    def __str__(self):
        return f"{self.type_intervention} on {self.date_heure}"

class InterventionTechnicien(models.Model):
    ROLE_CHOICES = [
        ('intervenant', 'Intervenant'),
        ('validateur', 'Validateur'),
    ]
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)
    technicien = models.ForeignKey(Technicien, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class Citoyen(models.Model):
    id_citoyen = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    score_ecologique = models.IntegerField(default=0)
    preferences_mobilite = models.TextField(help_text="Préférences de mobilité (JSON ou texte)")

    def __str__(self):
        return self.nom

class Consultation(models.Model):
    id_consultation = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    theme = models.CharField(max_length=200)
    date_consultation = models.DateField()
    participants = models.ManyToManyField(Citoyen, through='Participation')

    def __str__(self):
        return self.theme

class Participation(models.Model):
    citoyen = models.ForeignKey(Citoyen, on_delete=models.CASCADE)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    date_participation = models.DateTimeField(auto_now_add=True)

class VehiculeAutonome(models.Model):
    id_vehicule = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plaque_immatriculation = models.CharField(max_length=20, unique=True)
    type_vehicule = models.CharField(max_length=50)
    energie_utilisee = models.CharField(max_length=50)

    def __str__(self):
        return self.plaque_immatriculation

class Trajet(models.Model):
    id_trajet = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicule = models.ForeignKey(VehiculeAutonome, on_delete=models.CASCADE, related_name='trajets')
    origine = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    duree = models.IntegerField(help_text="Durée en minutes")
    economie_co2 = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.origine} -> {self.destination}"
