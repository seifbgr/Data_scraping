from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import time
import pandas as pd
import random

# Configuration améliorée du navigateur
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(options=options)
driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.maximize_window()

# URL de départ
driver.get('https://www.aliexpress.us/w/wholesale-microphone.html?spm=a2g0o.productlist.search.0')

# Fonction pour récupérer le texte ou None si l'élément n'existe pas
def get_text_or_none(product, xpath):
    try:
        return product.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        return None
    except StaleElementReferenceException:
        return None

# Fonction pour faire défiler la page de manière plus naturelle
def scroll_with_random_pauses(driver):
    # Hauteur totale de la page
    total_height = driver.execute_script("return document.body.scrollHeight")
    
    # Faire défiler par étapes avec des pauses aléatoires
    current_position = 0
    step = random.randint(300, 500)  # Défilement par petits incréments aléatoires
    
    while current_position < total_height:
        scroll_to = min(current_position + step, total_height)
        driver.execute_script(f"window.scrollTo({current_position}, {scroll_to});")
        current_position = scroll_to
        
        # Pause aléatoire pour simuler un comportement humain
        time.sleep(random.uniform(0.5, 1))
        
        # Pause plus longue à certains points pour simuler la lecture
        if random.random() < 0.2:  # 20% de chance de "lire" la page
            time.sleep(random.uniform(0.5, 1))

# Accepter les cookies si nécessaire
try:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="gdpr-new-container"]/div/div[2]/button[3]'))
    ).click()
    print("Cookies acceptés")
except (TimeoutException, NoSuchElementException) as e:
    print("Pas de dialogue de cookies ou impossible de l'accepter:", e)

# Attendre le chargement initial
time.sleep(1)

# Fermer le popup si présent
try:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class = 'eo_bp eo_y']"))
    ).click()
    print("Popup fermé")
except (TimeoutException, NoSuchElementException) as e:
    print("Pas de popup ou impossible de le fermer:", e)

# Listes pour stocker les données
titles = []
prices = []
eval_ratings = []
sold = []
prices_avant = []
save = []
reduc = []
liens = []

# Page actuelle
page = 1
max_pages = 60  # Limite maximale de pages à scraper

while page <= max_pages:
    print(f"Traitement de la page {page}")
    
    # Attendre que la page se charge complètement
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'card-list'))
        )
    except TimeoutException:
        print(f"Impossible de charger la page {page}, arrêt du scraping")
        break
    
    # Faire défiler la page pour charger tous les éléments
    scroll_with_random_pauses(driver)
    
    # Récupérer les produits
    try:
        product_elements = container.find_elements(By.XPATH, ".//div[@class = 'jr_js card-out-wrapper']")
        print(f"Nombre de produits trouvés: {len(product_elements)}")
        
        if not product_elements:
            print("Aucun produit trouvé, vérification de structure alternative...")
            # Essayer des sélecteurs alternatifs si la structure a changé
            product_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'card-out-wrapper')]")
            print(f"Sélecteur alternatif: {len(product_elements)} produits trouvés")
    except Exception as e:
        print(f"Erreur lors de la récupération des produits: {e}")
        product_elements = []
    
    # Extraction des données
    for product in product_elements:
        try:
            titles.append(get_text_or_none(product, ".//h3[@class = 'jr_kp']"))
            prices.append(get_text_or_none(product, ".//div[@class = 'jr_kr']"))
            prices_avant.append(get_text_or_none(product, ".//div[@class = 'jr_ks']"))
            eval_ratings.append(get_text_or_none(product, ".//span[@class = 'jr_kf']"))
            sold.append(get_text_or_none(product, ".//span[@class = 'jr_j7']"))
            reduc.append(get_text_or_none(product, ".//span[@class = 'jr_kt']"))
            link = product.find_element(By.XPATH, "./a")
            href = link.get_attribute("href")
            liens.append(href)

        except StaleElementReferenceException:
            print("Élément périmé, passage au suivant")
            continue
    
    # Sauvegarder les données actuelles au cas où le script échouerait plus tard
    if page % 5 == 0:
        temp_df = pd.DataFrame({
            'Titres': titles,
            'Prix': prices,
            'Prix_av_redu': prices_avant,
            'Evalutaion': eval_ratings,
            'Commandes': sold,
            'Reduction': reduc,
            'Liens'   : liens,
        })
        temp_df.to_csv(f'Ali_chaise_page_{page}.csv', index=False)
        print(f"Données sauvegardées jusqu'à la page {page}")
    
    # Passer à la page suivante
    page += 1
    
    if page <= max_pages:
        try:
            # Attendre que la pagination soit disponible
            pagination = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "comet-pagination"))
            )
            
            # Méthode 1: Essayer de cliquer sur le bouton "Suivant"
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'comet-pagination-next')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_button)
                print("Navigation avec bouton Suivant")
            except Exception as e:
                print(f"Erreur avec bouton Suivant: {e}")
                
                # Méthode 2: Essayer de cliquer sur le numéro de page
                try:
                    next_page_link = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, f"//li[contains(@class, 'comet-pagination-item')]//a[text()='{page}']"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_link)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", next_page_link)
                    print(f"Navigation vers page {page} par numéro")
                except Exception as e2:
                    print(f"Erreur avec numéro de page: {e2}")
                    
                    # Méthode 3: Essayer de naviguer via l'URL
                    try:
                        current_url = driver.current_url
                        if 'page=' in current_url:
                            new_url = current_url.replace(f'page={page-1}', f'page={page}')
                        else:
                            separator = '&' if '?' in current_url else '?'
                            new_url = f"{current_url}{separator}page={page}"
                        
                        print(f"Navigation via URL: {new_url}")
                        driver.get(new_url)
                    except Exception as e3:
                        print(f"Toutes les méthodes de navigation ont échoué: {e3}")
                        break
            
            # Attendre que la nouvelle page soit chargée
            time.sleep(random.uniform(1, 2))
            
            # Vérifier que nous sommes bien sur la nouvelle page
            try:
                # Vérifier si une nouvelle page s'est bien chargée (le contenu est différent)
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(container)
                )
                print(f"Chargement de la page {page} confirmé")
            except TimeoutException:
                print(f"La page semble ne pas avoir changé, vérification manuelle nécessaire")
                
        except Exception as e:
            print(f"Erreur lors de la navigation vers la page {page}: {e}")
            break

# Sauvegarder toutes les données
df = pd.DataFrame({
    'titles': titles,
    'prices': prices,
    'prices_avant': prices_avant,
    'eval': eval_ratings,
    'sold': sold,
    'reduc': reduc,
    'Liens'   : liens,

})

df.to_csv('Ali_chaise_complet.csv', index=False)
print(f"Extraction terminée. {len(titles)} produits extraits.")

# Fermer le navigateur
driver.quit()