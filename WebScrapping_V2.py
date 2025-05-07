from selenium import webdriver
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from time import sleep
import re
from datetime import datetime
import sys
from contextlib import contextmanager

# Diccionario para traducir meses en español a números
MESES_ES = {
    'enero': 1, 'ene': 1,
    'febrero': 2, 'feb': 2,
    'marzo': 3, 'mar': 3,
    'abril': 4, 'abr': 4,
    'mayo': 5, 'may': 5,
    'junio': 6, 'jun': 6,
    'julio': 7, 'jul': 7,
    'agosto': 8, 'ago': 8,
    'septiembre': 9, 'sep': 9,
    'octubre': 10, 'oct': 10,
    'noviembre': 11, 'nov': 11,
    'diciembre': 12, 'dic': 12
}

def scraping_emails():
    @contextmanager
    def get_driver():
        env_path = r"C:\Users\csanh\OneDrive\Escritorio\PDF PUC\Semestre 5\Innovación, desarollo y emprendimiento\Codigo web scrapping\credenciales.env"
        load_dotenv(env_path)
        
        chrome_options = Options()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            yield driver
        finally:
            driver.quit()

    def find_interactive_elements(driver):
        """Identifica y clasifica elementos interactivos en la página."""
        selectors = {
            "buttons": ["button", "[role='button']", "[type='button']"],
            "links": ["a[href]"],
            "inputs": ["input", "textarea", "select"],
            "clickable_divs": ["div[onclick]", "div[role='link']"],
            "dropdowns": ["[role='listbox']", "[aria-haspopup='true']"],
        }

        interactive_elements = {}
        for element_type, selector_list in selectors.items():
            elements = []
            for selector in selector_list:
                try:
                    found_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    elements.extend(found_elements)
                except:
                    continue
            interactive_elements[element_type] = elements
        return interactive_elements

    def next_page(driver, main_page, parar=False):
        numero = 0
        frase = main_page + "/p"
        juntos = ""
        sleep(1)
    
        for k in range(2, 10000):
            if verificar_mensaje_no_resultados(driver=driver):
                return
            elif parar != True:
                numero = k
                juntos = frase + str(numero)
                emails = access_all_emails_on_page(driver=driver)
                access_a_single_email(emails=emails)
                driver.get(juntos)

    def access_all_emails_on_page(driver):
        emails = driver.find_elements(By.CSS_SELECTOR, "tr.zA")
        return emails

    def access_a_single_email(emails):
        cargos = 0
        transferencias = 0
        transferencias_a_terceros = 0
        transferencias_de_terceros = 0
        devoluciones = 0
        strings_Cargo_apendiar = []
        parar = False

        def clean_list(lista):
            lista_final = []
            for strings in lista:
                if type(strings) == type("abc m"):
                    if strings == None:
                        continue
                    elif "Te informamos que se ha realizado una compra por " in strings:
                        str_recortada = strings.replace("Te informamos que se ha realizado una compra por ","")
                        str_recortada = str_recortada.replace(" con cargo a Cuenta ",";")
                        str_recortada = str_recortada.replace(" en ", ";")
                        str_recortada = str_recortada.replace(" el ", ";")
                        str_recortada = str_recortada.replace(".", "")
                        str_recortada = str_recortada.replace("Clemente Arturo Sanhueza Carvajal: ", "")
                        str_recortada = str_recortada.replace("$", "-")
                        str_lista = str_recortada.split(";")
                        str_lista[3] = str_lista[3].split(" ")
                        lista_final.append(str_lista) 
                    elif "Te informamos que tu devolución por" in strings:
                        str_recortada = strings.replace("Te informamos que tu devolución por ", "")
                        str_recortada = str_recortada.replace("Clemente Arturo Sanhueza Carvajal: ", "")
                        str_recortada = str_recortada.replace("$", "+")
                        str_recortada = str_recortada.replace(" desde ", ";")
                        str_recortada = str_recortada.replace(", el ", ";")
                        str_recortada = str_recortada.replace(".", "")
                        str_recortada = str_recortada.replace(", a las", "")
                        str_recortada = str_recortada.replace(", está en proceso de validación y será abonada en tu cuenta terminada en ", ";")
                        str_recortada = str_recortada.replace(" dentro de las próximas 48 horas hábiles", "")
                        str_lista = str_recortada.split(";")
                        str_lista[2] = str_lista[2].split(" ")
                        lista_orden_correcto = [str_lista[0], str_lista[3], str_lista[1], str_lista[2]]
                        lista_orden_correcto[3][1] += lista_orden_correcto[3][2]
                        lista_orden_correcto[3].pop()
                        lista_final.append(lista_orden_correcto)
                elif type(strings) == dict:
                    lista_final.append([strings.get("Monto"), "****2094", strings.get("Destinatario"), [strings.get("Fecha"), strings.get("Hora")]])
            return lista_final

        def append_on_txt(lista):
            list_of_lists = clean_list(lista=lista)
            for linea in list_of_lists:
                writting_on_txt(linea[3][0], linea[3][1], linea[0], linea[2], linea[1])

        def day_already_pass(day_of_email):
            lista_año_dia = day_of_email.split(" ")
            day_of_email = datetime.strptime(f"{lista_año_dia[0]} {lista_año_dia[1]}", "%d/%m/%Y %H:%M")
            with open("Transactions", "r") as f:
                linea = f.readline().rstrip().split(";")
                dia_txt = datetime.strptime(f"{linea[0]} {linea[1]}", "%d/%m/%Y %H:%M")
            return day_of_email <= dia_txt

        # Procesamiento de cada email
        for k in range(50, len(emails)):
            email_a_revisar = emails[k]
            
        for i, email in enumerate(emails, 1):
            fecha = False
            if i in range(0, 51):
                continue
                
            texto = ""
            try:
                remitente = email.find_element(By.CSS_SELECTOR, "span[email]").get_attribute("email")
                asunto = email.find_element(By.CSS_SELECTOR, "span.bog").text
                fragmento = email.find_element(By.CSS_SELECTOR, "span.y2").text

                # Procesamiento según tipo de email
                if "Devolución".lower() in asunto.lower():
                    devoluciones += 1
                    texto = money_devolution_case(driver=driver, email_element=email)
                    lista = clean_list([texto])
                    fecha = day_already_pass(f"{lista[0][3][0]} {lista[0][3][1]}")
                    strings_Cargo_apendiar.append(texto)

                elif "Cargo".lower() in asunto.lower():
                    cargos += 1
                    texto = charge_on_bank_account(driver=driver, email_element=email)
                    lista = clean_list([texto])
                    fecha = day_already_pass(f"{lista[0][3][0]} {lista[0][3][1]}")
                    strings_Cargo_apendiar.append(texto)

                elif "Transferencia".lower() in asunto.lower():
                    if "Transferencia a terceros".lower() in asunto.lower():
                        transferencias_a_terceros += 1
                        texto = transfer_founds_for_you(driver=driver, email_element=email)
                        fecha = day_already_pass(texto.get("Fecha") + " " + texto.get("Hora"))
                        strings_Cargo_apendiar.append(texto)
                    
                    elif "Recibiste una transferencia".lower() in asunto.lower() or "itau informa".lower() in asunto.lower() or "Transferencia de fondos".lower() in asunto.lower():
                        transferencias_de_terceros += 1
                        if "Recibiste una transferencia".lower() in asunto.lower():
                            texto = transfer_founds_to_you(driver=driver, email_element=email, bank="BICE")
                        elif "itau informa".lower() in asunto.lower():
                            texto = transfer_founds_to_you(driver=driver, email_element=email, bank="ITAU")
                        elif "Transferencia de fondos".lower() in asunto.lower():
                            texto = transfer_founds_to_you(driver=driver, email_element=email, bank="EDWARDS")
                        
                        fecha = day_already_pass(texto.get("Fecha") + " " + texto.get("Hora"))
                        strings_Cargo_apendiar.append(texto)
                    
                    transferencias += 1

                if texto != "":
                    print("\n", texto, "\n")

            except Exception as e:
                print(f"\nError procesando email #{i}: {str(e)}\n")

            if fecha == True:
                strings_Cargo_apendiar.pop()
                append_on_txt(lista=strings_Cargo_apendiar)
                sort_transaction_txt()
                print(f"Cargos: {cargos}\nTransferencias: {transferencias}\nDevoluciones: {devoluciones}")
                calcular_total()
                parar = True
                return

        append_on_txt(lista=strings_Cargo_apendiar)
        print(f"""Resumen:
              Cargos: {cargos}
              Transferencias: {transferencias}
              Transferencias de terceros: {transferencias_de_terceros}
              Transferencias a terceros: {transferencias_a_terceros}
              Devoluciones: {devoluciones}""")

    def verificar_mensaje_no_resultados(driver):
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'No hay ningún mensaje que coincida')]")
                )
            )
            return True
        except:
            return False

    def charge_on_bank_account(driver, email_element):
        try:
            main_window = driver.current_window_handle
            
            ActionChains(driver) \
                .key_down(Keys.CONTROL) \
                .click(email_element) \
                .key_up(Keys.CONTROL) \
                .perform()
            
            new_window = [w for w in driver.window_handles if w != main_window][0]
            driver.switch_to.window(new_window)
            
            texto_completo = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, 
                    '//*[contains(., "Te informamos que se ha realizado una compra por")]')
                )
            ).text

            lineas = texto_completo.split("\n")
            mensaje_compra = next(linea for linea in lineas if "Te informamos" in linea)
            
            driver.close()
            driver.switch_to.window(main_window)
            
            return mensaje_compra
            
        except Exception as e:
            print(f"Error al procesar email bancario: {str(e)}")
            if 'main_window' in locals():
                driver.switch_to.window(main_window)
            return None

    def transfer_founds_to_you(driver, email_element, bank):
        def Bice_Bank_Case(driver, email_element):
            try:
                main_window = driver.current_window_handle
                
                ActionChains(driver) \
                    .key_down(Keys.CONTROL) \
                    .click(email_element) \
                    .key_up(Keys.CONTROL) \
                    .perform()
                
                new_window = [w for w in driver.window_handles if w != main_window][0]
                driver.switch_to.window(new_window)
                
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, 
                        '//*[contains(., "Recibiste una transferencia") or contains(., "BANCO ⚫ BICE")]'
                    ))
                )
                
                texto_completo = driver.find_element(By.TAG_NAME, 'body').text
                
                info = {
                    "Fecha": None,
                    "Hora": None,
                    "Monto": None,
                    "Destinatario": None,
                    "Cuenta_Origen": "****2094",
                    "Cuenta_Destino": None,
                    "Numero_Operacion": None
                }
                
                fecha_hora_match = re.search(r'(\d{1,2} \w{3} \d{4}) - (\d{2}:\d{2})', texto_completo)
                if fecha_hora_match:
                    info["Fecha"] = fecha_hora_match.group(1)
                    info["Hora"] = fecha_hora_match.group(2)

                info["Fecha"] = texto_a_fecha_numerica_custom_3(info["Fecha"])

                monto_match = re.search(r'\$\s*([\d.,]+)\b', texto_completo)
                if monto_match:
                    monto = monto_match.group(1).replace('.', '').replace(',', '.')
                    try:
                        info["Monto"] = int(monto)
                    except ValueError:
                        info["Monto"] = monto_match.group(1)
                
                remitente_match = re.search(r'Cuenta de origen\s*Nombre\s*(.+)', texto_completo)
                if remitente_match:
                    info["Destinatario"] = remitente_match.group(1).strip()
                
                cuenta_destino_match = re.search(r'Número de cuenta\s*(\d{2}-\d{3}-\d{5}-\d{2}|\d+)\b', texto_completo)
                if cuenta_destino_match:
                    info["Cuenta_Destino"] = cuenta_destino_match.group(1)
                
                operacion_match = re.search(r'Número de operación\s*(\d+)', texto_completo)
                if operacion_match:
                    info["Numero_Operacion"] = operacion_match.group(1)
                
                driver.close()
                driver.switch_to.window(main_window)
                return info
                
            except Exception as e:
                print(f"Error al procesar email del BICE: {str(e)}")
                if 'main_window' in locals():
                    driver.switch_to.window(main_window)
                return None

        def Itau_Bank_Case(driver, email_element):
            try:
                main_window = driver.current_window_handle
                
                ActionChains(driver) \
                    .key_down(Keys.CONTROL) \
                    .click(email_element) \
                    .key_up(Keys.CONTROL) \
                    .perform()
                
                new_window = [w for w in driver.window_handles if w != main_window][0]
                driver.switch_to.window(new_window)
                
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, 
                        '//*[contains(., "ha instruido una transferencia")]'
                    ))
                )
                
                texto_completo = driver.find_element(By.TAG_NAME, 'body').text
                
                info = {
                    "Fecha": None,
                    "Hora": None,
                    "Monto": None,
                    "Destinatario": None,
                    "Cuenta_Destino": None,
                    "Comentario": None
                }
                
                fecha_hora_match = re.search(r'(\d{2}/\d{2}/\d{4})-(\d{2}:\d{2}):\d{2}', texto_completo)
                if fecha_hora_match:
                    info["Fecha"] = fecha_hora_match.group(1)
                    info["Hora"] = fecha_hora_match.group(2)
                
                monto_match = re.search(r'\$\s*([\d.,]+)\b', texto_completo)
                if monto_match:
                    monto = monto_match.group(1).replace('.', '').replace(',', '')
                    info["Monto"] = f"+{monto}"
                
                destinatario_match = re.search(r'Titular Cuenta:\s*(.+)', texto_completo)
                if destinatario_match:
                    info["Destinatario"] = destinatario_match.group(1).strip()
                
                cuenta_match = re.search(r'Numero Cuenta:\s*(\d+)', texto_completo)
                if cuenta_match:
                    info["Cuenta_Destino"] = cuenta_match.group(1)
                
                comentario_match = re.search(r'comentario:\s*(.+?)\s*\*\*Importante:', texto_completo, re.DOTALL | re.IGNORECASE)
                if comentario_match:
                    info["Comentario"] = comentario_match.group(1).strip()
                
                driver.close()
                driver.switch_to.window(main_window)
                
                print(info, "Procesado exitosamente")
                return info
                
            except Exception as e:
                print(f"Error al procesar email de Itaú: {str(e)}")
                if 'main_window' in locals():
                    driver.switch_to.window(main_window)
                return None

        def Santander_Bank_Case(driver, email_element):
            try:
                main_window = driver.current_window_handle
                
                ActionChains(driver) \
                    .key_down(Keys.CONTROL) \
                    .click(email_element) \
                    .key_up(Keys.CONTROL) \
                    .perform()
                
                new_window = [w for w in driver.window_handles if w != main_window][0]
                driver.switch_to.window(new_window)
                
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, 
                        '//*[contains(., "ha realizado una transferencia") or contains(., "transferencia a tu cuenta")]'
                    ))
                )
                
                texto_completo = driver.find_element(By.TAG_NAME, 'body').text
                
                info = {
                    "Fecha": None,
                    "Hora": "00:00",
                    "Monto": None,
                    "Destinatario": None,
                    "Cuenta_Destino": None,
                    "Comentario": None
                }
                
                fecha_match = re.search(r'con fecha (\d{2}/\d{2}/\d{4})', texto_completo)
                if fecha_match:
                    info["Fecha"] = fecha_match.group(1)
                
                monto_match = re.search(r'Monto transferido\s*\|\s*\$\s*([\d.,]+)', texto_completo)
                if monto_match:
                    monto = monto_match.group(1).replace('.', '').replace(',', '')
                    info["Monto"] = f"+{monto}"
                
                destinatario_match = re.search(r'Estimado\(a\) (.+?):', texto_completo)
                if destinatario_match:
                    info["Destinatario"] = destinatario_match.group(1).strip()
                
                cuenta_match = re.search(r'Nº de cuenta\s*\|\s*([\d-]+)', texto_completo)
                if cuenta_match:
                    info["Cuenta_Destino"] = cuenta_match.group(1).replace('-', '')
                
                comentario_match = re.search(r'Comentario\s*(.+?)\s*(?:\n\n|\Z)', texto_completo, re.DOTALL)
                if comentario_match:
                    info["Comentario"] = comentario_match.group(1).strip()
                
                driver.close()
                driver.switch_to.window(main_window)
                
                print(info, "Procesado exitosamente")
                return info
                
            except Exception as e:
                print(f"Error al procesar email de Santander: {str(e)}")
                if 'main_window' in locals():
                    driver.switch_to.window(main_window)
                return None

        def Security_Bank_Case(driver, email_element):
            try:
                main_window = driver.current_window_handle
                
                ActionChains(driver) \
                    .key_down(Keys.CONTROL) \
                    .click(email_element) \
                    .key_up(Keys.CONTROL) \
                    .perform()
                
                new_window = [w for w in driver.window_handles if w != main_window][0]
                driver.switch_to.window(new_window)
                
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, 
                        '//*[contains(., "le ha transferido fondos a su cuenta")]'
                    ))
                )
                
                texto_completo = driver.find_element(By.TAG_NAME, 'body').text
                
                info = {
                    "Fecha": None,
                    "Hora": None,
                    "Monto": None,
                    "Destinatario": None,
                    "Cuenta_Destino": None,
                    "Motivo": None,
                    "Numero_Operacion": None
                }
                
                fecha_hora_match = re.search(r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2})', texto_completo)
                if fecha_hora_match:
                    info["Fecha"] = fecha_hora_match.group(1)
                    info["Hora"] = fecha_hora_match.group(2)
                
                monto_match = re.search(r'Monto:\s*\$\s*([\d.,]+)\b', texto_completo)
                if monto_match:
                    monto = monto_match.group(1).replace('.', '').replace(',', '')
                    info["Monto"] = f"+{monto}"
                
                destinatario_match = re.search(r'Estimado\(a\) (.+)', texto_completo)
                if destinatario_match:
                    info["Destinatario"] = destinatario_match.group(1).strip()
                
                cuenta_match = re.search(r'Cuenta de destino:\s*(\d+)', texto_completo)
                if cuenta_match:
                    info["Cuenta_Destino"] = cuenta_match.group(1)
                
                motivo_match = re.search(r'Motivo:\s*(.+?)\s*(?:\n|Cuenta de destino:)', texto_completo)
                if motivo_match:
                    info["Motivo"] = motivo_match.group(1).strip()
                
                operacion_match = re.search(r'Nº de operación:\s*(\d+)', texto_completo)
                if operacion_match:
                    info["Numero_Operacion"] = operacion_match.group(1)
                
                driver.close()
                driver.switch_to.window(main_window)
                
                print(info, "Procesado exitosamente")
                return info
                
            except Exception as e:
                print(f"Error al procesar email de Security: {str(e)}")
                if 'main_window' in locals():
                    driver.switch_to.window(main_window)
                return None

        def Edwards_Bank_Case(driver, email_element):
            try:
                main_window = driver.current_window_handle
                
                ActionChains(driver) \
                    .key_down(Keys.CONTROL) \
                    .click(email_element) \
                    .key_up(Keys.CONTROL) \
                    .perform()
                
                new_window = [w for w in driver.window_handles if w != main_window][0]
                driver.switch_to.window(new_window)
                
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, 
                        '//*[contains(., "Comprobante de transferencia electrónica")]'
                    ))
                )
                
                texto_completo = driver.find_element(By.TAG_NAME, 'body').text
                
                info = {
                    "Fecha": None,
                    "Hora": None,
                    "Monto": None,
                    "Destinatario": None,
                    "Cuenta_Destino": None,
                    "Banco_Destino": None,
                    "Numero_Comprobante": None
                }
                
                fecha_match = re.search(r'Fecha\s*\|\s*(\d{2}/\d{2}/\d{4})', texto_completo) or \
                            re.search(r'Fecha\s+(\d{2}/\d{2}/\d{4})', texto_completo)
                if fecha_match:
                    info["Fecha"] = fecha_match.group(1)
                
                hora_match = re.search(r'(\d{2}:\d{2})\s*(?:hrs|horas)?\s*$', texto_completo, re.MULTILINE)
                if hora_match:
                    info["Hora"] = hora_match.group(1)
                else:
                    info["Hora"] = "00:00"
                
                monto_match = re.search(r'Monto\s*\|\s*\$\s*([\d.,]+)', texto_completo) or \
                            re.search(r'Monto\s+\$\s*([\d.,]+)', texto_completo)
                if monto_match:
                    monto = monto_match.group(1).replace('.', '').replace(',', '')
                    info["Monto"] = f"+{monto}"
                
                destinatario_match = re.search(r'Estimado\(a\):\s*\*\*(.+?)\*\*', texto_completo) or \
                                    re.search(r'Nombre y Apellido\s+(.+)', texto_completo)
                if destinatario_match:
                    info["Destinatario"] = destinatario_match.group(1).strip()
                
                cuenta_match = re.search(r'Cuenta destino\s+(?:Cuenta Vista|Cuenta Corriente)\s+([\d-]+)', texto_completo) or \
                            re.search(r'00-\d{3}-\d{5}-\d{2}', texto_completo)
                if cuenta_match:
                    info["Cuenta_Destino"] = cuenta_match.group(1).replace('-', '') if cuenta_match.group(1) else cuenta_match.group(0).replace('-', '')
                
                banco_match = re.search(r'Banco\s+(.+)', texto_completo)
                if banco_match:
                    info["Banco_Destino"] = banco_match.group(1).strip()
                
                comprobante_match = re.search(r'Número de comprobante\s+(.+)', texto_completo) or \
                                re.search(r'TEFMBCO\d+', texto_completo)
                if comprobante_match:
                    info["Numero_Comprobante"] = comprobante_match.group(1) if comprobante_match.group(1) else comprobante_match.group(0)
                
                driver.close()
                driver.switch_to.window(main_window)
                
                print(info, "Procesado exitosamente")
                return info
                
            except Exception as e:
                print(f"Error al procesar email de Edwards: {str(e)}")
                if 'main_window' in locals():
                    driver.switch_to.window(main_window)
                return None

        if bank == "BICE":
            return Bice_Bank_Case(driver=driver, email_element=email_element)
        elif bank == "ITAU":
            return Itau_Bank_Case(driver=driver, email_element=email_element)
        elif bank == "SANTANDER":
            return Santander_Bank_Case(driver=driver, email_element=email_element)
        elif bank == "SECURITY":
            return Security_Bank_Case(driver=driver, email_element=email_element)
        elif bank == "EDWARDS":
            return Edwards_Bank_Case(driver=driver, email_element=email_element)

    def transfer_founds_for_you(driver, email_element):
        try:
            main_window = driver.current_window_handle
            
            ActionChains(driver) \
                .key_down(Keys.CONTROL) \
                .click(email_element) \
                .key_up(Keys.CONTROL) \
                .perform()
            
            new_window = [w for w in driver.window_handles if w != main_window][0]
            driver.switch_to.window(new_window)
            
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, 
                    '//*[contains(., "Comprobante de Transferencia a terceros")]'
                ))
            )
            
            texto_completo = driver.find_element(By.TAG_NAME, 'body').text
            
            info = {
                "Fecha": None,
                "Hora": None,
                "Monto": None,
                "Destinatario": None,
                "Cuenta_Origen": None,
                "Cuenta_Destino": None
            }
            
            fecha_hora_match = re.search(r'(\w+ \d+ de \w+ de \d+ \d{2}:\d{2})', texto_completo)
            if fecha_hora_match:
                fecha_hora = fecha_hora_match.group(1)
                info["Fecha"] = fecha_hora.split()[0] + " " + " ".join(fecha_hora.split()[1:4])
                info["Hora"] = fecha_hora.split()[-1]
                info["Fecha"] = texto_a_fecha_numerica_custom(info["Fecha"])
            
            monto_match = re.search(r'\$([\d.]+)', texto_completo)
            if monto_match:
                info["Monto"] = monto_match.group(1)
                info["Monto"] = "-" + info["Monto"].replace(".", "")
            
            lineas = texto_completo.split('\n')
            for i, linea in enumerate(lineas):
                if "Nombre y Apellido" in linea:
                    info["Destinatario"] = lineas[i+1].strip()
                if "Nº de Cuenta" in linea and "Origen" in lineas[i-2]:
                    info["Cuenta_Origen"] = lineas[i+1].strip()
                if "Nº de Cuenta" in linea and "Destino" in lineas[i-3]:
                    info["Cuenta_Destino"] = lineas[i+1].strip()
            
            driver.close()
            driver.switch_to.window(main_window)
            
            return info
            
        except Exception as e:
            print(f"Error al procesar email bancario: {str(e)}")
            if 'main_window' in locals():
                driver.switch_to.window(main_window)
            return None

    def money_devolution_case(driver, email_element):
        try:
            main_window = driver.current_window_handle
            
            ActionChains(driver) \
                .key_down(Keys.CONTROL) \
                .click(email_element) \
                .key_up(Keys.CONTROL) \
                .perform()
            
            new_window = [w for w in driver.window_handles if w != main_window][0]
            driver.switch_to.window(new_window)
            
            texto_completo = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, 
                    '//*[contains(., "Te informamos que tu devolución por")]'
                ))
            ).text

            lineas = texto_completo.split("\n")
            mensaje_devolucion = next(linea for linea in lineas if "Te informamos" in linea)
            
            driver.close()
            driver.switch_to.window(main_window)
            
            return mensaje_devolucion
            
        except Exception as e:
            print(f"Error al procesar email bancario: {str(e)}")
            if 'main_window' in locals():
                driver.switch_to.window(main_window)
            return None

    def texto_a_fecha_numerica_custom(fecha_str):
        fecha_str = fecha_str.strip().lower()
        anio_actual = datetime.now().year

        partes = fecha_str.split()
        if partes[0] in ['lunes', 'martes', 'miércoles', 'miercoles', 'jueves', 'viernes', 'sábado', 'sabado', 'domingo']:
            partes = partes[1:]
            fecha_str = ' '.join(partes)

        try:
            if "de" in fecha_str:
                partes = fecha_str.split(" de ")
                dia = int(partes[0])
                mes = MESES_ES[partes[1].strip()]
                if len(partes) == 3:
                    anio = int(partes[2])
                else:
                    anio = anio_actual
                return f"{dia}/{mes}/{anio}"
        except Exception as e:
            raise ValueError("Formato no reconocido o error de parsing: " + str(e))

        raise ValueError("Formato de fecha no reconocido: " + fecha_str)

    def texto_a_fecha_numerica_custom_2(fecha_str):
        str_final = ""
        lista = fecha_str.split(" ")
        str_final += lista[0] + "/" + str(MESES_ES.get(lista[1])) + "/" + lista[2] + " " + lista[3]
        return str_final

    def texto_a_fecha_numerica_custom_3(fecha_str):
        string = ""
        lista = fecha_str.split(" ")
        string += lista[0] + "/" + str(MESES_ES.get(lista[1])) + "/" + lista[2]
        return string

    # Código principal de scraping_emails()
    with get_driver() as driver:
        try:
            username = os.getenv("mail_user")
            password = os.getenv("mail_password")
            bank = os.getenv("bank_user")

            # Navegación e inicio de sesión
            driver.get("https://accounts.google.com/AccountChooser/signinchooser?service=mail&continue=https://mail.google.com/mail/&flowName=GlifWebSignIn&flowEntry=AccountChooser&ec=asw-gmail-globalnav-signin")
            
            # Login
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "identifierId"))).send_keys(username)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Siguiente')]"))).click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Passwd"))).send_keys(password)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Siguiente')]"))).click()
            
            # Búsqueda de emails del banco
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q"))).send