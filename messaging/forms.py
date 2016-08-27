from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from .models import Message
from .models import MessageText
from .models import Room


class MessageForm(forms.ModelForm):
    class Meta:
        model = MessageText
        exclude = (
            'is_removed',
            'user',
        )

    to_users = forms.CharField(required=False, )
    room_cache = None
    error_messages = {
        'recipients_not_found': _("Recipients was not found. Sorry."),
        'wrong_recipients_data': _("Invalid recipients data was sent."),
    }

    def __init__(self, sender=None, *args, **kwargs):
        self.sender = sender
        super(MessageForm, self).__init__(*args, **kwargs)

    def clean_to_users(self):
        try:
            pks = self.cleaned_data['to_users'].split(',')
            pks = [int(pk) for pk in pks]
            pks.append(self.sender.pk)
            users = get_user_model().objects.filter(pk__in=pks)
            assert users
        except ValueError:
            raise forms.ValidationError(
                self.error_messages['wrong_recipients_data'],
                'wrong_recipients_data'
            )
        except AssertionError:
            raise forms.ValidationError(
                self.error_messages['recipients_not_found'],
                'recipients_not_found'
            )
        return users

    def clean(self):
        data = self.cleaned_data
        recipients = data['to_users']
        self.room_cache = Room.objects.get_or_create_room(recipients)
        return data

    def create_messages(self, message_text):
        users = self.room_cache.users.all()
        for user in users:
            message = Message(
                message=message_text,
                user=user,
                room=self.room_cache,
                is_watched=False if user != self.sender else True,
            )
            message.save()

    def save(self, commit=True):
        data = self.data
        message_text = MessageText(
            text=data['text'],
            user=self.sender,
        )
        message_text.save()
        self.create_messages(message_text)
        return self.room_cache
