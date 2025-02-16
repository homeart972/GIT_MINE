import asyncio
from playwright.async_api import async_playwright
import json
import pandas as pd
from datetime import datetime
import re

USER_DATA_DIR = "user_data"  # Dossier où Playwright stockera la session

async def save_user_data(context):
    """Sauvegarde les cookies, localStorage et sessionStorage dans user_data.json."""
    page = await context.new_page()
    data = {
        "cookies": await context.cookies(),
        "localStorage": await page.evaluate("() => Object.entries(localStorage)"),
        "sessionStorage": await page.evaluate("() => Object.entries(sessionStorage)"),
    }
    with open("user_data.json", "w") as f:
        json.dump(data, f)
    print("✅ Session sauvegardée dans user_data.json")

async def publish_post(playwright, title, video_url, text_content):
    """Lance un navigateur avec session persistante et publie un post."""
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR, headless=False
    )

    page = await context.new_page()
    await page.goto("https://manage.wix.com/my-account/sites")
    await page.wait_for_load_state("load")

    # Vérifie si l'utilisateur est connecté
    if "login" in page.url:
        print("⚠️ Session expirée, connexion requise.")
        await page.wait_for_selector("input[type='password']", timeout=60000)
        input("✅ Appuie sur Entrée après connexion...")  # Attente utilisateur
        await save_user_data(context)

    print("✅ Connexion réussie avec le user_data !")
    
    if "signin" in page.url:
        await page.goto("https://users.wix.com/signin")
        await page.wait_for_load_state("load")
        await page.locator("label:has-text('S'inscrire ou se connecter avec un e-mail')").click()
        await page.fill("label:has-text('S'inscrire ou se connecter avec un e-mail')", "homeart97200@gmail.com")
        await page.click("button:has-text('Continuer avec un e‑mail')")
        await page.wait_for_timeout(3000)
        await page.fill("label:has-text('Mot de passe')", "Jennyssa01")
        
        # Attendez que l'utilisateur résolve le CAPTCHA
        try:
            await page.wait_for_selector("input[type='checkbox']", timeout=5000)
            print("Veuillez compléter le CAPTCHA manuellement.")
            await asyncio.sleep(30)  # Pause pour donner le temps de résoudre
        except:
            print("Aucun CAPTCHA détecté, continuation de l'automatisation.")
        
        await page.click("button:has-text('Se connecter')")
        await page.wait_for_timeout(4000)
        await page.wait_for_load_state("load")
        await page.wait_for_timeout(5000)

    # Aller à la page des posts
    await page.goto("https://manage.wix.com/dashboard/e00f7aaf-a34a-401f-89e7-f8f364e23fec/blog/posts")
    #await page.wait_for_load_state("load")
    await page.wait_for_timeout(5000)

    # Aller à la page des posts
    #await page.goto("https://manage.wix.com/dashboard/e00f7aaf-a34a-401f-89e7-f8f364e23fec/blog/posts")
    #await page.wait_for_timeout(5000)

    # Créer un nouveau post
    await page.click("button:has-text('Créer un nouveau post')")
    # await page.wait_for_selector("input[placeholder='Ajoutez un titre original']", timeout=80000)
    await page.get_by_placeholder("Ajouter un titre").fill(title)
    await page.wait_for_timeout(5000)
    '''
    
    # Créer un nouveau post
    await page.click("button:has-text('Créer un nouveau post')")
    print("Création du post en cours...")
    try:
        await page.wait_for_selector("input[placeholder='Ajoutez un titre original']", timeout=60000)
        await page.fill("input[placeholder='Ajoutez un titre original']", title)
        print("Titre ajouté avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'ajout du titre : {e}")
        return  # Arrêtez cette itération si l'erreur persiste
    '''



    # Ajouter le texte principal
    editor_locator = page.locator(".tiptap")
    await editor_locator.fill(f"{text_content}\n\n")  # Ajouter deux sauts de ligne après le texte principal
    await page.wait_for_timeout(2000)
    # Déplacer le curseur à la fin du texte
    await editor_locator.evaluate("node => { const range = document.createRange(); range.selectNodeContents(node); range.collapse(false); const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range); }")

    # Simuler l'appui sur "Entrée" pour ajouter deux nouvelles lignes
    
    await editor_locator.press("Enter")
    await editor_locator.press("Enter")

    # Simuler un clic à la position actuelle (après les deux sauts de ligne)
    await editor_locator.click()

    # Ajouter la vidéo
    await page.get_by_role("button", name="Ajouter").click()
    await page.wait_for_timeout(3000)
    #page.locator("div").filter(has_text="Vidéo").locator("img").nth(2).click()
    await page.locator("div").filter(has_text=re.compile(r"^ImageGalerieVidéoGIFFichier$")).locator("img").nth(2).click()
    await page.get_by_placeholder("Ex. www.youtube.com/exemple").fill(video_url)
    await page.get_by_role("button", name="Intégrer la vidéo").click()
    await page.wait_for_timeout(2000)


    '''
    # Ajouter la vidéo à la fin
    await page.click("button:has-text('Ajouter')")
    await page.wait_for_selector("div:has-text('Vidéo')")
    await page.locator("div:has-text('Vidéo') img").nth(2).click()
    await page.fill("input[placeholder='Ex. www.youtube.com/exemple']", video_url)
    await page.click("button:has-text('Intégrer la vidéo')")
    await page.wait_for_timeout(2000)
    '''

    # Publier le post
    await page.click("button:has-text('Publier')")
    await page.wait_for_timeout(5000)
    print(f"Post '{title}' publié avec succès.")

    # Fermeture du contexte du navigateur
    await context.close()

# Fonction principale pour lire le fichier Excel et publier les posts du jour
async def main():
    # Charger le fichier Excel
    df = pd.read_excel(r"posts_to_publish.xlsx")

    # Filtrer les posts pour aujourd'hui
    today = datetime.now().date()
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    posts_today = df[df['Date'] == today]

    if posts_today.empty:
        print("Aucun post à publier aujourd'hui.")
        return

    # Lancer Playwright et publier les posts du jour
    async with async_playwright() as playwright:
        for _, row in posts_today.iterrows():
            title = row['Titre']
            video_url = row['Lien Video']
            text_content = row['Texte']
            await publish_post(playwright, title, video_url, text_content)
            print(f"Post '{title}' publié avec succès pour la date {today}")

# Exécuter le script
if __name__ == "__main__":
    asyncio.run(main())
