import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER

    # Gmail SMTP server setup
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(EMAIL_USER, EMAIL_PASS)
    server.send_message(msg)
    server.quit()
