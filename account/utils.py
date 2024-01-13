import os

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["subject"],
            body=data["body"],
            from_email=os.environ.get("EMAIL_FROM"),
            to=[data["to_email"]],
        )
        email.send()

    def send_email1(data):
        subject = data["subject"]
        body = data["body"]
        from_email = os.environ.get("EMAIL_FROM")
        to_email = data["to_email"]
        html_message = data["html_message"]

        # Saving HTML content to a temporary file
        temp_file_path = os.path.join(settings.MEDIA_ROOT, "ticket")
        print(temp_file_path)
        with open(temp_file_path, "w") as file:
            file.write(html_message)

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=[to_email],
        )
        # email.attach(html_message, "text/html")
        email.attach_file(temp_file_path)

        try:
            email.send()
            # Handle email sending success
        except Exception as e:
            # Handle exceptions or errors during email sending
            print(f"Error sending email: {e}")
