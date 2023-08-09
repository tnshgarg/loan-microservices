from __future__ import annotations

import json
import os
import smtplib
from dataclasses import dataclass
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ops.exceptions.ops_exceptions import DevOpsException


@dataclass
class FileAttachment:
    name: str
    data_binary: bytes


class GmailService:

    def __init__(self, sender_email) -> None:
        MAILING_CREDENTIALS = json.loads(os.environ.get("gmail_smtp", "{}"))
        self.credentials = MAILING_CREDENTIALS.get(sender_email, None)
        if self.credentials is None:
            raise DevOpsException(
                context={
                    "msg": "SMTP Credentials not Found",
                    "sender_email": sender_email
                }
            )
        self.sender_email = sender_email

        self.connection = None

    def __enter__(self):
        self.connection = smtplib.SMTP("smtp.gmail.com", 587)
        self.connection.starttls()
        self.connection.login(user=self.sender_email,
                              password=self.credentials)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.connection is not None:
            self.connection.quit()

    def sendmail(self, from_name="", to_name="", subject="", to_addresses=tuple(), message_text="", html_blocks=tuple(), files: tuple[FileAttachment] = tuple()):
        message = MIMEMultipart('alternative')
        message["Subject"] = subject
        message["From"] = from_name
        message["To"] = to_name
        message.attach(MIMEText(message_text, 'plain'))
        html_text = message_text+"\n"
        for html_block in html_blocks:
            html_text += html_block+"\n"
        message.attach(MIMEText(html_text, 'html'))
        for file_attachment in files:
            message.attach(MIMEApplication(
                file_attachment.data_binary, Name=file_attachment.name))

        self.connection.sendmail(
            from_addr=self.sender_email,
            to_addrs=to_addresses,
            msg=message.as_string()
        )
