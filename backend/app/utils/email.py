import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()


def enviar_codigo_email(destino: str, codigo: str):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    remitente = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM", remitente)

    if not remitente or not password:
        raise Exception("Faltan variables SMTP_USER o SMTP_PASSWORD en el entorno")

    mensaje = MIMEText(f"Tu código 2FA es: {codigo}")

    mensaje["Subject"] = "Código SIGI-A"
    mensaje["From"] = email_from
    mensaje["To"] = destino

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(remitente, password)
        server.send_message(mensaje)