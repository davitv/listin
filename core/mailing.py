from __future__ import unicode_literals

from django.conf import settings
from django.template import loader

from post_office import mail


def send_staff_invitation(staff):
    if settings.DEBUG:
        domain = "http://localhost:8000"
    else:
        domain = settings.EMAIL_LINKS_URL

    context = dict({
        'user': staff.user,
        'organization': staff.organization,
        'domain': domain
    })
    html_message = loader.render_to_string('email/staff_invite.html', context)
    text_message = loader.render_to_string('profiles/email/confirmation.txt', context)

    mail.send(
        [staff.user.email, ],
        settings.AUTH_MAIL_CONFIRMATION_FROM,
        message=text_message,
        html_message=html_message,
        priority='now',
    )
