import os

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
        # body = data["body"]
        from_email = os.environ.get("EMAIL_FROM")
        to_email = data["to_email"]
        html_message = data["html_message"]

        email = EmailMultiAlternatives(
            subject=subject,
            # body=body,
            from_email=from_email,
            to=[to_email],  # No need to wrap this in an extra list
        )
        email.attach_alternative(html_message, "text/html")

        try:
            email.send()
            # Handle email sending success
        except Exception as e:
            # Handle exceptions or errors during email sending
            print(f"Error sending email: {e}")
