<<<<<<< HEAD

=======
>>>>>>> aa8e61e (✨ Version simplifiée Streamlit (CSV uniquement))
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📍 Espaces de Coworking - Paris & IDF")

# Chargement des données locales
df = pd.read_csv("data/coworkings_paris_geo.csv")

# Nettoyage
df = df.dropna(subset=["Latitude", "Longitude"])
df["Code Postal"] = df["Code Postal"].astype(str)
df["Ville"] = df["Ville"].astype(str).str.strip().str.title()

# Recherche
search_query = st.text_input("🔍 Rechercher par nom ou adresse :", "")
if search_query:
    df = df[df["Nom"].str.contains(search_query, case=False, na=False) | df["Adresse"].str.contains(search_query, case=False, na=False)]

# Sélecteur de ville
villes = ["Toutes"] + sorted(df["Ville"].dropna().unique())
ville_selection = st.selectbox("🏙️ Filtrer par ville :", villes)
if ville_selection != "Toutes":
    df = df[df["Ville"] == ville_selection]

# Carte
st.subheader("🗺️ Carte des coworkings")
m = folium.Map(location=[48.8566, 2.3522], zoom_start=11)
for _, row in df.iterrows():
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=f"<b>{row['Nom']}</b><br>{row['Adresse']}",
        tooltip=row["Nom"],
        icon=folium.Icon(color='purple', icon='briefcase', prefix='fa')
    ).add_to(m)
st_folium(m, width=1200, height=400)

# Graphique
st.subheader("📊 Nombre d'espaces par ville")
ville_counts = df["Ville"].value_counts().reset_index()
ville_counts.columns = ["Ville", "Nombre"]
fig = px.bar(ville_counts, x="Ville", y="Nombre", title="Répartition des espaces de coworking", color_discrete_sequence=["purple"])
st.plotly_chart(fig, use_container_width=True)
