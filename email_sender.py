from smtplib import SMTP_SSL
from ssl import create_default_context
from email.message import EmailMessage
from imghdr import what


def send_mail(orders):
    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = "aconquihell@ensc.fr"
    receiver_email = "antoineconqui@gmail.com"
    password = "17Fevrier@"

    msg = EmailMessage()

    for order in orders:
        with open(order['image'], 'rb') as file:
            img_data = file.read()
            msg.add_attachment(img_data, maintype='image', subtype=what(None, img_data))

    context = create_default_context()

    with SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg,sender_email, receiver_email)