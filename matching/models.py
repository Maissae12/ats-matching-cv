from django.db import models
import os


class Offre(models.Model):
    STATUTS = [
        ('ouverte', 'Ouverte'),
        ('fermee', 'Fermée'),
    ]

    TYPES_CONTRAT = [
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('Stage', 'Stage'),
        ('Freelance', 'Freelance'),
        ('Intérim', 'Intérim'),
    ]

    titre = models.CharField(max_length=200)
    type_contrat = models.CharField(max_length=20, choices=TYPES_CONTRAT, default='CDI')
    salaire = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    statut = models.CharField(max_length=10, choices=STATUTS, default='ouverte')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre


class CV(models.Model):
    offre = models.ForeignKey(Offre, on_delete=models.CASCADE, related_name='candidats')
    nom_candidat = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=200, blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    linkedin = models.CharField(max_length=300, blank=True)
    github = models.CharField(max_length=300, blank=True)
    gitlab = models.CharField(max_length=300, blank=True)
    portfolio = models.CharField(max_length=300, blank=True)
    behance = models.CharField(max_length=300, blank=True)
    adresse = models.CharField(max_length=200, blank=True)
    fichier = models.FileField(upload_to='cvs/')
    texte_extrait = models.TextField(blank=True)
    embedding = models.JSONField(null=True, blank=True)
    date_upload = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.nom_candidat and self.fichier:
            nom_fichier = os.path.splitext(os.path.basename(self.fichier.name))[0]
            self.nom_candidat = nom_fichier.replace("_", " ").replace("CV", "").strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom_candidat


class Score(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE)
    offre = models.ForeignKey(Offre, on_delete=models.CASCADE)
    score_final = models.FloatField()
    score_semantique = models.FloatField()
    score_motscles = models.FloatField()
    competences_communes = models.JSONField(default=list, blank=True)
    competences_manquantes = models.JSONField(default=list, blank=True)
    sous_scores = models.JSONField(default=dict, blank=True)
    date_calcul = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cv.nom_candidat} - {self.offre.titre} : {self.score_final:.2f}"