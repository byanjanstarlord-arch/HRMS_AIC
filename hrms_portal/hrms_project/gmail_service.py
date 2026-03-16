import base64
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')


def send_email(to_email, subject, message, html_message=None):

    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(
            f"Gmail token not found at: {TOKEN_PATH}. Run hrms_project/gmail_auth.py first."
        )

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    service = build('gmail', 'v1', credentials=creds)

    if html_message:
        msg = MIMEMultipart('alternative')
        msg.attach(MIMEText(message, 'plain'))
        msg.attach(MIMEText(html_message, 'html'))
    else:
        msg = MIMEText(message)

    msg['to'] = to_email
    msg['subject'] = subject

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    body = {'raw': raw}

    service.users().messages().send(
        userId='me',
        body=body
    ).execute()