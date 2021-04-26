from smtplib import SMTP_SSL
from ssl import create_default_context

def send_mail(orders):
    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = "aconquihell@ensc.fr"
    receiver_email = "antoineconqui@gmail.com"
    password = "17Fevrier@"
    if len(orders) == 0:
        message = "Subject: No orders today."
    else:
        message = "Subject: Go "
        for order in orders:
            message += " - " + order[0] + " " + order[1]

    context = create_default_context()
    with SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)