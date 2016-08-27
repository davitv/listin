from django.core.management.base import BaseCommand
from twilio.rest import TwilioRestClient

account_sid = "AC777ac914a3a50baf7c7ef56802cb0fe3"
auth_token = "37343a8834b650f7d459d2a49e2c883e"
client = TwilioRestClient(account_sid, auth_token)


class Command(BaseCommand):
    help = 'Sends test email for checking out smtp state'

    def handle(self, *args, **options):
        message = client.messages.create(body="Areg Piliposyan, the CIA is watching you."
                                              " We saw your dog and we are not scared at all!",
            to="+37493048377",    # Replace with your phone number
            from_="+12056901425") # Replace with your Twilio number
        self.stdout.write(self.style.SUCCESS('Successfully sent sms %s ' % (message.sid,)))
