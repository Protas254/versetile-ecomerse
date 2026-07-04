import requests
import json
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

class SendGridAPIBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = settings.EMAIL_HOST_PASSWORD
        self.api_url = "https://api.sendgrid.com/v3/mail/send"

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent_count = 0
        for message in email_messages:
            if self._send(message):
                sent_count += 1
        return sent_count

    def _send(self, message):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Prepare personalizations
        personalizations = [{
            "to": [{"email": recipient} for recipient in message.to],
            "subject": message.subject
        }]

        # Add CC/BCC if present
        if message.cc:
            personalizations[0]["cc"] = [{"email": recipient} for recipient in message.cc]
        if message.bcc:
            personalizations[0]["bcc"] = [{"email": recipient} for recipient in message.bcc]

        data = {
            "personalizations": personalizations,
            "from": {"email": message.from_email},
            "content": []
        }

        # Handle plain text and HTML content
        if message.body:
            data["content"].append({
                "type": "text/plain",
                "value": message.body
            })

        # Check for HTML alternatives
        if hasattr(message, 'alternatives'):
            for content, mimetype in message.alternatives:
                if mimetype == "text/html":
                    data["content"].append({
                        "type": "text/html",
                        "value": content
                    })

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
            if response.status_code in [200, 201, 202]:
                return True
            else:
                if not self.fail_silently:
                    print(f"SendGrid API Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            if not self.fail_silently:
                print(f"SendGrid API Exception: {str(e)}")
            return False
