from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProprietaireViewSet, CapteurViewSet, TechnicienViewSet, 
    InterventionViewSet, CitoyenViewSet, ConsultationViewSet, 
    VehiculeAutonomeViewSet, TrajetViewSet, simulate_step
)

router = DefaultRouter()
router.register(r'proprietaires', ProprietaireViewSet)
router.register(r'capteurs', CapteurViewSet)
router.register(r'techniciens', TechnicienViewSet)
router.register(r'interventions', InterventionViewSet)
router.register(r'citoyens', CitoyenViewSet)
router.register(r'consultations', ConsultationViewSet)
router.register(r'vehicules', VehiculeAutonomeViewSet)
router.register(r'trajets', TrajetViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('simulate/', simulate_step, name='simulate-step'),
]
