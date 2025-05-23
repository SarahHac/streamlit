import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📍 Espaces de Coworking - Paris & IDF")

# Chargement des données
df = pd.read_csv("data/coworkings_paris_geo.csv")

# Vérification des colonnes nécessaires
if "Latitude" not in df.columns or "Longitude" not in df.columns:
    st.error("❌ Les colonnes 'Latitude' et 'Longitude' sont manquantes dans le fichier CSV.")
    st.stop()

# Nettoyage de base
df = df.dropna(subset=["Latitude", "Longitude"])

## Extraction depuis l'adresse
df["Code Postal"] = df["Adresse"].str.extract(r"(\d{5})")
df["Ville"] = df["Adresse"].str.split(",").apply(lambda x: x[-1].strip().title() if isinstance(x, list) and len(x) > 1 else "")


# Ville affichée homogène
def extraire_ville_affichee(row):
    cp = row["Code Postal"]
    if pd.notna(cp) and cp.startswith("75"):
        arrondissement = cp[-2:]
        try:
            int(arrondissement)  # vérifie que c’est bien un numéro
            return f"Paris {arrondissement.zfill(2)}"
        except:
            return "Paris"
    elif pd.notna(row["Ville"]) and row["Ville"] != "nan":
        return row["Ville"]
    else:
        return "Autre"

df["ville_affichee"] = df.apply(extraire_ville_affichee, axis=1)


if df.empty:
    st.warning("⚠️ Aucun espace de coworking avec coordonnées valides.")
    st.stop()

# 🔍 Recherche libre
search_query = st.text_input("🔍 Rechercher par nom ou adresse :", "")

# 🏙️ Filtre par ville ou arrondissement
ville_options = ["Toutes"] + sorted(df["ville_affichee"].dropna().unique())
ville_selection = st.selectbox("🏙️ Filtrer par ville ou arrondissement :", ville_options)

# Application des filtres
filtered_df = df.copy()
if search_query:
    filtered_df = filtered_df[filtered_df["Nom"].str.contains(search_query, case=False, na=False) | filtered_df["Adresse"].str.contains(search_query, case=False, na=False)]
if ville_selection != "Toutes":
    filtered_df = filtered_df[filtered_df["ville_affichee"] == ville_selection]

# 🗺️ Carte interactive avec points violets
m = folium.Map(location=[48.8566, 2.3522], zoom_start=11)

for _, row in filtered_df.iterrows():
    adresse = row["Adresse"] if pd.notna(row["Adresse"]) else ""
    popup = (
        f"<b>{row['Nom']}</b><br>{adresse}<br>{row['Ville']} {row['Code Postal']}<br>"
        f"<a href='{row['Site']}' target='_blank'>Site web</a>"
        if pd.notna(row['Site']) else
        f"<b>{row['Nom']}</b><br>{adresse}<br>{row['Ville']} {row['Code Postal']}"
    )
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=popup,
        tooltip=row["Nom"],
        icon=folium.Icon(color='purple', icon='briefcase', prefix='fa')  # violet 💜
    ).add_to(m)


with st.container():
    st.subheader("🗺️ Carte interactive des espaces de coworking")
    st_folium(m, width=1200, height=350)

st.divider()  # Ajoute une séparation nette sans espace flou


# 📊 Répartition dynamique : par Ville ou Département
st.subheader("📊 Répartition des coworkings")

# Ajout du champ Département si manquant
if "Département" not in df.columns:
    df["Département"] = df["Code Postal"].astype(str).str[:2]

# Sélecteur
filtre = st.selectbox("Afficher le graphique par :", ["Ville", "Département"])

# Données filtrées
if filtre == "Ville":
    data_counts = df["ville_affichee"].value_counts().reset_index()
    data_counts.columns = ["Ville", "Nombre"]

    # Tri des Paris 01 → Paris 20
    def sort_key(ville):
        if ville.startswith("Paris"):
            try:
                return int(ville.split(" ")[1].zfill(2))
            except:
                return 99
        return 100 + ord(ville[0])

    data_counts["Sort"] = data_counts["Ville"].apply(sort_key)
    data_counts = data_counts.sort_values("Sort")
    x_col = "Ville"
else:
    data_counts = df["Département"].value_counts().reset_index()
    data_counts.columns = ["Département", "Nombre"]
    x_col = "Département"

# Affichage graphique
fig = px.bar(
    data_counts,
    x=x_col,
    y="Nombre",
    title=f"Nombre d'espaces de coworking par {x_col.lower()}",
    color_discrete_sequence=["purple"]
)
st.plotly_chart(fig, use_container_width=True)
