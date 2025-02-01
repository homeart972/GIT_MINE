from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # Lancer Chromium en mode headless
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Aller sur un site web (exemple : Google)
        page.goto("https://www.google.com")

        # Prendre une capture d'écran
        page.screenshot(path="screenshot.png")

        print("✅ Capture d'écran enregistrée : screenshot.png")

        # Fermer le navigateur
        browser.close()

# Exécuter le script
if __name__ == "__main__":
    run()
