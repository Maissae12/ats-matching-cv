from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CV, Offre, Score
from .serializers import CVSerializer, OffreSerializer, ScoreSerializer
from .services import calculer_et_sauvegarder_score


def page_ajouter_offre(request):
    return render(request, "matching/ajouter_offre.html")


def page_liste_cvs(request):
    return render(request, "matching/liste_cvs.html")


def page_modifier_offre(request, offre_id):
    return render(request, "matching/modifier_offre.html", {"offre_id": offre_id})


def page_accueil(request):
    return render(request, "matching/accueil.html")


def page_liste_offres(request):
    return render(request, "matching/liste_offres.html")


def page_classement(request, offre_id):
    """
    Vue qui affiche juste la page HTML vide.
    Le calcul et l'affichage des données se font en JavaScript, via l'API.
    """
    return render(request, "matching/classement_api.html", {"offre_id": offre_id})


def page_upload_cv(request):
    return render(request, "matching/upload_cv.html")


class CVViewSet(viewsets.ModelViewSet):
    queryset = CV.objects.all()
    serializer_class = CVSerializer


class OffreViewSet(viewsets.ModelViewSet):
    queryset = Offre.objects.all()
    serializer_class = OffreSerializer

    @action(detail=True, methods=['get'])
    def classement(self, request, pk=None):
        """
        Endpoint API : /api/offres/{id}/classement/
        Recalcule uniquement si nécessaire (nouveau CV, ou offre modifiée).
        Les CV dont le score ne peut pas être calculé (texte vide, erreur,
        fichier manquant sur le disque, etc.) sont exclus du classement et
        listés séparément, sans faire planter toute la requête (500).
        """
        offre = self.get_object()
        tous_les_cvs = CV.objects.filter(offre=offre)

        resultats = []
        erreurs = []

        for cv in tous_les_cvs:
            try:
                score_obj = Score.objects.filter(cv=cv, offre=offre).first()

                besoin_recalcul = (
                    score_obj is None
                    or cv.date_upload > score_obj.date_calcul
                    or offre.date_modification > score_obj.date_calcul
                )

                if besoin_recalcul:
                    score_obj = calculer_et_sauvegarder_score(cv, offre)

                resultats.append(score_obj)

            except FileNotFoundError:
                # Le fichier existe en base mais plus sur le disque
                # (supprimé, déplacé, ou changement de MEDIA_ROOT)
                erreurs.append({
                    "cv": cv.nom_candidat,
                    "erreur": "Fichier CV introuvable sur le serveur "
                              "(a-t-il été supprimé ou déplacé après l'upload ?)."
                })

            except ValueError as e:
                erreurs.append({"cv": cv.nom_candidat, "erreur": str(e)})

            except Exception as e:
                # Filet de sécurité : toute autre erreur imprévue sur un CV
                # ne doit jamais faire planter l'affichage des autres candidats.
                erreurs.append({"cv": cv.nom_candidat, "erreur": f"Erreur inattendue : {e}"})

        resultats_tries = sorted(resultats, key=lambda s: s.score_final, reverse=True)
        serializer = ScoreSerializer(resultats_tries, many=True)

        return Response({
            "resultats": serializer.data,
            "erreurs": erreurs
        })


class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer