import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sentence_transformers import SentenceTransformer, util
from lecture_fichiers import (
    obtenir_texte_pertinent, extraire_sections, SYNONYMES_SECTIONS,
    extraire_email, extraire_telephone, extraire_linkedin, extraire_github,
    extraire_gitlab, extraire_portfolio, extraire_behance, extraire_adresse
)
from competences import score_mots_cles, extraire_competences
from .models import Score

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


def lire_texte_cv(cv):
    extension = os.path.splitext(cv.fichier.name)[1].lower()
    if extension == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(cv.fichier.path)
        texte = ""
        for page in reader.pages:
            texte += page.extract_text() or ""
        return texte
    elif extension == ".txt":
        with open(cv.fichier.path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Format non supporté : {extension}")


def calculer_sous_scores(offre_description, texte_cv):
   
    sections = extraire_sections(texte_cv, SYNONYMES_SECTIONS)
    sous_scores = {}
    for nom_section, contenu in sections.items():
        contenu_nettoye = contenu.strip()
        if len(contenu_nettoye) < 20:
            sous_scores[nom_section] = None
            continue
        embeddings = model.encode([offre_description, contenu_nettoye])
        score = util.cos_sim(embeddings[0], embeddings[1]).item()
        sous_scores[nom_section] = max(0.0, round(score, 3))
    return sous_scores


def calculer_score(cv, offre):
    texte_cv = lire_texte_cv(cv)
    texte_nettoye = texte_cv.strip()
    if len(texte_nettoye) < 50:
        raise ValueError(
            "Le texte extrait de ce CV est trop court ou inexploitable "
            "(probablement une image scannée, un document non pertinent, ou un fichier vide)."
        )
    if not cv.email and not cv.telephone:
        cv.email = extraire_email(texte_cv) or ""
        cv.telephone = extraire_telephone(texte_cv) or ""
        cv.linkedin = extraire_linkedin(texte_cv) or ""
        cv.github = extraire_github(texte_cv) or ""
        cv.gitlab = extraire_gitlab(texte_cv) or ""
        cv.portfolio = extraire_portfolio(texte_cv) or ""
        cv.behance = extraire_behance(texte_cv) or ""
        cv.adresse = extraire_adresse(texte_cv) or ""
        cv.save()

    texte_pertinent = obtenir_texte_pertinent(texte_cv)

    if cv.embedding:
        embedding_cv = cv.embedding
    else:
        embedding_cv = model.encode(texte_pertinent).tolist()
        cv.embedding = embedding_cv
        cv.save()

    texte_offre = offre.description

    embedding_offre = model.encode(texte_offre).tolist()
    score_semantique = util.cos_sim(embedding_offre, embedding_cv).item()
    score_keywords = score_mots_cles(texte_offre, texte_pertinent)

    competences_offre = extraire_competences(texte_offre)
    competences_cv = extraire_competences(texte_pertinent)
    competences_communes = sorted(competences_offre & competences_cv)
    competences_manquantes = sorted(competences_offre - competences_cv)
    sous_scores = calculer_sous_scores(texte_offre, texte_cv)

    # Score final = la similarité cosinus (SBERT)
    score_final = max(0.0, score_semantique)

    return {
        "score_final": score_final,
        "score_semantique": score_semantique,
        "score_motscles": score_keywords,
        "competences_communes": competences_communes,
        "competences_manquantes": competences_manquantes,
        "sous_scores": sous_scores,
    }

def calculer_et_sauvegarder_score(cv, offre):
    resultat = calculer_score(cv, offre)
    score_obj, cree = Score.objects.update_or_create(
        cv=cv,
        offre=offre,
        defaults={
            "score_final": resultat["score_final"],
            "score_semantique": resultat["score_semantique"],
            "score_motscles": resultat["score_motscles"],
            "competences_communes": resultat["competences_communes"],
            "competences_manquantes": resultat["competences_manquantes"],
            "sous_scores": resultat["sous_scores"],
        }
    )
    return score_obj