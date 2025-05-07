import os
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scraping_emails():
    # Configuración inicial
    env_path = r"C:\Users\csanh\OneDrive\Escritorio\PDF PUC\Semestre 5\Innovación, desarollo y emprendimiento\Codigo web scrapping\credenciales.env"
    load_dotenv(env_path)

    username = os.getenv("mail_user")
    password = os.getenv("mail_password")
    bank = os.getenv("bank_user")

    # Configuración del navegador
    chrome_options = Options()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 1. Inicio de sesión
        driver.get("https://mail.google.com")
        
        # Campo de email
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "identifierId"))
        ).send_keys(username + Keys.RETURN)
        
        # Campo de contraseña
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Passwd"))
        ).send_keys(password + Keys.RETURN)

        # 2. Búsqueda de correos del banco
        search_bar = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Buscar en correo']"))
        )
        search_bar.send_keys(bank + Keys.RETURN)

        # 3. Extracción de correos
        emails = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='main'] tr.zA"))
        )

        bank_emails = []
        for email in emails[:10]:  # Limitar a los primeros 10 para prueba
            try:
                sender = email.find_element(By.CSS_SELECTOR, "span[email]:not([email=''])").get_attribute("email")
                subject = email.find_element(By.CSS_SELECTOR, "span[data-legacy-thread-id]").text
                snippet = email.find_element(By.CSS_SELECTOR, "span[data-legacy-snippet]").text
                
                bank_emails.append({
                    "sender": sender,
                    "subject": subject,
                    "snippet": snippet,
                    "html": email.get_attribute("outerHTML")[:200] + "..."
                })
            except Exception as e:
                print(f"Error procesando email: {str(e)}")
                continue

        # Guardar resultados
        with open("bank_emails.json", "w", encoding="utf-8") as f:
            json.dump(bank_emails, f, indent=2, ensure_ascii=False)

        print(f"Se encontraron {len(bank_emails)} correos del banco")
        return bank_emails

    except Exception as e:
        print(f"Error durante el scraping: {str(e)}")
        return None
    finally:
        driver.quit()

# Ejecutar la función
if __name__ == "__main__":
    emails = scraping_emails()
    if emails:
        for idx, email in enumerate(emails, 1):
            print(f"\nEmail #{idx}:")
            print(f"Remitente: {email['sender']}")
            print(f"Asunto: {email['subject']}")
            print(f"Vista previa: {email['snippet']}")