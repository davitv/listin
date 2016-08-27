from django.core.management.base import BaseCommand
from post_office import mail
from django.template import loader
from django.conf import settings


class Command(BaseCommand):
    help = 'Sends test email for checking out smtp state'

    def add_arguments(self, parser):
        parser.add_argument('recipients', nargs='+', type=str)

    def handle(self, *args, **options):
        res = mail.send(
                    options['recipients'],
                    settings.EMAIL_HOST_USER,
                    subject='Test email',
                    message='Hi there!',
                    html_message='Hi <strong>there</strong>!',
                    priority='now',
                )
        print res
        self.stdout.write(self.style.SUCCESS('Successfully sent mails to %s' % (options['recipients'])))
