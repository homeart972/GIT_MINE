# lecture vidéo Remixed by DJAMA

import time
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright
import pandas as pd

# Fonction pour ouvrir et lire la vidéo depuis le lien YouTube
def play_video(page, titre, lien):
    print(f"🎬 Lecture de la vidéo '{titre}' depuis : {lien}")

    # Aller directement à l'URL de la vidéo
    page.goto(lien)

    # Attendre que la vidéo charge
    page.wait_for_selector("video", timeout=10000)

    # Vérifier si la vidéo est bien détectée
    video_player = page.query_selector("video")
    if video_player:
        print("✅ Vidéo détectée, lancement en cours...")
        page.keyboard.press("k")  # Raccourci YouTube pour lecture/pause
    else:
        print("❌ Impossible de détecter la vidéo.")

    # Attendre 10 secondes avant de passer à la suivante (facultatif)
    time.sleep(20)

def run(playwright: Playwright):
    # Lancer le navigateur
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Charger le fichier Excel
    df = pd.read_excel(r"E:\PYTHON_DOC\djama_publish.xlsx")

    # Obtenir la date actuelle et filtrer les vidéos à lire
    date_actuelle = datetime.now().date()
    lignes_valides = df[df['Date'].apply(pd.to_datetime).dt.date < date_actuelle]

    if lignes_valides.empty:
        print("⚠️ Aucune vidéo à lire.")
        context.close()
        browser.close()
        return

    for index, row in lignes_valides.iterrows():
        try:
            titre = row['Titre']
            lien = row['Lien']  # Lien YouTube de la vidéo

            if pd.notna(lien) and lien.startswith("https://www.youtube.com/watch"):
                play_video(page, titre, lien)
            else:
                print(f"❌ Lien invalide pour '{titre}'")

        except Exception as e:
            print(f"❌ Erreur lors de la lecture de '{titre}': {e}")

    print("🚀 Toutes les vidéos ont été lues.")
    context.close()
    browser.close()

# Exécuter avec Playwright
with sync_playwright() as playwright:
    run(playwright)

print('🎉 Lecture terminée.')
