# MonPetitDressing — Rendu intermédiaire PII 2026 (ENSC)

Application Data de gestion de dressing personnel

## Prérequis

- Python 3.10 ou supérieur
- Un accès à une base de données PostgreSQL

## Installation

### 1. Cloner le dépôt

- git clone https://github.com/Pierre-Viven/MonPetitDressing
- cd MonPetitDressing

### 2. Créer et activer un environnement virtuel (recommandé)

**Windows**
- python -m venv venv
- venv\Scripts\activate

**macOS / Linux**
- python3 -m venv venv
- source venv/bin/activate

### 3. Installer les dépendances

**Windows**
python -m pip install -r dependances.txt

**macOS / Linux**
- pip3 install -r dependances.txt

### 4. Configurer la base de données

Copiez le fichier d'exemple et renseignez vos identifiants PostgreSQL :

- cp .env.example .env

Puis éditez le fichier `.env` avec vos accès. (contactez pviven@ensc.fr si besoin)

### 5. Lancer l'application

**Windows**
- python -m streamlit run app_streamlit.py

**macOS / Linux**
- python3 -m streamlit run app_streamlit.py

L'interface s'ouvre automatiquement dans votre navigateur
à l'adresse http://localhost:8501

