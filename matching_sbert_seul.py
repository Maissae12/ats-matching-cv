from sentence_transformers import SentenceTransformer, util
from lecture_fichiers import charger_cvs_depuis_dossier, obtenir_texte_pertinent

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def matcher_cvs_sbert_seul(offre, cvs: dict):
    
    textes_pertinents = {
        nom: obtenir_texte_pertinent(texte) for nom, texte in cvs.items()
    }

    textes = [offre] + list(textes_pertinents.values())
    embeddings = model.encode(textes)

    resultats = []
    for i, nom in enumerate(textes_pertinents.keys()):
        score = util.cos_sim(embeddings[0], embeddings[i + 1]).item()
        resultats.append((nom, score))

    return sorted(resultats, key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    offre = (
    "Nous recherchons un développeur Backend avec expérience en Python, Django, "
    "API REST et bases de données SQL/PostgreSQL."
)
    cvs = charger_cvs_depuis_dossier("cvs")

    resultats = matcher_cvs_sbert_seul(offre, cvs)

    print("SBERT seul")
    for nom, score in resultats:
        print(f"{nom} : score={score:.3f}")