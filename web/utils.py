from django.core.mail import EmailMessage
import time

class Util:
    @staticmethod
    def send_email(data):
        #time.sleep(120)
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        email.send()