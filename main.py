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
    def __init__(self, model_choice):
        self.service = None
        self.model_choice = model_choice
        self.nome_vaga = None
        self.nome_empresa = None


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


    def get_message(self, **kwargs):
        message = None
        if self.model_choice == "1":
            message = input("Deseja personalizar a mensagem? Caso não deseje, pressione Enter: ")
        if not message:
            filename = "candidacy-model.txt" if self.model_choice == "1" else "interest-model.txt"
            with open(f"data/{filename}", "r", encoding='utf-8') as file:
                message = file.read()
        message = f"{get_greeting()}\n\n{message.format(**kwargs)}"
        return message


    def get_email_data(self):
        nome_empresa = None
        nome_vaga = None
        fonte = None
        if self.model_choice == "1":
            nome_vaga = input("Digite o nome da vaga: ")
            subject = f"Candidatura à vaga de {nome_vaga}"
        elif self.model_choice == "2":
            nome_empresa = input("Digite o nome da empresa: ")
            fonte = input("Digite a fonte da vaga: ")
            subject = f"Demonstração de interesse em futuras vagas na {nome_empresa}"
        return subject, nome_empresa, nome_vaga, fonte


    def send_email(self, attachment=None):
        message = MIMEMultipart()
        subject, nome_empresa, nome_vaga, fonte = self.get_email_data()
        content = self.get_message(nome_empresa=nome_empresa, nome_vaga=nome_vaga, fonte=fonte)
        message.attach(MIMEText(content, 'plain', 'utf-8'))
        message["To"] = input("Digite o e-mail do destinatário: ")
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
    model_choice = input("Deseja se candidatar(1) ou demonstrar interesse em futuras vagas(2)? ")
    email_service = EmailService(model_choice)
    email_service.authenticate()
    message = email_service.send_email(
        "data/resume.pdf"
    )
    print(f"E-mail enviado com sucesso! ID: {message['id']}")


if __name__ == "__main__":
    main()