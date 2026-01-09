from twilio.rest import Client
from django.conf import settings

# Use your Twilio credentials from settings.py
account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
twilio_whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER

client = Client(account_sid, auth_token)

def send_whatsapp_reminder(to_number, message):
    """Send a WhatsApp reminder using Twilio API"""
    client.messages.create(
        from_=f'whatsapp:{twilio_whatsapp_number}',
        body=message,
        to=f'whatsapp:{to_number}'
    )
