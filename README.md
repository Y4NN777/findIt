#  FindIt

### 📌 Description

**FindIt** est une application web développée avec **Flask** qui permet aux utilisateurs de déclarer et consulter des objets perdus ou retrouvés. Elle fournit une interface moderne et intuitive pour :

![image](https://github.com/user-attachments/assets/2fdae0c5-e7b1-44a2-811a-7643c18b75a8)
               

* S'enregistrer et se connecter de manière sécurisée
* Publier des annonces d'objets perdus ou retrouvés avec détails complets
* Rechercher et filtrer des objets par catégorie et localisation
* Gérer ses annonces via un tableau de bord personnel  
* Contacter d'autres utilisateurs pour récupérer des objets
* Marquer des objets comme résolus une fois retrouvés

---

### 📂 Structure du projet

```
FindIt/
├── .venv/                  # Environnement virtuel Python
├── instance/
│   └── database.db           # Base de données SQLite locale
├── static/                   # Fichiers statiques
│   ├── style.css             # CSS moderne avec système de design
│   └── favicon.png           # Icon de l'application
├── templates/                # Templates HTML (Jinja2)
│   ├── base.html             # Template de base avec navigation
│   ├── home.html             # Page d'accueil avec objets récents
│   ├── dashboard.html        # Tableau de bord utilisateur
│   ├── lost.html  
│   ├── match.html            # Corresponces entre objets
│   ├── resolved_matches.html # Correspondances resolus
│   ├── found.html            # Formulaire objets retrouvés
│   ├── search.html           # Page de recherche avancée
│   ├── login.html            # Connexion utilisateur
│   └── register.html         # Inscription utilisateur
├── .env                    # Variables d'environnement (non versionné)
├── .env.example            # Exemple de fichier `.env`
├── .gitignore              # Fichiers à ignorer par Git
├── app.py                  # Script principal de l'application Flask
├── models.py               # Modèles de base de données SQLAlchemy
├── routes.py               # Routes de l'application et logique metier
├── get_secret_key.py       # Générateur de clé secrète
├── README.md               # Documentation du projet
└── requirements.txt        # Liste des dépendances Python
```

---

### ⚙️ Installation et configuration

#### 1. Cloner le dépôt

```bash
git clone https://github.com/Y4NN777/findIt.git
cd findIt
```

#### 2. Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
.venv\Scripts\activate        # Windows
```

#### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

#### 4. Configurer la clé secrète

1. Crée un fichier `.env` à la racine :

   ```env
   SECRET_KEY=ta_clé_secrète_ici
   ```
2. Tu peux générer une clé sécurisée avec :

   ```bash
   python get_secret_key.py
   ```

#### 5. Initialiser la base de données ( Optionel, seras cree lors du premier lancement de l'application)

```bash
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

---

### 🚀 Lancer l'application

```bash
flask run
```
ou
```bash
python app.py
```

Accède à [http://127.0.0.1:5000](http://127.0.0.1:5000) dans ton navigateur.

---

### 🌟 Fonctionnalités principales

#### 🔐 Authentification
- Inscription et connexion sécurisées
- Gestion de sessions utilisateur
- Protection des routes privées

#### 📋 Gestion des objets
- **Déclaration d'objets perdus** avec informations détaillées
- **Déclaration d'objets retrouvés** pour aider la communauté
- **Catégorisation** (Électronique, Bijoux, Vêtements, etc.)
- **Localisation précise** et date de perte/découverte
- **Méthodes de contact** multiples (email, téléphone)
- **Système de récompenses** pour motiver les retours

#### 🎯 Interface utilisateur
- **Design moderne** avec système de couleurs professionnel
- **Tableau de bord personnel** avec statistiques
- **Page d'accueil** affichant les objets récents
- **Recherche avancée** par mots-clés, catégorie et localisation
- **Interface responsive** pour mobile et desktop
- **Messages flash** pour les notifications

#### 📊 Tableau de bord
- Vue d'ensemble des objets déclarés
- Statistiques personnelles (actifs, résolus, total)
- Actions rapides (éditer, marquer comme résolu)
- Gestion du statut des annonces

---

### 🎨 Design et UX

L'application utilise un **système de design moderne** avec :

- **Palette de couleurs professionnelle** (bleu principal, couleurs de statut)
- **Typography cohérente** avec échelle de tailles
- **Espacement systématique** pour une lecture agréable
- **Animations subtiles** pour l'interactivité
- **Icônes FontAwesome** pour une navigation intuitive
- **Design responsive** adapté à tous les écrans

---

### 🗄️ Base de données

#### Modèles principaux :

**User**
- Informations d'authentification
- Relation avec les objets déclarés

**LostItem** 
- Titre, description, catégorie
- Localisation et date de perte
- Informations de contact et récompense
- Statut (actif, résolu, expiré)

**FoundItem**
- Titre, description, catégorie  
- Localisation et date de découverte
- Informations de contact
- Statut (actif, résolu)

---

### 📘 Technologies et bibliothèques utilisées

#### Backend
- **[Flask](https://flask.palletsprojects.com/)** - Framework web Python
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM pour la base de données
- **[Flask-Login](https://flask-login.readthedocs.io/)** - Gestion des sessions
- **[Werkzeug](https://werkzeug.palletsprojects.com/)** - Hachage des mots de passe

#### Base de données
- **[SQLite](https://sqlite.org/)** - Base de données embarquée

#### Frontend
- **[Jinja2](https://jinja.palletsprojects.com/)** - Moteur de templates
- **CSS moderne** avec variables et grille responsive
- **[FontAwesome](https://fontawesome.com/)** - Icônes vectorielles

#### Environnement
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** - Variables d'environnement

---

### 🛠️ Debug et développement

#### Scripts de débogage bientot disponibles :
```bash
# Vérifier le contenu de la base de données
python debug_database_script.py

# Tester les requêtes Flask
python debug_routes_script.py
```

#### Logs utiles :
L'application affiche des informations de débogage dans la console pour :
- Requêtes de base de données
- Sessions utilisateur  
- Erreurs de templates
- Statistiques du tableau de bord

---

### 🚀 Déploiement

#### Variables d'environnement requises :
```env
SECRET_KEY=votre_clé_secrète_très_longue_et_sécurisée
FLASK_ENV=production
```

#### Plateformes de déploiement envisagees :
- **Railway** - Déploiement simple avec base SQLite
- **Render** - Support gratuit avec base PostgreSQL
- **Heroku** - Plateforme mature avec add-ons

---

### ✅ Roadmap et améliorations futures

#### 🎯 Priorité haute
- [ ] **Upload d'images** pour les objets
- [ ] **Système de messagerie** entre utilisateurs
- [ ] **Notifications par email** pour les correspondances
- [ ] **Géolocalisation** sur carte interactive

#### 🔧 Améliorations techniques
- [ ] **Tests automatisés** (unittest/pytest)
- [ ] **API REST** pour applications mobiles
- [ ] **Base de données PostgreSQL** pour la production
- [ ] **Cache Redis** pour les performances

#### 🎨 UX/UI
- [ ] **Mode sombre** pour l'interface
- [ ] **PWA** (Progressive Web App)
- [ ] **Filtres avancés** avec autocomplétion
- [ ] **Système de favoris** pour suivre des objets

#### 🛡️ Sécurité
- [ ] **Rate limiting** pour les requêtes
- [ ] **Validation côté serveur** renforcée  
- [ ] **HTTPS obligatoire** en production
- [ ] **Modération** des contenus

---

### 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Crée une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit tes changements (`git commit -am 'Ajoute nouvelle fonctionnalité'`)
4. Push sur la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvre une Pull Request

---

### 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

### 👨‍💻 Auteur

Développé avec ❤️ par **y4nn**

---

*Dernière mise à jour : Juin 2025*
