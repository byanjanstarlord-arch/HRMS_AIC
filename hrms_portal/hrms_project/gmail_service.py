import base64
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')


def _load_credentials():
    token_json = os.environ.get('GMAIL_TOKEN_JSON', '').strip()
    if token_json:
        try:
            token_info = json.loads(token_json)
        except json.JSONDecodeError as exc:
            raise ValueError('Invalid JSON in GMAIL_TOKEN_JSON') from exc
        return Credentials.from_authorized_user_info(token_info, SCOPES)

    token_path = os.environ.get('GMAIL_TOKEN_PATH', TOKEN_PATH)
    if os.path.exists(token_path):
        return Credentials.from_authorized_user_file(token_path, SCOPES)

    raise FileNotFoundError(
        'Gmail token not found. Set GMAIL_TOKEN_JSON in Railway variables '
        f'or provide token file at: {token_path}'
    )


def send_email(to_email, subject, message, html_message=None):
    creds = _load_credentials()

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