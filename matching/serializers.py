from rest_framework import serializers
from .models import CV, Offre, Score
import os


class CVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = ['id', 'nom_candidat', 'email', 'telephone', 'linkedin', 'github',
                  'gitlab', 'portfolio', 'behance', 'adresse', 'fichier', 'offre', 'date_upload']

    def validate_fichier(self, valeur):
        extension = os.path.splitext(valeur.name)[1].lower()
        if extension not in ['.pdf', '.txt']:
            raise serializers.ValidationError(
                "Seuls les fichiers PDF ou TXT sont acceptés."
            )

        taille_max_mo = 5
        if valeur.size > taille_max_mo * 1024 * 1024:
            raise serializers.ValidationError(
                f"Le fichier dépasse la taille maximale autorisée ({taille_max_mo} Mo)."
            )

        return valeur

    def validate(self, donnees):
        # .get() au lieu de [...] : évite un KeyError si 'fichier' est absent
        # (cas d'un PATCH partiel qui ne touche pas au fichier)
        fichier = donnees.get('fichier')
        offre = donnees.get('offre')

        # Nom à vérifier : priorité au nom_candidat saisi manuellement,
        # sinon on le déduit du nom de fichier (même logique que CV.save())
        nom_candidat_saisi = donnees.get('nom_candidat')
        if nom_candidat_saisi:
            nom_a_verifier = nom_candidat_saisi.strip()
        elif fichier:
            nom_fichier = os.path.splitext(os.path.basename(fichier.name))[0]
            nom_a_verifier = nom_fichier.replace("_", " ").replace("CV", "").strip()
        else:
            nom_a_verifier = None

        if offre and nom_a_verifier:
            deja_existant = CV.objects.filter(
                offre=offre,
                nom_candidat__iexact=nom_a_verifier
            ).exists()

            if deja_existant:
                raise serializers.ValidationError(
                    f"Un CV pour '{nom_a_verifier}' existe déjà pour cette offre."
                )

        return donnees


class OffreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offre
        # Cette liste doit correspondre EXACTEMENT aux champs définis dans
        # models.py -> class Offre. Ne pas ajouter missions/profil/avantages/
        # description_complete tant qu'ils n'existent pas sur le modèle,
        # sinon DRF lève "Field name `X` is not valid for model `Offre`".
        fields = ['id', 'titre', 'type_contrat', 'salaire', 'description',
                  'statut', 'date_creation', 'date_modification']
        read_only_fields = ['id', 'date_creation', 'date_modification']


class ScoreSerializer(serializers.ModelSerializer):
    nom_candidat = serializers.CharField(source='cv.nom_candidat', read_only=True)
    fichier_cv = serializers.FileField(source='cv.fichier', read_only=True)
    email = serializers.CharField(source='cv.email', read_only=True)
    telephone = serializers.CharField(source='cv.telephone', read_only=True)
    linkedin = serializers.CharField(source='cv.linkedin', read_only=True)
    github = serializers.CharField(source='cv.github', read_only=True)
    gitlab = serializers.CharField(source='cv.gitlab', read_only=True)
    portfolio = serializers.CharField(source='cv.portfolio', read_only=True)
    behance = serializers.CharField(source='cv.behance', read_only=True)
    adresse = serializers.CharField(source='cv.adresse', read_only=True)

    class Meta:
        model = Score
        fields = ['id', 'cv', 'nom_candidat', 'fichier_cv', 'email', 'telephone',
                  'linkedin', 'github', 'gitlab', 'portfolio', 'behance', 'adresse',
                  'offre', 'score_final', 'score_semantique', 'score_motscles',
                  'competences_communes', 'competences_manquantes', 'sous_scores',
                  'date_calcul']