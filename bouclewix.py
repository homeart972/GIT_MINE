import time
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright
import pandas as pd

# Fonction pour traiter chaque titre
def process_individual(page, titre):
    # Remplir le champ de recherche avec le titre
    print(f"Traitement du titre : {titre}")
    
    page.frame_locator("frame[name=\"Top\"]").get_by_role("link", name="Blog").click()
    page.frame_locator("frame[name=\"Top\"]").get_by_label("Rechercher").click()
    page.frame_locator("frame[name=\"Top\"]").get_by_placeholder("Rechercher").fill(titre)
    page.frame_locator("frame[name=\"Top\"]").get_by_placeholder("Rechercher").press("Enter")
    print(f"Le lien pour le titre '{titre}' a été cliqué.")
    page.frame_locator("frame[name=\"Top\"]").get_by_text(titre).click()
    #page.frame_locator("frame[name=\"Top\"]").locator("#post-footer").get_by_role("button", name="Vous n'aimez plus ce post").click()
    #page.frame_locator("frame[name=\"Top\"]").get_by_label("Play video").click()
    #page.frame_locator("frame[name=\"Top\"]").frame_locator("iframe[title=\"Khalid - Location \\(Lyrics\\)\"]").locator("video").click()
    page.frame_locator("frame[name=\"Top\"]").get_by_label("Play video").dblclick()
    #page.frame_locator("frame[name=\"Top\"]").get_by_label("Lire(k)").click()
    
    
    '''
    
    for frame in page.frames:
        print("Frame name:", frame.name, "| URL:", frame.url)

    
    
    try:
    # Trouver le bouton "Play" basé sur l'attribut 'aria-label'
    
        inner_frame = page.frame_locator("frame[name=\"Top\"]").frame_locator("iframe[title='titre']")
        inner_frame.locator("button[aria-label='Lire']").click()

        #page.frame_locator("frame[name=\"Top\"]").frame_locator("iframe[title=titre]").get_by_label("Lire Raccourci clavier k").click()
        #page.frame_locator("frame[name=\"Top\"]").frame_locator("iframe[title=\"Bas - Tribe with J\\.Cole\"]").get_by_label("Pause Raccourci clavier k").click()

        #play_button = page.frame_locator("frame[name=\"Top\"]").locator("button[aria-label='Lire']")
        #play_button = page.frame_locator("frame[name=\"Top\"]").locator("button.ytp-play-button[aria-label='Lire']")

        #play_button.wait_for(timeout=5000)
        #play_button.click()  # Cliquer sur le bouton Play
    
        #frame.locator("video").click()
    
        # Envoyez le raccourci clavier 'k' via la page ou directement à la frame
        #page.frame_locator("frame[name=\"Top\"]")
        #page.keyboard.press('k')
        
        #frame.press("k")
        time.sleep(2)
        #page.frame_locator("frame[name=\"Top\"]").get_by_label("Play video").click()
        #page.keyboard.press('k')
        #frame.press("k")
        #page.frame_locator("frame[name=\"Top\"]").keyboard.press("k")
        print("Le raccourci clavier 'k' a été envoyé pour contrôler la vidéo.")
        print("Le bouton 'Play' a été cliqué avec succès.")
        time.sleep(10)  # Attendre que la vidéo joue un peu
    except Exception as e:
        print(f"Erreur : Impossible de cliquer sur le bouton 'Play'. ({e})")
    #page.frame_locator("frame[name=\"Top\"]").get_by_placeholder("Rechercher").fill(titre)
    #page.frame_locator("frame[name=\"Top\"]").get_by_placeholder("Rechercher").press("Enter")
    
    '''
    try:
        video_frame.evaluate("document.querySelector('button[aria-label=\"Lire\"]').dblclick()")
        print("Le bouton 'Play' a été cliqué via JavaScript.")
    except Exception as e:
        print(f"Erreur : Impossible de cliquer sur le bouton 'Play' avec JavaScript. ({e})")


    
    '''
    
    # avec javascript
    try:
        # Forcer la lecture via JavaScript
        page.frame_locator("frame[name=\"Top\"]").evaluate("document.querySelector('button[aria-label=\"Lire\"]').click()")
        print("Lecture de la vidéo déclenchée avec JavaScript.")
        time.sleep(10)
    except Exception as e:
        print(f"Erreur : Impossible de déclencher la lecture de la vidéo avec JavaScript. ({e})")
    '''


    
    time.sleep(5)  # Temps d'attente pour permettre au site de charger les résultats
    # Cliquer sur le lien correspondant (vérifiez que cela correspond à votre site)
    #page.frame_locator("frame[name=\"Top\"]").get_by_role("link", name="Blog").click()
    #page.frame_locator("frame[name=\"Top\"]").get_by_role("link", name="Blog").click()
    
    '''
    try:
        page.frame_locator("frame[name=\"Top\"]").get_by_role("link", name=titre).click()
        print(f"Le lien pour le titre '{titre}' a été cliqué.")
    except Exception as e:
        print(f"Erreur : Impossible de cliquer sur le lien pour le titre '{titre}'. Vérifiez qu'il existe. ({e})")
    '''





def run(playwright: Playwright) -> None:
    # Lancer le navigateur
    browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    #browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://onedayclip.free.fr/")

    # Charger le fichier Excel
    df = pd.read_excel(r"E:\PYTHON_DOC\wix_publish.xlsx")

    # Obtenir la date actuelle
    date_actuelle = datetime.now().date()

    # Filtrer les lignes où la date est avant la date actuelle
    lignes_valides = df[df['Date'].apply(pd.to_datetime).dt.date < date_actuelle]

    # Vérifier si des lignes valides existent
    if lignes_valides.empty:
        print("Aucune ligne valide pour le traitement.")
        context.close()
        browser.close()
        return

    # Répéter le traitement 3 fois
    for iteration in range(3):
        print(f"=== Début de l'itération {iteration + 1} ===")
        for index, row in lignes_valides.iterrows():
            try:
                titre = row['Titre']  # Extraire le titre
                date_titre = pd.to_datetime(row['Date']).date()
                print(f"[Itération {iteration + 1}] Traitement du titre '{titre}' avec la date {date_titre}.")
                process_individual(page, titre)
            except Exception as e:
                print(f"[Itération {iteration + 1}] Erreur lors du traitement de la ligne {index + 1}: {e}")

    # Fermer le contexte et le navigateur
    print("Traitement terminé.")
    context.close()
    browser.close()

# Exécuter avec Playwright
with sync_playwright() as playwright:
    run(playwright)

print('Traitement fini.')

