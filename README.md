# Systeme de matching CV / Offres d'emploi - ATS
## Projet de fin d'annee - NeoMorIT
### Maissae Abougarn - Eleve ingenieur Genie Informatique, ENSA Khouribga

## 1. Objectif

Comparer automatiquement des CV a des offres d'emploi et calculer un score de
pertinence, afin de classer les candidatures par ordre de pertinence pour un
recruteur, avec un systeme explicable (competences en commun/manquantes,
detail du score par section du CV).

## 2. Architecture generale

```
stage_nlp/
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── projet_nlp_cv/               # Configuration du projet Django
│   ├── settings.py
│   └── urls.py
│
├── matching/                    # Application principale
│   ├── models.py                 # Modeles CV, Offre, Score
│   ├── serializers.py            # Traduction objets <-> JSON (DRF)
│   ├── views.py                  # Vues HTML + ViewSets API
│   ├── urls.py                   # Routes de l'application
│   ├── services.py               # Logique de calcul du score (lien NLP <-> Django)
│   ├── static/matching/style.css # Feuille de style personnalisee
│   ├── templates/matching/       # Pages HTML (consomment l'API, ne calculent rien)
│   └── management/commands/
│       └── importer_cvs.py       # Commande d'import en masse (tests)
│
├── lecture_fichiers.py           # Lecture PDF/TXT, extraction sections, coordonnees
├── competences.py                 # Referentiel de competences + score mots-cles
└── cvs_source/                    # CV de test, source pour les imports
```

Le moteur NLP (`lecture_fichiers.py`, `competences.py`) est independant de
Django : il peut etre teste seul en ligne de commande, ou appele depuis
`matching/services.py` pour etre integre a l'application web.

Le projet est conteneurise avec Docker (application Django + base de
donnees PostgreSQL), pour un deploiement reproductible.

## 3. Fonctionnement du moteur NLP

### 3.1 Lecture et extraction (`lecture_fichiers.py`)
- `lire_fichier(chemin)` : lit un fichier `.pdf` ou `.txt`
- `extraire_sections(texte, synonymes_sections)` : decoupe le CV en sections
  (Competences, Projets Academiques, Formation) en acceptant plusieurs
  synonymes par titre
- `obtenir_texte_pertinent(texte_cv)` : combine les sections Competences et
  Projets pour le calcul du score principal ; si rien n'est detecte, retombe
  sur le texte complet (filet de securite)
- `nettoyer_artefacts_icones(texte)` : supprime les artefacts de texte
  generes par les icones (enveloppe, telephone...) presentes dans les PDF,
  qui peuvent polluer l'extraction des coordonnees
- Extraction automatique des coordonnees du candidat : email, telephone,
  adresse, LinkedIn, GitHub, GitLab, portfolio personnel, Behance

Seules les sections Competences et Projets sont comparees a l'offre pour le
score principal : un test comparatif a montre qu'utiliser le CV complet
dilue le score de similarite semantique (voir section 6).

### 3.2 Score mots-cles (`competences.py`)
- `REFERENTIEL_COMPETENCES` : dictionnaire de competences techniques, chacune
  associee a une liste de synonymes (ex : `"machine learning": ["machine
  learning", "ml", "apprentissage automatique"]`)
- `extraire_competences(texte)` : detecte les competences presentes dans un
  texte
- `score_mots_cles(offre, cv)` : pourcentage de competences demandees par
  l'offre que possede le candidat

### 3.3 Score semantique SBERT
- Modele : `paraphrase-multilingual-MiniLM-L12-v2` (multilingue)
- Chaque texte est transforme en vecteur numerique (embedding)
- La similarite cosinus entre vecteurs donne un score entre 0 et 1
- Les embeddings des CV sont mis en cache (champ `embedding` du modele
  `CV`) pour eviter de recalculer inutilement la vectorisation a chaque
  requete

### 3.4 Score final
```python
score_final = (0.6 * score_semantique) + (0.4 * score_mots_cles)
```
Le score mots-cles corrige un biais du score semantique seul, qui peut
favoriser un profil au vocabulaire proche de l'offre meme sans les
competences exactes demandees (voir section 6 pour un exemple concret).

### 3.5 Explicabilite du score
En plus du score final, le systeme calcule et affiche :
- Les **competences en commun** entre l'offre et le CV
- Les **competences manquantes** au candidat
- Un **detail par section** (Competences, Projets, Formation) : un
  sous-score semantique independant pour chaque section, a titre
  informatif uniquement (le classement reste base sur le score final
  global, pas sur ces sous-scores)

## 4. Integration Django

### 4.1 Modeles
- **Offre** : titre, description, statut (ouverte / fermee / pourvue),
  date de creation, date de derniere modification
- **CV** : nom du candidat (extrait automatiquement du nom de fichier),
  coordonnees extraites (email, telephone, adresse, LinkedIn, GitHub,
  GitLab, portfolio, Behance), fichier PDF/TXT, offre associee, embedding
  mis en cache
