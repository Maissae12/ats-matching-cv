import re
from unidecode import unidecode

REFERENTIEL_COMPETENCES = {
    # ---------- LANGAGES DE PROGRAMMATION ----------
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "php": ["php"],
    "c": ["langage c", " c "],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp"],
    "ruby": ["ruby"],
    "go": ["golang", "go lang"],
    "rust": ["rust"],
    "kotlin": ["kotlin"],
    "swift": ["swift"],
    "r": ["langage r", "r studio", "rstudio"],
    "scala": ["scala"],
    "perl": ["perl"],
    "matlab": ["matlab"],
    "vba": ["vba", "visual basic for applications"],
    "dart": ["dart"],
    "sql": ["sql", "bases de donnees relationnelles", "base de donnees sql"],

    # ---------- WEB FRONTEND ----------
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "sass": ["sass", "scss"],
    "tailwind": ["tailwind", "tailwindcss"],
    "bootstrap": ["bootstrap"],
    "react": ["react", "react.js", "reactjs"],
    "angular": ["angular"],
    "vue.js": ["vue.js", "vuejs", "vue"],
    "next.js": ["next.js", "nextjs"],
    "svelte": ["svelte"],
    "jquery": ["jquery"],
    "webpack": ["webpack"],

    # ---------- WEB BACKEND / FRAMEWORKS ----------
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "node.js": ["node.js", "nodejs", "node"],
    "express.js": ["express.js", "expressjs", "express"],
    "laravel": ["laravel"],
    "symfony": ["symfony"],
    "spring boot": ["spring boot", "spring"],
    "asp.net": ["asp.net", "aspnet", ".net", "dotnet"],
    "ruby on rails": ["ruby on rails", "rails"],
    "graphql": ["graphql"],
    "rest api": ["rest api", "api rest", "restful"],
    "soap": ["soap"],
    "microservices": ["microservices", "architecture microservices"],

    # ---------- DESKTOP / AUTRES ----------
    "javafx": ["javafx"],
    "tkinter": ["tkinter"],
    "qt": ["qt", "pyqt"],
    "electron": ["electron"],

    # ---------- BASES DE DONNEES ----------
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "sqlite": ["sqlite"],
    "oracle db": ["oracle database", "oracle sql", "oracle db"],
    "sql server": ["sql server", "microsoft sql server", "mssql"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "nosql": ["nosql"],
    "elasticsearch": ["elasticsearch", "elastic search"],
    "cassandra": ["cassandra"],
    "firebase": ["firebase"],

    # ---------- DATA / IA / ML ----------
    "machine learning": ["machine learning", "ml", "apprentissage automatique"],
    "deep learning": ["deep learning", "apprentissage profond"],
    "intelligence artificielle": ["intelligence artificielle", "ia", "artificial intelligence", "ai"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "keras": ["keras"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib"],
    "seaborn": ["seaborn"],
    "nlp": [
        "nlp",
        "natural language processing",
        "traitement du langage naturel",
        "traitement automatique du langage",
    ],
    "spacy": ["spacy"],
    "nltk": ["nltk"],
    "hugging face": ["hugging face", "huggingface", "transformers"],
    "llm": ["llm", "large language model", "grands modeles de langage", "genai", "ia generative", "generative ai"],
    "computer vision": ["computer vision", "vision par ordinateur", "opencv"],
    "data science": ["data science", "science des donnees"],
    "data analysis": ["data analysis", "analyse de donnees"],
    "data engineering": ["data engineering", "ingenierie des donnees"],
    "big data": ["big data"],
    "spark": ["spark", "apache spark", "pyspark"],
    "hadoop": ["hadoop"],
    "etl": ["etl", "extract transform load"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau software", "tableau"],
    "looker": ["looker"],
    "airflow": ["airflow", "apache airflow"],
    "statistiques": ["statistiques", "statistics"],

    # ---------- CLOUD / DEVOPS / INFRA ----------
    "git": ["git"],
    "github": ["github"],
    "gitlab": ["gitlab"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "linux": ["linux"],
    "unix": ["unix"],
    "windows server": ["windows server"],
    "bash": ["bash", "shell scripting", "shell script"],
    "ci/cd": ["ci/cd", "cicd", "integration continue", "deploiement continu"],
    "jenkins": ["jenkins"],
    "terraform": ["terraform"],
    "ansible": ["ansible"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "devops": ["devops"],
    "reseaux": ["reseaux informatiques", "administration reseau", "networking"],
    "cybersecurite": ["cybersecurite", "securite informatique", "cybersecurity"],
    "virtualisation": ["virtualisation", "vmware", "hyper-v"],

    # ---------- MOBILE ----------
    "android": ["android"],
    "ios": ["ios"],
    "flutter": ["flutter"],
    "react native": ["react native"],
    "xamarin": ["xamarin"],

    # ---------- OUTILS BUREAUTIQUE ----------
    "excel": ["excel", "microsoft excel"],
    "word": ["word", "microsoft word"],
    "powerpoint": ["powerpoint", "microsoft powerpoint"],
    "google sheets": ["google sheets"],
    "notion": ["notion"],

    # ---------- METHODES DE GESTION DE PROJET ----------
    "scrum": ["scrum"],
    "agile": ["agile", "methodes agiles"],
    "kanban": ["kanban"],
    "gestion de projet": ["gestion de projet", "project management"],
    "pmp": ["pmp", "project management professional"],
    "prince2": ["prince2"],
    "jira": ["jira"],
    "trello": ["trello"],
    "confluence": ["confluence"],

    # ---------- MARKETING / COMMUNICATION / DIGITAL ----------
    "marketing digital": ["marketing digital", "digital marketing"],
    "seo": ["seo", "referencement naturel"],
    "sea": ["sea", "referencement payant", "google ads"],
    "reseaux sociaux": ["reseaux sociaux", "social media"],
    "community management": ["community management", "community manager"],
    "content marketing": ["content marketing", "marketing de contenu"],
    "copywriting": ["copywriting", "redaction web"],
    "email marketing": ["email marketing", "emailing"],
    "google analytics": ["google analytics"],
    "branding": ["branding", "image de marque"],
    "communication": ["communication"],
    "relations publiques": ["relations publiques", "rp"],

    # ---------- VENTE / COMMERCE ----------
    "vente": ["vente", "techniques de vente"],
    "negociation": ["negociation"],
    "prospection": ["prospection commerciale", "prospection"],
    "crm": ["crm", "customer relationship management", "salesforce", "hubspot"],
    "e-commerce": ["e-commerce", "ecommerce"],
    "relation client": ["relation client", "service client", "customer service"],

    # ---------- FINANCE / COMPTABILITE ----------
    "comptabilite": ["comptabilite", "comptable"],
    "controle de gestion": ["controle de gestion"],
    "audit": ["audit financier", "audit"],
    "fiscalite": ["fiscalite"],
    "analyse financiere": ["analyse financiere"],
    "sage": ["sage", "sage comptabilite"],
    "sap": ["sap"],
    "gestion budgetaire": ["gestion budgetaire", "budgeting"],

    # ---------- RH ----------
    "recrutement": ["recrutement"],
    "gestion rh": ["gestion des ressources humaines", "gestion rh", "ressources humaines"],
    "paie": ["paie", "gestion de la paie"],
    "formation professionnelle": ["formation professionnelle"],
    "droit du travail": ["droit du travail", "droit social"],

    # ---------- INGENIERIE / BTP / INDUSTRIE ----------
    "autocad": ["autocad"],
    "solidworks": ["solidworks"],
    "revit": ["revit", "bim"],
    "genie civil": ["genie civil"],
    "genie electrique": ["genie electrique", "electrotechnique"],
    "genie mecanique": ["genie mecanique"],
    "plc": ["plc", "automate programmable", "automatisme"],
    "lean manufacturing": ["lean manufacturing", "lean management"],
    "six sigma": ["six sigma"],
    "gestion de production": ["gestion de production", "production management"],
    "qualite": ["controle qualite", "assurance qualite", "qualite"],
    "logistique": ["logistique", "supply chain"],

    # ---------- SANTE ----------
    "soins infirmiers": ["soins infirmiers"],
    "premiers secours": ["premiers secours", "secourisme"],
    "dossier medical": ["dossier medical", "dossier patient"],

    # ---------- JURIDIQUE ----------
    "droit des affaires": ["droit des affaires"],
    "droit civil": ["droit civil"],
    "redaction juridique": ["redaction juridique", "redaction de contrats"],

    # ---------- LANGUES ----------
    "anglais": ["anglais", "english"],
    "francais": ["francais", "french"],
    "espagnol": ["espagnol", "spanish"],
    "arabe": ["arabe", "arabic"],
    "allemand": ["allemand", "german"],

    # ---------- SOFT SKILLS ----------
    "travail equipe": ["travail d'equipe", "esprit d'equipe", "teamwork"],
    "leadership": ["leadership"],
    "communication ecrite": ["communication ecrite et orale"],
    "resolution de problemes": ["resolution de problemes", "problem solving"],
    "autonomie": ["autonomie"],
    "esprit critique": ["esprit critique", "pensee critique"],
    "gestion du temps": ["gestion du temps", "time management"],
    "adaptabilite": ["adaptabilite", "flexibilite"],
}


def normaliser(texte):
    """Nettoie un texte pour la comparaison (minuscules, accents enlevés)."""
    return unidecode(texte).lower()


def extraire_competences(texte, referentiel=REFERENTIEL_COMPETENCES):
    texte_norm = normaliser(texte)
    trouvees = set()

    for nom_principal, variantes in referentiel.items():
        for variante in variantes:
            variante_norm = normaliser(variante)
            pattern = r"\b" + re.escape(variante_norm.strip()) + r"\b"
            if re.search(pattern, texte_norm):
                trouvees.add(nom_principal)
                break

    return trouvees


def score_mots_cles(texte_offre, texte_cv, referentiel=REFERENTIEL_COMPETENCES):
    """
    Calcule le pourcentage de compétences demandées dans l'offre
    que possède le candidat, indépendamment de son propre nombre total de compétences.
    Retourne un score entre 0 et 1.
    """
    competences_offre = extraire_competences(texte_offre, referentiel)
    competences_cv = extraire_competences(texte_cv, referentiel)

    if not competences_offre:
        return 0.0

    communes = competences_offre & competences_cv
    return len(communes) / len(competences_offre)