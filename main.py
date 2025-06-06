from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv, set_key
from time import sleep
from datetime import datetime, date, timedelta
from pathlib import Path
from collections import defaultdict
import os
import re
import sys
import requests
import calendar

# Diccionario para traducir meses en español a números
MESES_ES = {
    'enero': 1, 'ene': 1, 'febrero': 2, 'feb': 2, 'marzo': 3, 'mar': 3, 'abril': 4, 'abr': 4, 
    'mayo': 5, 'may': 5, 'junio': 6, 'jun': 6, 'julio': 7, 'jul': 7, 'agosto': 8, 'ago': 8,
    'septiembre': 9, 'sep': 9, 'octubre': 10, 'oct': 10, 'noviembre': 11, 'nov': 11, 
    'diciembre': 12, 'dic': 12
}

def saldo_inicial(Day, Hour, amount, place, card_number):
    archivo = open("Transactions", "w")
    archivo.close()
    
    with open("Transactions", "r") as f:
        lineas = f.readlines()
        for k in range(len(lineas)):
            lineas[k] = lineas[k].rstrip().split(";")
    if [f"{Day}",f"{Hour}",f"{amount}",f"{place}",f"{card_number}"] in lineas:
        pass
    else:
        writting_on_txt(Day, Hour, amount, place, card_number)
        sort_transaction_txt()

# We need to do a efficient code so if we already search an email we don't need to search again
# for each email we extract the next information
# Day, Hour, amount, income or outcome with a sign in amount and place.
# To separate we will use ;
def writting_on_txt(Day, Hour, amount, place, card_number):
    with open("Transactions", "a") as f:
       print(f"{Day};{Hour};{amount};{place};{card_number}", file=f)



# In order to do an efficient Code, we need to sort the Transactions txt for hour and Day
# This function will be use at the end of next_page function when all new transactions are already upload
def sort_transaction_txt():
    with open("Transactions", "r") as f:
        # We put the txt as a arrange of list
        lineas = f.readlines()
        for k in range(len(lineas)):
            lineas[k] = lineas[k].rstrip().split(";")
        
        for k in range(len(lineas)):
            lineas[k][1] = datetime.strptime(lineas[k][1], "%H:%M")
            lineas[k][0] = datetime.strptime(lineas[k][0], "%d/%m/%Y")
        
        lineas_por_hora = sorted(lineas, key=lambda x: x[1], reverse=True)
        lineas_por_dia = sorted(lineas_por_hora, key=lambda x: x[0], reverse=True)

        for k in range(len(lineas_por_dia)):
            lineas_por_dia[k][0] = datetime.strftime(lineas_por_dia[k][0], "%d/%m/%Y")
            lineas_por_dia[k][1] = datetime.strftime(lineas_por_dia[k][1], "%H:%M")
        
        with open("transactions", "w") as f:
            for k in range(len(lineas_por_dia)):
                print(f"{lineas_por_dia[k][0]};{lineas_por_dia[k][1]};{lineas_por_dia[k][2]};{lineas_por_dia[k][3]};{lineas_por_dia[k][4]}", file=f)

# Return the balance of Transaction.txt
def calcular_total():
    with open("Transactions", "r") as f:
        total = 0
        lineas = f.readlines()
        for k in range(len(lineas)):
            lineas[k] = lineas[k].rstrip().split(";")
            try:
                total += int(lineas[k][2])
            except:
                continue
        return total

def mandar_total(monto):
    """chrome_options = Options()
    chrome_options.add_experimental_option(name="excludeSwitches", value=["enable-logging", "enable-automation"])
    chrome_options.add_experimental_option(name="useAutomationExtension", value=False)
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())

    driver2 = webdriver.Chrome(service=service, options=chrome_options)
    # (Opcional) ruta a tu ChromeDriver
    service = Service('/usr/local/bin/chromedriver')  # Cambia si es necesario

    # Configura opciones para evitar advertencias o errores
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-features=BlockExternalProtocolInWee,NetworkService,NetworkServiceInProcess')
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-sync')
    options.add_argument('--no-first-run')
    options.add_argument('--no-default-browser-check')
    
    driver2 = webdriver.Chrome(service=service, options=options)
    # Here we get the main page of mail from google
    driver2.get("http://192.168.4.1")
    sleep(3)

    # Encontrar el campo de texto (puedes ajustar el selector si cambia)
    input_box = WebDriverWait(driver2, 10).until(
        EC.presence_of_element_located((By.NAME, "message"))
    )
    string = "Saldo: $" + str(monto)
    input_box.send_keys(string)

    # Enviar el formulario (puede ser presionando Enter o clic en el botón)
    input_box.send_keys(Keys.ENTER)
    # Esperar un poco para ver el resultado
    sleep(5)
    driver2.quit()"""

    string = "Saldo: $" + str(monto)
    try:
        response = requests.get("http://192.168.4.1", params={"message": string}, timeout=5)
        if response.ok:
            print("Mensaje enviado correctamente.")
        else:
            print("Error al enviar:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error de conexión al ESP:", e)

def calcular_gasto_diario(saldo):
    hoy = date.today()
    dias_totales = calendar.monthrange(hoy.year, hoy.month)[1]
    dias_restantes = dias_totales - hoy.day + 1  # incluye hoy

    if dias_restantes <= 0:
        return 0  # Evita división por cero

    gasto_diario = saldo / dias_restantes
    return round(gasto_diario)

