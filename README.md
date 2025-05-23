# 📍 Coworking Paris & Île-de-France – Visualisation interactive

Projet réalisé dans le cadre d’un Master 2, cette application Streamlit vise à proposer une visualisation interactive des espaces de coworking situés à Paris et en Île-de-France, en croisant données géographiques, web scraping et analyse visuelle.

🔗 Application déployée : [https://projetfinalhacenesarah.streamlit.app/](https://projetfinalhacenesarah.streamlit.app/)

---

## 🎯 Objectif

Le projet a pour but de :

- Scraper des données d’espaces de coworking depuis un site web ciblé.
- Géolocaliser automatiquement chaque espace via l’API OpenCage.
- Construire une visualisation interactive permettant :
  - une recherche par nom ou adresse,
  - un filtrage par ville ou arrondissement,
  - une carte Folium dynamique,
  - une répartition visuelle par ville ou département avec Plotly.

---

## ⚙️ Architecture du projet

```
📁 streamlit/
├── app_coworking_streamlit_final.py         ← Fichier principal Streamlit
├── scraping_colab_geo_streamlit_ready.py    ← Script de scraping + géolocalisation
├── requirements.txt                         ← Liste des dépendances Python
├── data/
│   └── coworkings_paris_geo.csv             ← Données enrichies (scrapées + géocodées)
└── .streamlit/
    └── config.toml                          ← Configuration de déploiement Streamlit Cloud
```

---

## 🐍 Version Python utilisée

Le projet utilise **Python 3.10**, version stable et compatible avec :

- `pandas >= 2.2` pour un traitement efficace des DataFrames,
- `plotly >= 5.18` pour la génération de graphiques modernes,
- `streamlit-folium` pour l’intégration de cartes interactives.

Cette version permet aussi de garantir la compatibilité avec les dépendances utilisées sur **Streamlit Cloud**, évitant ainsi les erreurs d’environnement.

---

## 🧪 Étapes d’exécution en local

1. **Cloner le dépôt** :
```bash
git clone https://github.com/SarahHac/streamlit.git
cd streamlit
```

2. **Créer et activer un environnement virtuel** :
```bash
python3.10 -m venv env
source env/bin/activate  # (sur Mac/Linux)
```

3. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

4. **Lancer l’application Streamlit** :
```bash
streamlit run app_coworking_streamlit_final.py
```

---

## 🧹 Fichiers clés détaillés

### `scraping_colab_geo_streamlit_ready.py`
- Scrape automatiquement des espaces de coworking sur `leportagesalarial.com`.
- Nettoie les données (adresse, CP, ville...).
- Géolocalise chaque point grâce à OpenCage.
- Génère un fichier `data/coworkings_paris_geo.csv` prêt à être utilisé.

### `app_coworking_streamlit_final.py`
- Lit les données enrichies.
- Affiche :
  - une **carte Folium** avec des marqueurs cliquables,
  - un **graphique Plotly** dynamique,
  - une **barre de recherche** et des **filtres** par ville.
