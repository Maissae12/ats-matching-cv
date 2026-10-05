from sentence_transformers import SentenceTransformer, util
from lecture_fichiers import charger_cvs_depuis_dossier
from competences import score_mots_cles

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def matcher_cvs_sans_extraction(offre, cvs: dict, poids_sbert=0.6, poids_motscles=0.4):

    textes = [offre] + list(cvs.values())
    embeddings = model.encode(textes)

    resultats = []
    for i, nom in enumerate(cvs.keys()):
        score_semantique = util.cos_sim(embeddings[0], embeddings[i + 1]).item()
        score_keywords = score_mots_cles(offre, cvs[nom])

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

    resultats = matcher_cvs_sans_extraction(offre, cvs)

    for nom, score_final, score_sem, score_kw in resultats:
        print(
            f"{nom} : score final sans extraction ={score_final:.3f}  "
        )