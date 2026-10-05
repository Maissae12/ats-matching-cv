from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cvs', views.CVViewSet)
router.register(r'offres', views.OffreViewSet)
router.register(r'scores', views.ScoreViewSet)

urlpatterns = [
path('page-classement/<int:offre_id>/', views.page_classement, name='page_classement'),
path('api/', include(router.urls)),
path('upload-cv/', views.page_upload_cv, name='page_upload_cv'),
path('offres/', views.page_liste_offres, name='page_liste_offres'),
path('cvs/', views.page_liste_cvs, name='page_liste_cvs'),
path('ajouter-offre/', views.page_ajouter_offre, name='page_ajouter_offre'),
path('modifier-offre/<int:offre_id>/', views.page_modifier_offre, name='page_modifier_offre'),
path('', views.page_accueil, name='page_accueil'),
]