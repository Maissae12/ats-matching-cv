from pypdf import PdfReader
import os
import re
from unidecode import unidecode
def lire_fichier(chemin):
    extension = os.path.splitext(chemin)[1].lower()

    if extension == ".pdf":
        reader = PdfReader(chemin)
        texte = ""
        for page in reader.pages:
            texte += page.extract_text()
        return texte

    elif extension == ".txt":
        with open(chemin, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise ValueError(f"Format non supporté : {extension}")


def charger_cvs_depuis_dossier(dossier):
    cvs = {}
    for nom_fichier in os.listdir(dossier):
        chemin_complet = os.path.join(dossier, nom_fichier)
        cvs[nom_fichier] = lire_fichier(chemin_complet)
    return cvs



def normaliser(texte):

    texte = unidecode(texte).lower()
    texte = re.sub(r"[^a-z0-9]", "", texte)
    return texte

def nettoyer_artefacts_icones(texte):
    
    motifs_icones = [
        r'envel.{0,2}pe',       
        r't[eé]l[eé]phone',    
        r'mobile',
        r'linked.{0,2}in',      
        r'github',
        r'map.{0,2}marker',
        r'globe',
    ]

    for motif in motifs_icones:
        texte = re.sub(motif, ' ', texte, flags=re.IGNORECASE)

    return texte


def extraire_email(texte):
    """Détecte une adresse email dans le texte du CV, en ignorant les artefacts d'icônes."""
    texte_nettoye = nettoyer_artefacts_icones(texte)
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    resultat = re.search(pattern, texte_nettoye)
    return resultat.group(0) if resultat else None

def extraire_telephone(texte):
    """Détecte un numéro de téléphone marocain (formats courants)."""
    texte_nettoye = nettoyer_artefacts_icones(texte)
    pattern = r'(?:\+212|0)[\s.-]?[5-7](?:[\s.-]?\d{2}){4}'
    resultat = re.search(pattern, texte_nettoye)
    return resultat.group(0) if resultat else None



def extraire_adresse(texte):
    villes_courantes = [
        'casablanca', 'rabat', 'marrakech', 'fes', 'fès', 'tanger', 'agadir',
        'meknes', 'meknès', 'oujda', 'kenitra', 'kénitra', 'tetouan', 'tétouan',
        'khouribga', 'safi', 'el jadida', 'béni mellal', 'beni mellal'
    ]
    lignes = texte.split('\n')
    for ligne in lignes[:15]:
        ligne_basse = ligne.lower()
        if 'maroc' in ligne_basse or any(ville in ligne_basse for ville in villes_courantes):
            resultat = re.split(r'[•|·]|\s{2,}', ligne)[0]
            return resultat.strip()
    return None


def extraire_linkedin(texte):
    """Détecte une URL ou un identifiant LinkedIn."""
    pattern = r'linkedin\.com/in/[a-zA-Z0-9_-]+'
    resultat = re.search(pattern, texte, re.IGNORECASE)
    if resultat:
        url = resultat.group(0)
        return url if url.startswith('http') else f"https://{url}"
    return None


def extraire_github(texte):
    """Détecte une URL ou un identifiant GitHub."""
    pattern = r'github\.com/[a-zA-Z0-9_-]+'
    resultat = re.search(pattern, texte, re.IGNORECASE)
    if resultat:
        url = resultat.group(0)
        return url if url.startswith('http') else f"https://{url}"
    return None


def extraire_gitlab(texte):
    """Détecte une URL ou un identifiant GitLab."""
    pattern = r'gitlab\.com/[a-zA-Z0-9_-]+'
    resultat = re.search(pattern, texte, re.IGNORECASE)
    if resultat:
        url = resultat.group(0)
        return url if url.startswith('http') else f"https://{url}"
    return None


def extraire_behance(texte):
    """Détecte une URL Behance (profils design)."""
    pattern = r'behance\.net/[a-zA-Z0-9_-]+'
    resultat = re.search(pattern, texte, re.IGNORECASE)
    if resultat:
        url = resultat.group(0)
        return url if url.startswith('http') else f"https://{url}"
    return None
    """Retourne un dictionnaire {nom_fichier: contenu_texte} pour tous les CV du dossier."""
    """Enlève accents, espaces, ponctuation, met en minuscules."""
def extraire_portfolio(texte):
    """Détecte un site personnel/portfolio (hors LinkedIn/GitHub)."""
    pattern = r'\b(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.(?:com|dev|io|me|fr))\b'
    for match in re.finditer(pattern, texte, re.IGNORECASE):
        domaine = match.group(0).lower()
        if not any(site in domaine for site in ['linkedin', 'github', 'gitlab', 'behance', 'gmail', 'yahoo', 'hotmail', 'outlook']):
            return match.group(0)
    return None
 
 
 
 
 
 
 
 
 
 
SYNONYMES_SECTIONS = {
    "Compétences": [
        "competences", "competence", "skills", "hard skills",
        "competences techniques", "technical skills",
    ],
    "Projets Académiques": [
        "projets academiques", "projets", "projects",
        "experience professionnelle", "experiences",
        "realisations", "portfolio",
    ],
    "Formation": [
        "formation", "education", "diplomes", "diplome",
        "parcours academique", "cursus",
    ],
}

def extraire_sections(texte, synonymes_sections):
    lignes = texte.split("\n")
    sections = {nom: "" for nom in synonymes_sections}
    section_actuelle = None

    for ligne in lignes:
        ligne_normalisee = normaliser(ligne)

        nouveau_titre = None
        for nom_section, variantes in synonymes_sections.items():
            for variante in variantes:
                if ligne_normalisee.startswith(variante):
                    nouveau_titre = nom_section
                    break
            if nouveau_titre:
                break

        if nouveau_titre is not None:
            section_actuelle = nouveau_titre
        elif section_actuelle is not None:
            sections[section_actuelle] += ligne + "\n"
        elif ligne_normalisee and len(ligne_normalisee) < 30:
            section_actuelle = None

    return sections


def obtenir_texte_pertinent(texte_cv):
    """Extrait et combine les sections Compétences + Projets d'un CV."""
    sections = extraire_sections(texte_cv, SYNONYMES_SECTIONS)
    texte_pertinent = sections["Compétences"] + "\n" + sections["Projets Académiques"]

    if not texte_pertinent.strip():
        return texte_cv
    return texte_pertinent



