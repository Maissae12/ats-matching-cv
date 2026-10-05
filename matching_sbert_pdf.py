from sentence_transformers import SentenceTransformer, util
from lecture_fichiers import charger_cvs_depuis_dossier, obtenir_texte_pertinent
from competences import score_mots_cles

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def matcher_cvs(offre, cvs: dict, poids_sbert=0.6, poids_motscles=0.4):
   
    textes_pertinents = {
        nom: obtenir_texte_pertinent(texte) for nom, texte in cvs.items()
    }

    textes = [offre] + list(textes_pertinents.values())
    embeddings = model.encode(textes)

    resultats = []
    for i, nom in enumerate(textes_pertinents.keys()):
        score_semantique = util.cos_sim(embeddings[0], embeddings[i + 1]).item()
        score_keywords = score_mots_cles(offre, textes_pertinents[nom])

        score_final = (poids_sbert * score_semantique) + (
            poids_motscles * score_keywords
        )

        resultats.append((nom, score_final, score_semantique, score_keywords))

    return sorted(resultats, key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    offre = (
        "Nous recherchons un développeur Backend avec expérience en Python, Django, "
        "API REST et bases de données SQL/PostgreSQL."
    )
    cvs = charger_cvs_depuis_dossier("cvs")

    resultats = matcher_cvs(offre, cvs)

    
    for nom, score_final, score_sem, score_kw in resultats:
        print(
            f"{nom} : score final avec extraction ={score_final:.3f}  "
        )