- **Score** : score final, score semantique, score mots-cles, competences
  communes/manquantes (JSON), sous-scores par section (JSON), lien vers le
  CV et l'offre concernes

### 4.2 API REST (Django REST Framework)
- `GET/POST /api/cvs/` : liste et creation de CV (avec validation du
  format de fichier, de la taille, et detection des doublons de
  candidature)
- `GET/POST /api/offres/` : liste et creation d'offres
- `GET /api/offres/{id}/classement/` : calcule (ou reutilise) le score de
  chaque CV lie a cette offre, et renvoie le classement trie ; isole les
  CV illisibles dans une liste d'erreurs separee sans bloquer le reste du
  classement
- `GET/PATCH/DELETE /api/offres/{id}/`, `/api/cvs/{id}/` : consultation,
  modification et suppression

Le classement n'est recalcule que si necessaire : un nouveau CV, ou une
offre modifiee apres le dernier calcul. Sinon, le score deja enregistre en
base est reutilise, ce qui rend la consultation quasi instantanee.

### 4.3 Robustesse
- Rejet a l'upload des fichiers dont le format n'est pas PDF/TXT, ou
  depassant 5 Mo
- Detection des CV dont le texte extrait est trop court ou inexploitable
  (image scannee, document non pertinent) : le CV est exclu du classement
  avec un message explicite, sans bloquer le calcul des autres candidats
- Detection des doublons de candidature (meme candidat, meme offre)

### 4.4 Pages web (frontend)
Chaque page HTML consomme l'API en JavaScript (`fetch`) : elle ne calcule
jamais rien elle-meme, elle affiche uniquement les donnees renvoyees par
l'API.

| Page | Role |
|---|---|
| `/` | Accueil, acces aux sections principales |
| `/offres/` | Liste des offres (recherche, statut, creation, modification, suppression) |
| `/ajouter-offre/` | Formulaire de creation d'une offre |
| `/modifier-offre/<id>/` | Formulaire d'edition d'une offre existante |
| `/upload-cv/` | Depot de plusieurs CV a la fois, lies a une offre choisie |
| `/cvs/` | Liste des candidats, filtrable par offre, avec suppression et fiche detaillee |
| `/page-classement/<id>/` | Classement trie et triable, avec jauges de score, fiche competences, fiche coordonnees, detail par section |



## 6. Choix techniques et justifications

- **SBERT plutot que TF-IDF seul** : le cahier des charges recommandait de
  commencer par TF-IDF pour un prototype rapide ; SBERT a ete integre
  directement car l'objectif final du projet est la similarite semantique
  complete.

- **Extraction des sections Competences/Projets uniquement** : comparer le
  CV complet a l'offre dilue le score semantique (verifie experimentalement).
- **Django REST Framework plutot que FastAPI** : reutilisation d'une base
  Django deja maitrisee, et besoin natif d'une interface d'administration
  et d'un ORM pour gerer CV/Offres/Scores.
- **CV lie a une offre des l'upload** : chaque CV est associe a l'offre
  pour laquelle il a ete depose, pour ne classer que les candidats ayant
  reellement postule a une offre donnee.
- **PostgreSQL plutot que SQLite** : passage a une base de donnees adaptee
  a un usage multi-utilisateurs et a la production, avec conteneurisation
  Docker pour la reproductibilite du deploiement.
- **Explicabilite (competences communes/manquantes, sous-scores par
  section)** : un score seul (ex : 0.65) n'est pas exploitable par un
  recruteur sans contexte ; le detail par section et la liste des
  competences justifient concretement le classement.

## 7. Infrastructure et deploiement

Le projet est conteneurise avec Docker :
- **Service `web`** : application Django (build depuis le `Dockerfile`)
- **Service `db`** : PostgreSQL 16, avec volume persistant

```bash
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## 8. Limites connues et pistes d'amelioration

| Limite | Statut | Piste d'amelioration |
|---|---|---|
| Dependance aux titres de section du CV | Partiellement resolu | Detection par mots-cles dans tout le texte, en complement |
| Poids 60/40 fixes arbitrairement | Non resolu | Tester plusieurs ponderations sur un jeu de CV annotes |
| Pas de detection du niveau de maitrise (annees d'experience) | Prototype teste, non integre | Ponderer le score par la duree d'experience detectee |
| Nom du candidat extrait du nom de fichier, pas du contenu du CV | Connue | Extraction depuis le texte du CV, ou saisie manuelle |
| Pas d'authentification | A traiter | Systeme de connexion recruteur/candidat |
| Adresse parfois mal decoupee si le CV n'utilise pas de separateur standard | Connue | Regles de decoupage plus robustes |

## 9. Prochaines etapes

- Finaliser le rapport de projet avec cette architecture complete
- Decider de l'integration de la ponderation par l'experience
- Tests automatises sur les fonctions cles du moteur NLP
- Preparation de la soutenance (demonstration, support de presentation)