from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib


SMTP_SERVER = "smtp.qq.com"
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')


def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(SMTP_USERNAME, EMAIL_RECIPIENT, text)
    server.quit()
