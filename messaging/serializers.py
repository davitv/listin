from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from core.serializers import UserSerializer

from messaging.models import Message, MessageText, Room

from utils.serializers import ConcatenatedListField


class MessageSerializer(serializers.Serializer):
    """
    This is the main serializer that handles messaging
    logics.
    """
    text = serializers.CharField(required=True, )
    to_users = ConcatenatedListField(required=False,
                                     child=serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all()))
    sender = UserSerializer(read_only=True,)
    date_added = serializers.DateTimeField(read_only=True,)
    pk = serializers.IntegerField(read_only=True,)
    is_watched = serializers.IntegerField(read_only=True,)
    user_cache = None
    room_cache = None
    default_error_messages = {
        'room_or_users_required': _("Specify room or recipients"),
    }

    def __init__(self, *args, **kwargs):
        if 'context' in kwargs:
            self.user_cache = kwargs['context'].pop('user', None)
            self.room_cache = kwargs['context'].pop('room', None)
        super(MessageSerializer, self).__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        message_text = MessageText(
            user=self.user_cache,
            text=validated_data['text'],
        )
        message_text.save()
        ret = self.create_messages(message_text)
        return ret

    def create_messages(self, message_text):
        ret = None
        for user in self.room_cache.users.all():
            message = Message(
                user=user,
                message=message_text,
                is_watched=0,
                room=self.room_cache
            )
            if user == self.user_cache:
                message.is_watched = 1
                ret = message
            message.save()
        return ret

    def validate(self, data):
        data['user'] = self.user_cache
        if self.room_cache is None:
            try:
                assert data.get('to_users', False)
                data['to_users'].append(self.user_cache)
            except AssertionError:
                raise serializers.ValidationError(
                    self.error_messages['room_or_users_required']
                )
            else:
                self.room_cache = Room.objects.get_or_create_room(users=data['to_users'])

        return data
