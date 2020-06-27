from extensions import mail
from flask_mail import Message


def send_email(title, recipient, html):
    msg = Message(title, recipient)
    msg.html = html
    mail.send(msg)
