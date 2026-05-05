import smtplib
from email.mime.text import MIMEText

def enviar_codigo_email(destino: str, codigo: str):
    remitente = "hawk1809em@gmail.com"
    password = "depjvgbfmnkksoxe"

    mensaje = MIMEText(f"Tu código 2FA es: {codigo}")
    mensaje["Subject"] = "Código de verificación SIGI-A"
    mensaje["From"] = remitente
    mensaje["To"] = destino

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(remitente, password)
        server.send_message(mensaje)