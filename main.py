import imaplib
import os
import re
import dotenv

env_path = r"C:\Users\csanh\OneDrive\Escritorio\PDF PUC\Semestre 5\Innovación, desarollo y emprendimiento\Codigo web scrapping\credenciales.env"
dotenv.load_dotenv(env_path)

username = os.getenv("mail_user")
password = os.getenv("mail_password")
bank = os.getenv("bank_user")
bank_mail = os.getenv("bank_mail")
app_password = os.getenv("gmail_app_password")

# Añade esto después de cargar las variables
if not all([username, app_password, bank_mail]):
    print("¡Error! Faltan variables en el archivo .env")
    print(f"Usuario: {username}\nClave App: {app_password}\nCorreo Banco: {bank_mail}")
    exit()

print(username, password, bank, bank_mail, app_password)

def print_raw_email(email, password, bank_email):
    mail = None
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        mail.login(email, password)
        mail.select('inbox')
        
        # Buscar todos los correos del banco
        status, data = mail.search(None, f'(FROM "{bank_email}")')
        if status != 'OK' or not data[0]:
            print("No hay correos del banco")
            return
            
        # Obtener el último correo
        latest_email_id = data[0].split()[-1]
        status, email_data = mail.fetch(latest_email_id, '(RFC822)')
        raw_email = email_data[0][1].decode('utf-8')
        
        # Guardar en un archivo para analizar
        with open("last_email.txt", "w", encoding="utf-8") as f:
            f.write(raw_email)
        print("¡Correo guardado en last_email.txt!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if mail:
            try:
                mail.close()
                mail.logout()
            except:
                pass

# Ejecutar
print_raw_email(username, app_password, bank_mail)