def calcular_porcentaje_restante(saldo_actual, saldo_inicial):
    if saldo_inicial == 0:
        return 0  # Evita división por cero
    
    porcentaje = round((saldo_actual / saldo_inicial) * 100)
    string = f"Porcentaje restante: {porcentaje}%"
    return string

def scraping_emails(args):
    
    #env_path = r"C:\Users\csanh\OneDrive\Escritorio\PDF PUC\Semestre 5\Innovación, desarollo y emprendimiento\Codigo web scrapping\credenciales.env"
    env_path = os.path.join(os.path.dirname(__file__), "credenciales.env")
    parar = False
    
    if len(args) >= 5:

        correo = args[1]
        password = args[2]
        monto_inicial = "+" + sys.argv[3]
        banco = ' '.join(args[4:])  # Une todo lo que venga después como nombre del banco

        set_key(str(env_path), "mail_user", correo)
        set_key(str(env_path), "mail_password", password)
        set_key(str(env_path), "bank_user", banco)
        print("✅ Datos guardados en .env")
    
    else:
        
        load_dotenv(env_path)
        correo = os.getenv("mail_user")
        password = os.getenv("mail_password")
        monto_inicial = "+" + os.getenv("monto_inicial")
        banco = os.getenv("bank_user")
             
    saldo_inicial("1/05/2025", "00:00", monto_inicial, "Cantidad inicial", "****2094")
    chrome_options = Options()
    chrome_options.add_experimental_option(name="excludeSwitches", value=["enable-logging", "enable-automation"])
    chrome_options.add_experimental_option(name="useAutomationExtension", value=False)
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Here we get the main page of mail from google
    driver.get("https://accounts.google.com/AccountChooser/signinchooser?service=mail&continue=https://mail.google.com/mail/&flowName=GlifWebSignIn&flowEntry=AccountChooser&ec=asw-gmail-globalnav-signin")
    # We need to search the credential fields
    driver.implicitly_wait(10)
    # Name field and send buton
    try:
        name_field = driver.find_element(By.ID, "identifierId")
        print("💌 Ingresando el correo...")
        name_field.send_keys(correo)
        print(f"✅ Correo ingresado: {correo}")
    except Exception as e:
        driver.close()

    try:
        next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Siguiente') or contains(., 'Next')]"))
        )
        next_button.click()
    except Exception as e:
        print("Error en boton mandar", e)
        driver.close()

    try:
        password_field = driver.find_element(By.NAME, "Passwd")
        print("🔐 Ingresando la contraseña...")
        password_field.send_keys(password)
        print(f"✅ Contraseña ingresada")
    except Exception as e:
        print("Problemas en el Campo de Contraseña")
        driver.close()

    try:
        next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Siguiente') or contains(., 'Next')]"))
        )
        next_button.click()
    except Exception as e:
        print("Error en boton mandar", e)
        driver.close()

    # Now we need to search the keyword Banco, in my case Banco de Chile is the unique account that i Use
    # First use the search bar to search from keyword
    try:
        search_bar = driver.find_element(By.NAME, "q")
        #Search_query abril:
        #search_query = f"from:{bank} after:2025/03/31 before:2025/05/01"
        # Obtener la fecha actual
        hoy = date.today()
        año = hoy.year
        mes = hoy.month
        # Calcular primer y último día del mes
        primer_dia = date(año, mes, 1)
        # Generar la query
        search_query = f"from:{banco} after:{primer_dia.strftime('%Y/%m/%d')}"
        print("🔎 Ingresando query de búsqueda:", search_query)

        search_bar.send_keys(search_query)
        search_bar.send_keys(Keys.RETURN)
        print(f"✅ Query ingresada")

    except Exception as e:
        print("Error en la barra de busqueda", e)
        driver.close()

    #print("Se supone que estamos ya filtrado por Banco de Chile")
    #print("Filtrado por banco")
    # We need to iterate from each email in search of information
    # first of all access the email
    # This function change the page if dosent see the keyword No resultados
    # Internal use of function verificar_mensaje_no_resultados.
    # Dosent return anything
    def next_page(driver, main_page, parar=False):
        # We can pass the page if we change the value of p
        # When we arrive to the last page a menssage arrive
        numero = 0
        frase = main_page + "/p"
        juntos = ""
        #sleep(1)
    
        for k in range(2, 10000):
            if verificar_mensaje_no_resultados(driver=driver):
                return None

            elif not parar:
                numero = k
                juntos = frase + str(numero)
                emails = access_all_emails_on_page(driver=driver)
                access_a_single_email(emails=emails)
                driver.get(juntos)
                #print("Proxima página", juntos, "\n")

    # The function create the dictionary of emails.
    # Return the dicctionary of emails.
    def access_all_emails_on_page(driver):
        emails = driver.find_elements(By.CSS_SELECTOR, "tr.zA")
        #return emails
        # Obtener tanto emails individuales como conversaciones
        all_elements = driver.find_elements(By.CSS_SELECTOR, "tr.zA, div[role='listitem']")
        
        expanded_emails = []
        for element in all_elements:
            try:
                # Intentar detectar si es un contenedor de conversación
                if "Hilo" in element.get_attribute("aria-label") or "Conversation" in element.get_attribute("aria-label"):
                    # Expandir si está colapsado
                    try:
                        expand_btn = element.find_element(By.CSS_SELECTOR, "div[aria-expanded='false']")
                        expand_btn.click()
                        sleep(1)
                        
                        # Obtener emails dentro de la conversación
                        thread_emails = element.find_elements(By.XPATH, ".//tr[contains(@class, 'zA')]")
                        expanded_emails.extend(thread_emails)
                    except NoSuchElementException:
                        # Si no tiene botón de expandir, es un email normal
                        expanded_emails.append(element)
                else:
                    expanded_emails.append(element)
            except Exception:
                expanded_emails.append(element)
                
        return expanded_emails

    # First of all the function print the class of each the element
    # Next proceed to print  the email number in the dicctionary, from and asunto of each email
    # Dosent return anything only print the values.
    def access_a_single_email(emails):
        cargos = 0
        transferencias = 0
        transferencias_a_terceros = 0
        transferencias_de_terceros = 0
        devoluciones = 0
        
        # Depending on the data type the function return a list that will append later
        def clean_list(lista):
            #print("Entrando a Clean_list")
            lista_final = []
            for strings in lista:
                #print("TIPO DE DATO: ", type(strings))
                if type(strings) == type("abc m"):
                    #print("STRING A PROCESAR: ", strings)
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
                        print(lista_orden_correcto)
                        lista_final.append(lista_orden_correcto)
                elif type(strings) == dict:
                    lista_final.append([strings.get("Monto"),  "****2094", strings.get("Destinatario") ,[strings.get("Fecha"),strings.get("Hora")]])
            return lista_final

        # Append the text from the list as argument to the txt
        def append_on_txt(lista):
            list_of_lists = clean_list(lista=lista)
            
            for linea in list_of_lists:
                writting_on_txt(linea[3][0], linea[3][1], linea[0], linea[2], linea[1])

        # This function return False if the Day of last transaction in Transactions is more recent that email day
        # In case that the actual mail day is less resent that first transaction return True
        def day_already_pass(day_of_email):
            lista_año_dia = day_of_email.split(" ")
            day_of_email =  datetime.strptime(f"{lista_año_dia[0]} {lista_año_dia[1]}", "%d/%m/%Y %H:%M")
            with open("Transactions", "r") as f:
                linea = f.readline().rstrip().split(";")
                dia_txt = datetime.strptime(f"{linea[0]} {linea[1]}", "%d/%m/%Y %H:%M")
            if day_of_email <= dia_txt:
                return True
            else:
                return False

        # The function extract the valuable information in Charge on bank acount emails.
        def charge_on_bank_account(driver, email_element):

            try:
                # 1. Scroll y hover para asegurar visibilidad
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", email_element)
                ActionChains(driver).move_to_element(email_element).pause(0.5).perform()
                
                # 2. Expandir el email en la misma vista
                email_element.click()
                #sleep(1)  # Espera para la animación
                
                expanded_email = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH,
                '//div[@role="listitem" and @aria-expanded="true"]'
                )))

                # 3. Extraer contenido del email expandido
                texto_completo = WebDriverWait(expanded_email, 10).until(
                    EC.visibility_of_element_located((By.XPATH,
                        '//div[@role="listitem" and @aria-expanded="true"]'
                        '//div[contains(., "Te informamos que se ha realizado una compra por")]'
                    ))
                ).text
                
                # 4. Filtrar solo la línea relevante
                lineas = [linea.strip() for linea in texto_completo.split('\n') if linea.strip()]
                mensaje_compra = next((linea for linea in lineas if "Te informamos" in linea), None)
                return mensaje_compra or texto_completo[:200] + "..."  # Fallback con fragmento
                
            except TimeoutException:
                print("Tiempo de espera agotado al expandir el email")

            except NoSuchElementException:
                print("No se encontró el mensaje de transacción")
            except Exception as e:
                print(f"Error inesperado: {str(e)}")
            
            finally:
                # 5. Colapsar el email (solo si sigue expandido)
                driver.back()
                #sleep(1)
            return None

        # The function extract the value information of transfer of money emails.
        # The case that this function cover is when you recibe money
        def transfer_founds_to_you(driver, email_element, bank):
            
            def Bice_Bank_Case(driver, email_element):       
                
                try:
                    # 1. Scroll y hover para asegurar visibilidad
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", email_element)
                    ActionChains(driver).move_to_element(email_element).pause(0.5).perform()
                    
                    # 2. Expandir el email en la misma vista
                    email_element.click()
                    #sleep(1)  # Espera para la animación
                    
                    expanded_email = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH,
                    '//div[@role="listitem" and @aria-expanded="true"]'
                    )))

                    # 3. Extraer contenido del email expandido
                    texto_completo = WebDriverWait(expanded_email, 10).until(
                        EC.visibility_of_element_located((By.XPATH,
                            '//div[@role="listitem" and @aria-expanded="true"]//div[contains(., "Recibiste una transferencia") or contains(., "BANCO ⚫ BICE")]'
                        ))
                    ).text
                    
                    # Procesar la información
                    info = {
                        "Fecha": None,
                        "Hora": None,
                        "Monto": None,
                        "Destinatario": None,  # Cambiado de Destinatario a Remitente (quien envía el dinero)
                        "Cuenta_Origen": "****2094",
                        "Cuenta_Destino": None,
                        "Numero_Operacion": None
                    }
                    
                    # Extraer fecha y hora - formato "13 abr 2025 - 10:45 h"
                    fecha_hora_match = re.search(r'(\d{1,2} \w{3} \d{4}) - (\d{2}:\d{2})', texto_completo)
                    if not fecha_hora_match:
                        # Intentar otro formato posible
                        fecha_hora_match = re.search(r'(\w{3}), (\d{1,2} \w{3}), (\d{2}:\d{2})', texto_completo)
                        if fecha_hora_match:
                            info["Fecha"] = f"{fecha_hora_match.group(2)} {datetime.datetime.now().year}"
                            info["Hora"] = fecha_hora_match.group(3)
                    else:
                        info["Fecha"] = fecha_hora_match.group(1)
                        info["Hora"] = fecha_hora_match.group(2)

                    #print("Despues de facha y hora", info)
                    info["Fecha"] = texto_a_fecha_numerica_custom_3(info["Fecha"])


                    # Extraer monto
                    monto_match = re.search(r'\$\s*([\d.,]+)\b', texto_completo)
                    if monto_match:
                        monto = monto_match.group(1).replace('.', '').replace(',', '.')
                        try:
                            info["Monto"] = int(monto)
                        except ValueError:
                            info["Monto"] = monto_match.group(1)
                    #print("Despues de monto", monto_match)
                    
                    # Extraer remitente (nombre de quien envía el dinero)
                    remitente_match = re.search(r'Cuenta de origen\s*Nombre\s*(.+)', texto_completo)
                    if remitente_match:
                        info["Destinatario"] = remitente_match.group(1).strip()
                    #print("Remitente", info)
                    
                    # Extraer número de cuenta destino
                    cuenta_destino_match = re.search(r'Número de cuenta\s*(\d{2}-\d{3}-\d{5}-\d{2}|\d+)\b', texto_completo)
                    if cuenta_destino_match:
                        info["Cuenta_Destino"] = cuenta_destino_match.group(1)
                    #print("Cuenta de destino", info)
                    
                    # Extraer número de operación
                    operacion_match = re.search(r'Número de operación\s*(\d+)', texto_completo)
                    if operacion_match:
                        info["Numero_Operacion"] = operacion_match.group(1)
                    #print("N operacion", info, "\n")
                    
                    # Cerrar la pestaña del email
                    #driver.close()
                    #driver.switch_to.window(main_window)
                    #print(info, "Mandada exitosamente")
                    return info
                    
                except TimeoutException:
                    print("Tiempo de espera agotado al expandir el email")

                except NoSuchElementException:
                    print("No se encontró el mensaje de transacción")
                except Exception as e:
                    print(f"Error inesperado: {str(e)}")
                
                finally:
                    # 5. Colapsar el email (solo si sigue expandido)
                    driver.back()
                    #sleep(1)
                return None

            
            def Itau_Bank_Case(driver, email_element):
                print("EMAIL DEL ITAU DE TRANSFERENCIA")

                try:
                    # Guardar la ventana principal
                    main_window = driver.current_window_handle
                    
                    # Abrir el email en nueva pestaña
                    ActionChains(driver) \
                        .key_down(Keys.CONTROL) \
                        .click(email_element) \
                        .key_up(Keys.CONTROL) \
                        .perform()
                    
                    # Cambiar a la nueva pestaña
                    new_window = [w for w in driver.window_handles if w != main_window][0]
                    driver.switch_to.window(new_window)
                    
                    # Esperar a que el contenido esté presente
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, 
                            '//*[contains(., "ha instruido una transferencia")]'
                        ))
                    )
                    
                    # Extraer toda la información relevante
                    texto_completo = driver.find_element(By.TAG_NAME, 'body').text
                    
                    # Procesar la información
                    info = {
                        "Fecha": None,
                        "Hora": None,
                        "Monto": None,
                        "Destinatario": None,
                        "Cuenta_Destino": None,
                        "Comentario": None
                    }
                    
                    # Extraer fecha y hora - formato 23/04/2025-21:16:51
                    fecha_hora_match = re.search(r'(\d{2}/\d{2}/\d{4})-(\d{2}:\d{2}):\d{2}', texto_completo)
                    if fecha_hora_match:
                        info["Fecha"] = fecha_hora_match.group(1)  # Formato dd/mm/yyyy
                        info["Hora"] = fecha_hora_match.group(2)   # Formato HH:mm
                    
                    # Extraer monto con + y sin puntos
                    monto_match = re.search(r'\$\s*([\d.,]+)\b', texto_completo)
                    if monto_match:
                        monto = monto_match.group(1).replace('.', '').replace(',', '')
                        info["Monto"] = f"+{monto}"  # Formato con +
                    
                    # Extraer destinatario (titular de la cuenta)
                    destinatario_match = re.search(r'Titular Cuenta:\s*(.+)', texto_completo)
                    if destinatario_match:
                        info["Destinatario"] = destinatario_match.group(1).strip()
                    
                    # Extraer número de cuenta destino
                    cuenta_match = re.search(r'Numero Cuenta:\s*(\d+)', texto_completo)
                    if cuenta_match:
                        info["Cuenta_Destino"] = cuenta_match.group(1)
                    
                    # Extraer comentario si existe
                    comentario_match = re.search(r'comentario:\s*(.+?)\s*\*\*Importante:', texto_completo, re.DOTALL | re.IGNORECASE)
                    if comentario_match:
                        info["Comentario"] = comentario_match.group(1).strip()
                    
                    # Cerrar la pestaña del email
                    driver.close()
                    driver.switch_to.window(main_window)
                    
                    print(info, "Procesado exitosamente")  # Debug
                    return info
                    
                except Exception as e:
                    print(f"Error al procesar email de Itaú: {str(e)}")
                    if 'main_window' in locals():
                        driver.switch_to.window(main_window)
                    return None

            def Santander_Bank_Case(driver, email_element):

                try:
                    # Guardar ventana principal
                    main_window = driver.current_window_handle
                    
                    # Abrir email en nueva pestaña
                    ActionChains(driver) \
                        .key_down(Keys.CONTROL) \
                        .click(email_element) \
                        .key_up(Keys.CONTROL) \
                        .perform()
                    
                    # Cambiar a nueva pestaña
                    new_window = [w for w in driver.window_handles if w != main_window][0]
                    driver.switch_to.window(new_window)
                    
                    # Esperar contenido
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, 
                            '//*[contains(., "ha realizado una transferencia") or contains(., "transferencia a tu cuenta")]'
                        ))
                    )
                    
                    texto_completo = driver.find_element(By.TAG_NAME, 'body').text
                    
                    info = {
                        "Fecha": None,
                        "Hora": "00:00",  # Valor por defecto
                        "Monto": None,
                        "Destinatario": None,
                        "Cuenta_Destino": None,
                        "Comentario": None
                    }
                    
                    # Extraer fecha (formato: 01/04/2025)
                    fecha_match = re.search(r'con fecha (\d{2}/\d{2}/\d{4})', texto_completo)
                    if fecha_match:
                        info["Fecha"] = fecha_match.group(1)
                    
                    # Extraer monto (ej: $ 8.250 → +8250)
                    monto_match = re.search(r'Monto transferido\s*\|\s*\$\s*([\d.,]+)', texto_completo)
                    if monto_match:
                        monto = monto_match.group(1).replace('.', '').replace(',', '')
                        info["Monto"] = f"+{monto}"
                    
                    # Extraer destinatario
                    destinatario_match = re.search(r'Estimado\(a\) (.+?):', texto_completo)
                    if destinatario_match:
                        info["Destinatario"] = destinatario_match.group(1).strip()
                    
                    # Extraer cuenta destino (formato: 0-000-31-82209-4 → 000031822094)
                    cuenta_match = re.search(r'Nº de cuenta\s*\|\s*([\d-]+)', texto_completo)
                    if cuenta_match:
                        info["Cuenta_Destino"] = cuenta_match.group(1).replace('-', '')
                    
                    # Extraer comentario si existe
                    comentario_match = re.search(r'Comentario\s*(.+?)\s*(?:\n\n|\Z)', texto_completo, re.DOTALL)
                    if comentario_match:
                        info["Comentario"] = comentario_match.group(1).strip()
                    
                    # Cerrar pestaña y volver
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

                    # 1. Scroll y hover para asegurar visibilidad
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", email_element)
                    ActionChains(driver).move_to_element(email_element).pause(0.5).perform()
                    
                    # 2. Expandir el email en la misma vista
                    email_element.click()
                    sleep(1)  # Espera para la animación
                    
                    expanded_email = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH,
                    '//div[@role="listitem" and @aria-expanded="true"]'
                    )))

                    # 3. Extraer contenido del email expandido
                    texto_completo = WebDriverWait(expanded_email, 10).until(
                        EC.visibility_of_element_located((By.XPATH,
                            '//div[@role="listitem" and @aria-expanded="true"]//div[contains(., "le ha transferido fondos a su cuenta)]'
                        ))
                    ).text
                    
                    # Procesar la información
                    info = {
                        "Fecha": None,
                        "Hora": None,
                        "Monto": None,
                        "Destinatario": None,
                        "Cuenta_Destino": None,
                        "Motivo": None,
                        "Numero_Operacion": None
                    }
                    
                    # Extraer fecha y hora - formato 01/04/2025 11:11 hrs.
                    fecha_hora_match = re.search(r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2})', texto_completo)
                    if fecha_hora_match:
                        info["Fecha"] = fecha_hora_match.group(1)  # Formato dd/mm/yyyy
                        info["Hora"] = fecha_hora_match.group(2)   # Formato HH:mm
                    
                    # Extraer monto con + y sin puntos/miles
                    monto_match = re.search(r'Monto:\s*\$\s*([\d.,]+)\b', texto_completo)
                    if monto_match:
                        monto = monto_match.group(1).replace('.', '').replace(',', '')
                        info["Monto"] = f"+{monto}"  # Formato con +
                    
                    # Extraer destinatario (del encabezado)
                    destinatario_match = re.search(r'Estimado\(a\) (.+)', texto_completo)
                    if destinatario_match:
                        info["Destinatario"] = destinatario_match.group(1).strip()
                    
                    # Extraer número de cuenta destino
                    cuenta_match = re.search(r'Cuenta de destino:\s*(\d+)', texto_completo)
                    if cuenta_match:
                        info["Cuenta_Destino"] = cuenta_match.group(1)
                    
                    # Extraer motivo
                    motivo_match = re.search(r'Motivo:\s*(.+?)\s*(?:\n|Cuenta de destino:)', texto_completo)
                    if motivo_match:
                        info["Motivo"] = motivo_match.group(1).strip()
                    
                    # Extraer número de operación
                    operacion_match = re.search(r'Nº de operación:\s*(\d+)', texto_completo)
                    if operacion_match:
                        info["Numero_Operacion"] = operacion_match.group(1)
                
                except TimeoutException:
                    print("Tiempo de espera agotado al expandir el email")

                except NoSuchElementException:
                    print("No se encontró el mensaje de transacción")
                except Exception as e:
                    print(f"Error inesperado: {str(e)}")
                
                finally:
                    # 5. Colapsar el email (solo si sigue expandido)
                    driver.back()
                    sleep(1)
                return None

            def Edwards_Bank_Case(driver, email_element):

                try:
                    # Guardar ventana principal
                    main_window = driver.current_window_handle
                    
                    # Abrir email en nueva pestaña
                    ActionChains(driver) \
                        .key_down(Keys.CONTROL) \
                        .click(email_element) \
                        .key_up(Keys.CONTROL) \
                        .perform()
                    
                    # Cambiar a nueva pestaña
                    new_window = [w for w in driver.window_handles if w != main_window][0]
                    driver.switch_to.window(new_window)
                    
                    # Esperar contenido
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
                    
                    # Extraer fecha (formato: 01/04/2025)
                    fecha_match = re.search(r'Fecha\s*\|\s*(\d{2}/\d{2}/\d{4})', texto_completo) or \
                                re.search(r'Fecha\s+(\d{2}/\d{2}/\d{4})', texto_completo)
                    if fecha_match:
                        info["Fecha"] = fecha_match.group(1)
                    
                    # Extraer hora (formato: 06:52)
                    hora_match = re.search(r'(\d{2}:\d{2})\s*(?:hrs|horas)?\s*$', texto_completo, re.MULTILINE)
                    if hora_match:
                        info["Hora"] = hora_match.group(1)
                    else:
                        info["Hora"] = "00:00"  # Por defecto si no se encuentra
                    
                    # Extraer monto (ej: $8.250 → +8250)
                    monto_match = re.search(r'Monto\s*\|\s*\$\s*([\d.,]+)', texto_completo) or \
                                re.search(r'Monto\s+\$\s*([\d.,]+)', texto_completo)
                    if monto_match:
                        monto = monto_match.group(1).replace('.', '').replace(',', '')
                        info["Monto"] = f"+{monto}"
                    
                    # Extraer destinatario
                    destinatario_match = re.search(r'Estimado\(a\):\s*\*\*(.+?)\*\*', texto_completo) or \
                                        re.search(r'Nombre y Apellido\s+(.+)', texto_completo)
                    if destinatario_match:
                        info["Destinatario"] = destinatario_match.group(1).strip()
                    
                    # Extraer cuenta destino (normalizada sin guiones)
                    cuenta_match = re.search(r'Cuenta destino\s+(?:Cuenta Vista|Cuenta Corriente)\s+([\d-]+)', texto_completo) or \
                                re.search(r'00-\d{3}-\d{5}-\d{2}', texto_completo)
                    if cuenta_match:
                        info["Cuenta_Destino"] = cuenta_match.group(1).replace('-', '') if cuenta_match.group(1) else cuenta_match.group(0).replace('-', '')
                    
                    # Extraer banco destino
                    banco_match = re.search(r'Banco\s+(.+)', texto_completo)
                    if banco_match:
                        info["Banco_Destino"] = banco_match.group(1).strip()
                    
                    # Extraer número de comprobante
                    comprobante_match = re.search(r'Número de comprobante\s+(.+)', texto_completo) or \
                                    re.search(r'TEFMBCO\d+', texto_completo)
                    if comprobante_match:
                        info["Numero_Comprobante"] = comprobante_match.group(1) if comprobante_match.group(1) else comprobante_match.group(0)
                    
                    # Cerrar pestaña y volver
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
            
            print("✅ Transferencia  registrada")

        # The function extract the value information of transfer of money emails.
        # The case that this function cover is when you give money
        def transfer_founds_for_you(driver, email_element):
            print("Extrayendo informacion de una transferencia hecha por mi:")
            """
            Extrae información estructurada de un email de transferencia bancaria a terceros.
            Returns:
                Diccionario con la información estructurada de la transferencia
            """
            try:
                # Guardar la ventana principal
                main_window = driver.current_window_handle
                
                # Abrir el email en nueva pestaña (más estable)
                ActionChains(driver) \
                    .key_down(Keys.CONTROL) \
                    .click(email_element) \
                    .key_up(Keys.CONTROL) \
                    .perform()
                
                # Cambiar a la nueva pestaña
                new_window = [w for w in driver.window_handles if w != main_window][0]
                driver.switch_to.window(new_window)
                
                # Esperar a que el contenido esté presente
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, 
                        '//*[contains(., "Comprobante de Transferencia a terceros")]'
                    ))
                )
                
                # Extraer toda la información relevante
                texto_completo = driver.find_element(By.TAG_NAME, 'body').text
                
                # Procesar la información
                info = {
                    "Fecha": None,
                    "Hora": None,
                    "Monto": None,
                    "Destinatario": None,
                    "Cuenta_Origen": None,
                    "Cuenta_Destino": None
                }
                
                # Extraer fecha y hora
                fecha_hora_match = re.search(r'(\w+ \d+ de \w+ de \d+ \d{2}:\d{2})', texto_completo)
                if fecha_hora_match:
                    fecha_hora = fecha_hora_match.group(1)
                    info["Fecha"] = fecha_hora.split()[0] + " " + " ".join(fecha_hora.split()[1:4])
                    info["Hora"] = fecha_hora.split()[-1]
                    info["Fecha"] = texto_a_fecha_numerica_custom(info["Fecha"])
                    #print(info["Fecha"])
                
                # Extraer monto
                monto_match = re.search(r'\$([\d.]+)', texto_completo)
                if monto_match:
                    info["Monto"] = monto_match.group(1)
                    info["Monto"] = "-" + info["Monto"].replace(".", "")
                
                # Formato de fecha no reconocido
                # Extraer información de origen y destino
                lineas = texto_completo.split('\n')
                for i, linea in enumerate(lineas):
                    if "Nombre y Apellido" in linea:
                        info["Destinatario"] = lineas[i+1].strip()
                    if "Nº de Cuenta" in linea and "Origen" in lineas[i-2]:
                        info["Cuenta_Origen"] = lineas[i+1].strip()
                    if "Nº de Cuenta" in linea and "Destino" in lineas[i-3]:
                        info["Cuenta_Destino"] = lineas[i+1].strip()
                
                # Cerrar la pestaña del email
                driver.close()
                driver.switch_to.window(main_window)
                
                return info
                
            except Exception as e:
                #print(f"Error al procesar email bancario: {str(e)}")
                # Asegurarse de volver a la ventana principal
                if 'main_window' in locals():
                    driver.switch_to.window(main_window)
                return None

        # The function extract the value information of money devolution
        def money_devolution_case(driver, email_element):

            try:
                # 1. Scroll y hover para asegurar visibilidad
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", email_element)
                ActionChains(driver).move_to_element(email_element).pause(0.5).perform()
                
                # 2. Expandir el email en la misma vista
                email_element.click()
                #sleep(1)  # Espera para la animación
                
                expanded_email = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH,
                '//div[@role="listitem" and @aria-expanded="true"]'
                )))

                # 3. Extraer contenido del email expandido
                texto_completo = WebDriverWait(expanded_email, 10).until(
                    EC.visibility_of_element_located((By.XPATH,
                        '//div[@role="listitem" and @aria-expanded="true"]'
                        '//div[contains(., "Te informamos que tu devolución por")]'
                    ))
                ).text
                
                # 4. Filtrar solo la línea relevante
                lineas = [linea.strip() for linea in texto_completo.split('\n') if linea.strip()]
                mensaje_compra = next((linea for linea in lineas if "Te informamos" in linea), None)
                
                return mensaje_compra or texto_completo[:200] + "..."  # Fallback con fragmento
                
            except TimeoutException:
                print("Tiempo de espera agotado al expandir el email")

            except NoSuchElementException:
                print("No se encontró el mensaje de transacción")
            except Exception as e:
                print(f"Error inesperado: {str(e)}")
            
            finally:
                # 5. Colapsar el email (solo si sigue expandido)
                driver.back()
                #sleep(1)
            return None

        def texto_a_fecha_numerica_custom(fecha_str):
            """
            Convierte fechas tipo 'viernes 04 de abril' a '4/4/2025'.
            Si no se incluye el año, se asume el año actual.
            """
            fecha_str = fecha_str.strip().lower()
            anio_actual = datetime.now().year

            # Eliminar nombre del día si existe
            partes = fecha_str.split()
            if partes[0] in ['lunes', 'martes', 'miércoles', 'miercoles', 'jueves', 'viernes', 'sábado', 'sabado', 'domingo']:
                partes = partes[1:]  # quitar el día
                fecha_str = ' '.join(partes)

            # Extraer día, mes y opcionalmente año
            try:
                # Caso con año (ej: 04 de abril de 2023)
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

        def texto_a_fecha_numerica_custom_3(fecha_str):
            string = ""
            lista = fecha_str.split(" ")
            #print(lista, fecha_str)
            string += lista[0] + "/" + str(MESES_ES.get(lista[1])) + "/" + lista[2]
            return string

        strings_Cargo_apendiar = []
        threads = defaultdict(list)
        for i, email in enumerate(emails, 1):
            fecha = False
            thread_id = email.get_attribute("data-thread-id") or "solo"
            threads[thread_id].append(email)

            if i in range(0, 51):
                continue
            
            else:
                texto = ""
                
                try:
                    remitente = email.find_element(By.CSS_SELECTOR, "span[email]").get_attribute("email")
                    asunto = email.find_element(By.CSS_SELECTOR, "span.bog").text
                    #fragmento = email.find_element(By.CSS_SELECTOR, "span.y2").text

                    print(f"✅ Leyendo mail: De: {remitente} | Asunto: {asunto}")
                    # Hacer caso de devolución
                    if "Devolución".lower() in asunto.lower():
                        devoluciones += 1
                        texto = money_devolution_case(driver=driver, email_element=email)
                        lista = clean_list([texto])
                        fecha = day_already_pass(f"{lista[0][3][0]} {lista[0][3][1]}")
                        strings_Cargo_apendiar.append(texto)

                    # Hacer caso de Cargo
                    # Crea la variable string con lo que dice el texto en cada mail
                    elif "Cargo".lower() in asunto.lower():
                        cargos += 1
                        texto = charge_on_bank_account(driver=driver, email_element=email)
                        lista = clean_list([texto])
                        fecha = day_already_pass(f"{lista[0][3][0]} {lista[0][3][1]}")
                        strings_Cargo_apendiar.append(texto)
                        print("✅ Cargo registrado")

                    # Hacer caso transferencias
                    # Distinguir hechas de recibidas
                    # Caso especial, agregar destinatario.
                    elif "Transferencia".lower() in asunto.lower():
                        # Unique posibility Banco de Chile do a Transference of money
                        # Most easy case
                        if "Transferencia a terceros".lower() in asunto.lower():
                            print("Yo transfiriendo a otro")
                            transferencias_a_terceros += 1
                            texto = transfer_founds_for_you(driver=driver, email_element=email)
                            print(texto, texto.get("Fecha") + " " +  texto.get("Hora"))
                            fecha = day_already_pass(texto.get("Fecha") + " " +  texto.get("Hora"))
                            strings_Cargo_apendiar.append(texto)
                        
                        elif "Recibiste una transferencia".lower() in asunto.lower() or "itau informa".lower() in asunto.lower() or "Transferencia de fondos".lower() in asunto.lower():
                            transferencias_de_terceros += 1
                            # Banco BICE
                            if "Recibiste una transferencia".lower() in asunto.lower():
                                texto = transfer_founds_to_you(driver=driver, email_element=email, bank="BICE")
                                #print("\n", texto, "\n")
                                fecha = day_already_pass(texto.get("Fecha") + " " +  texto.get("Hora"))
                                strings_Cargo_apendiar.append(texto)
                            # Banco ITAU
                            elif "itau informa".lower() in asunto.lower():
                                texto = transfer_founds_to_you(driver=driver, email_element=email, bank="ITAU")
                                print("\n", texto, "\n")
                                #print("Siguiente paso: FECHA STR")
                                fecha = day_already_pass(texto.get("Fecha") + " " +  texto.get("Hora"))
                                strings_Cargo_apendiar.append(texto)

                            # Banco Edwards
                            elif "Transferencia de fondos".lower() in asunto.lower():
                                texto = transfer_founds_to_you(driver=driver, email_element=email, bank="EDWARDS")
                                print("\n", texto, "\n")
                                print("Siguiente paso: FECHA STR")
                                fecha = day_already_pass(texto.get("Fecha") + " " +  texto.get("Hora"))
                                strings_Cargo_apendiar.append(texto)
                            
                            # Banco Security
                            elif "Transferencia de fondos".lower() in asunto.lower():
                                texto = transfer_founds_to_you(driver=driver, email_element=email, bank="SECURITY")
                                print("\n", texto, "\n")
                                print("Siguiente paso: FECHA STR")
                                fecha = day_already_pass(texto.get("Fecha") + " " +  texto.get("Hora"))
                                strings_Cargo_apendiar.append(texto)
                            print("✅ Transferencia registrada")
                        transferencias += 1
                    
                    #if texto != "":
                    #    print("\n", texto, "\n")
                    #print(f"Contenido: {contenido}")
                except Exception as e:
                    print(f"\nError procesando email #{i}: {str(e)}\n")

            if fecha == True:
                strings_Cargo_apendiar.pop()
                append_on_txt(lista=strings_Cargo_apendiar)
                #print("CARGO A APPENDEAR", strings_Cargo_apendiar)
                sort_transaction_txt()
                print(f"Cargos: {cargos}\nTransferencias: {transferencias}\nDevoluciones: {devoluciones}")
                calcular_total()
                parar = True
                sys.exit()
                return 

        append_on_txt(lista=strings_Cargo_apendiar)
        verificar_mensaje_no_resultados(driver=driver)
        print(f"\n📊 Resumen Final:\n")
        print(f"Cargos: {cargos}\nTransferencias: {transferencias}\nTransferencias de terceros: {transferencias_de_terceros}\nTransferencias a terceros: {transferencias_a_terceros}\nDevoluciones: {devoluciones}\n")

    # Verify if the mennsage of No resultados arrise.
    # if No resultados its not present return False.
    # It works for as a stop at the page changer function.
    def verificar_mensaje_no_resultados(driver):
        """Verifica si aparece el mensaje de 'no resultados' en la página"""
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'No hay ningún mensaje que coincida')]")
                )
            )
            return True
        except:
            return False

    pagina_principal = driver.current_url
    next_page(driver=driver, main_page=pagina_principal, parar=parar)
    sort_transaction_txt()

if __name__ == "__main__":
    scraping_emails(sys.argv)
    total = calcular_total()
    gasto_diario = calcular_gasto_diario(total)
    porcentaje_restante = calcular_porcentaje_restante(total, 150000)
    string = "💰 Saldo actual: $" + str(total)
    print(string)
    string = "📆 Gasto diario recomendado: $" + str(gasto_diario)
    print(string) 
    print("📈", porcentaje_restante)
    print("✅ **Proceso de scrapping completado exitosamente** 🚀")
    #sleep(20)
    #mandar_total(total)