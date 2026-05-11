import smtplib
import os

from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()


def enviar_codigo_email(destino: str, codigo: str):

    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")

    mensaje = MIMEText(
        f"Tu código 2FA es: {codigo}"
    )

    mensaje["Subject"] = "Código SIGI-A"
    mensaje["From"] = remitente
    mensaje["To"] = destino

    with smtplib.SMTP(
        "smtp.gmail.com",
        587
    ) as server:

        server.starttls()

        server.login(
            remitente,
            password
        )

        server.send_message(mensaje)