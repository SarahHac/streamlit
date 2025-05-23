import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from unidecode import unidecode
import time
from opencage.geocoder import OpenCageGeocode

def get_coworking_links():
    url = "https://www.leportagesalarial.com/coworking/"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erreur lors de l'accès à la page principale: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    postal_code_pattern = re.compile(r'\b(75|77|78|91|92|93|94|95)\d{3}\b')
    links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        if postal_code_pattern.search(href):
            full_url = href if href.startswith("http") else f"https://www.leportagesalarial.com{href}"
            links.append(full_url)

    return list(set(links))

def extract_coworking_info(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        info = {
            'Nom': '',
            'Adresse': '',
            'Code Postal': '',
            'Ville': '',
            'Téléphone': '',
            'Site': ''
        }

        title = soup.find('title')
        if title:
            info['Nom'] = title.text.strip().split(':')[0]

        for li in soup.find_all('li'):
            strong = li.find('strong')
            if strong:
                label = unidecode(strong.text.strip().lower())
                content = strong.next_sibling.strip() if strong.next_sibling and isinstance(strong.next_sibling, str) else ""
                if 'adresse' in label:
                    info['Adresse'] = content
                    # Extraction du CP et Ville si possible
                    match = re.search(r'(\d{5})\s+(.+)', content)
                    if match:
                        info['Code Postal'] = match.group(1)
                        info['Ville'] = match.group(2).strip().title()
                elif 'code postal' in label and not info['Code Postal']:
                    info['Code Postal'] = content.strip()
                elif 'ville' in label and not info['Ville']:
                    info['Ville'] = content.strip().title()
                elif 'telephone' in label:
                    info['Téléphone'] = content.replace(":", "").strip()
                elif 'site' in label:
                    a_tag = li.find('a')
                    if a_tag and a_tag.has_attr('href'):
                        info['Site'] = a_tag['href']

        return info
    except Exception as e:
        print(f"Erreur sur {url} : {e}")
        return None

def geolocate_dataframe(df):
    key = "5fb01c04e7f84dcea30361f63d4859ec"
    geocoder = OpenCageGeocode(key)

    def geocode_address(row):
        full_address = f"{row['Adresse']}, {row['Code Postal']} {row['Ville']}".strip()
        try:
            results = geocoder.geocode(full_address)
            if results and len(results):
                lat = results[0]['geometry']['lat']
                lng = results[0]['geometry']['lng']
                return pd.Series([lat, lng])
            else:
                print(f"[⚠️] Adresse non trouvée : {full_address}")
                return pd.Series([None, None])
        except Exception as e:
            print(f"[❌] Erreur pour {full_address} : {e}")
            return pd.Series([None, None])

    df[['Latitude', 'Longitude']] = df.apply(geocode_address, axis=1)
    return df

# === MAIN ===
def main():
    links = get_coworking_links()
    print(f"{len(links)} liens trouvés")

    data = []
    for i, link in enumerate(links):
        print(f"Scraping {i+1}/{len(links)}: {link}")
        info = extract_coworking_info(link)
        if info:
            data.append(info)
        time.sleep(1)

    df = pd.DataFrame(data)

    # Nettoyage des champs
    df["Adresse"] = df["Adresse"].astype(str).str.replace(":", "", regex=False).str.strip()
    df["Code Postal"] = df["Code Postal"].astype(str).str.extract(r"(\d{5})")
    df["Ville"] = df["Ville"].astype(str).str.strip().str.title()

    # Ajout du département
    def extraire_departement(cp):
        if isinstance(cp, str) and len(cp) >= 2:
            return cp[:2]
        return None

    df["Département"] = df["Code Postal"].apply(extraire_departement)

    # Géolocalisation
    df = geolocate_dataframe(df)

    # Sauvegarde
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/coworkings_paris_geo.csv", index=False)
    print("✅ Fichier sauvegardé dans data/coworkings_paris_geo.csv")

if __name__ == "__main__":
    main()
