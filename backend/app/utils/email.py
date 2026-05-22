import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()


def enviar_email(destino: str, asunto: str, cuerpo: str):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    remitente = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM", remitente)

    if not remitente or not password:
        raise Exception("Faltan variables SMTP_USER o SMTP_PASSWORD en el entorno")

    mensaje = MIMEText(cuerpo, "plain", "utf-8")
    mensaje["Subject"] = asunto
    mensaje["From"] = email_from
    mensaje["To"] = destino

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(remitente, password)
        server.send_message(mensaje)


def enviar_codigo_email(destino: str, codigo: str):
    asunto = "Código SIGI-A"
    cuerpo = f"Tu código 2FA es: {codigo}"

    enviar_email(destino, asunto, cuerpo)


def enviar_link_activacion_email(destinatario: str, link_activacion: str):
    asunto = "Activa tu cuenta en SIGI-A"

    cuerpo = f"""
Hola,

Gracias por registrarte en SIGI-A.

Para activar tu cuenta, ingresa al siguiente enlace:

{link_activacion}

Este enlace vence en 24 horas.

Si no creaste esta cuenta, puedes ignorar este mensaje.
"""

    enviar_email(destinatario, asunto, cuerpo)