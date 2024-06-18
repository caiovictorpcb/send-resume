import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
import base64
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", 'https://www.googleapis.com/auth/gmail.send']



def get_greeting():
    now = datetime.now()
    if 6 <= now.hour < 12:
        time_greeting = "Bom dia"
    elif 12 <= now.hour < 18:
        time_greeting = "Boa tarde"
    else:
        time_greeting = "Boa noite"
    return f"Olá, {time_greeting}."


class EmailService:
    def __init__(self):
        self.service = None

    def authenticate(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        self.service = build("gmail", "v1", credentials=creds)


    def get_message(self):
        message = input("Enter the message: ")
        nome = input('Seu nome: ')
        if not message:
            with open("data/message.txt", "r", encoding='utf-8') as file:
                message = file.read()
        message = f"{get_greeting()}\n\n{message.format(meu_nome=nome)}"
        return message


    def send_email(self, to, subject, attachment=None):
        message = MIMEMultipart()
        content = self.get_message()
        message.attach(MIMEText(content, 'plain', 'utf-8'))
        message["To"] = to
        message["From"] = "Caio Victor"
        message["Subject"] = subject
        if attachment:
            with open(attachment, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename=Curriculo Caio Victor.pdf",
                )
                message.attach(part)
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}
        message = self.service.users().messages().send(userId="me", body=create_message).execute()

        return message


def main():
    email_service = EmailService()
    email_service.authenticate()
    to = input("Enter the email address: ")
    subject = input("Enter the subject: ")
    message = email_service.send_email(
        to,
        subject,
        "data/resume.pdf"
    )
    print(f"Message Id: {message['id']}")


if __name__ == "__main__":
    main()