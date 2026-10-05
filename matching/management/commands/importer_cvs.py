import os
from django.core.management.base import BaseCommand
from django.core.files import File
from matching.models import CV, Offre


class Command(BaseCommand):
    help = "Importe les CV (PDF) d'un dossier, liés à une offre précise, sans doublons."

    def add_arguments(self, parser):
        parser.add_argument('dossier', type=str, help="Chemin du dossier contenant les CV")
        parser.add_argument('offre_id', type=int, help="ID de l'offre à laquelle lier ces CV")

    def handle(self, *args, **options):
        dossier = options['dossier']
        offre_id = options['offre_id']

        try:
            offre = Offre.objects.get(id=offre_id)
        except Offre.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Offre introuvable avec l'ID {offre_id}"))
            return

        if not os.path.isdir(dossier):
            self.stdout.write(self.style.ERROR(f"Dossier introuvable : {dossier}"))
            return

        # Noms déjà importés pour CETTE offre (pour éviter les doublons)
        noms_deja_importes = set(
            os.path.basename(cv.fichier.name).split('_')[0] if False else
            os.path.splitext(os.path.basename(cv.fichier.name))[0]
            for cv in CV.objects.filter(offre=offre)
        )

        fichiers = [f for f in os.listdir(dossier) if f.lower().endswith(('.pdf', '.txt'))]

        for nom_fichier in fichiers:
            nom_sans_extension = os.path.splitext(nom_fichier)[0]

            if nom_sans_extension in noms_deja_importes:
                self.stdout.write(self.style.WARNING(f"Ignoré (déjà importé) : {nom_fichier}"))
                continue

            chemin_complet = os.path.join(dossier, nom_fichier)

            with open(chemin_complet, 'rb') as f:
                cv = CV(offre=offre)
                cv.fichier.save(nom_fichier, File(f), save=True)

            self.stdout.write(self.style.SUCCESS(f"Ajouté : {cv.nom_candidat} → {offre.titre}"))