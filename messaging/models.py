from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings


class RoomManager(models.Manager):
    def get_chat_room(self, users):
        """
        This method will find room in which are those users
        are participants.
        :param users: settings.AUTH_USER_MODEL queryset
        :return: Room instance
        """
        rooms = None
        available_rooms = self.annotate(count=models.Count('users')).filter(users=users[0])
        for user in users[1:]:
            rooms = available_rooms.filter(users=user)
        if rooms:
            return rooms.filter(count=len(users)).first()
        else:
            return rooms

    def get_or_create_room(self, users):
        """
        This method will find room in which are those users
        are participants. If it's not exist, will create new
        one, add those users and return it.
        :param users: settings.AUTH_USER_MODEL queryset
        :return: Room instance
        """
        room = self.get_chat_room(users)
        if room:
            return room
        else:
            return self.create_room(users)

    def create_room(self, users):
        room = self.model()
        room.save()
        room.users = users
        return room


@python_2_unicode_compatible
class Room(models.Model):
    """
    Room which are keeping users messages together.
    Made for making possible for particular users have
    conference chat together.
    """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="room_creator", blank=True, null=True,)
    name = models.CharField(max_length=200, blank=True, null=True,)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='participants')
    kind = models.PositiveIntegerField(default=0, blank=True, null=False,)

    label = models.CharField(max_length=200, blank=True, null=True, )

    date_added = models.DateTimeField(auto_now_add=True,)
    date_modified = models.DateTimeField(auto_now=True,)

    objects = RoomManager()

    def __str__(self):
        return '(%s)' % (self.name, )


@python_2_unicode_compatible
class MessageText(models.Model):
    """
    This is the main model for message. It's keeps message basic
    data.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sender",)
    kind = models.PositiveIntegerField(default=0, blank=True, null=False,)
    text = models.TextField(blank=False, null=False,)
    is_removed = models.PositiveIntegerField(default=0, blank=True, null=False, )
    date_added = models.DateTimeField(auto_now_add=True,)
    date_modified = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return '(%s) to %s' % (self.user, self.date_added, )


class MessageManager(models.Manager):
    def get_room_messages(self, user, participants):
        """
        This method will find room in which are those users
        are participants and return messages related to that user.
        :param user: settings.AUTH_USER_MODEL
        :param participants: list of pks of participants
        :return: Message queryset
        """
        # lists are mutable
        all_participants = participants[:]
        all_participants.append(user.pk)
        room = Room.objects.get_chat_room(all_participants)
        if room:
            return self.filter(room=room, user=user)
        return self.none()


@python_2_unicode_compatible
class Message(models.Model):
    """
    This model is actual message for enduser. Using this model
    as a helper for main MessageText model we can implement
    watched/unwatched functionality, easy querying all messages
    that are available for particular user.
    """
    message = models.ForeignKey(MessageText, blank=True, null=False,)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=False,)
    room = models.ForeignKey(Room, blank=True, null=True,)

    is_watched = models.PositiveIntegerField(default=0, blank=True, null=False, )

    date_added = models.DateTimeField(auto_now_add=True,)
    date_modified = models.DateTimeField(auto_now=True,)

    objects = MessageManager()

    def __str__(self):
        return '%s (%s)' % (self.sender, self.date, )

    @property
    def text(self):
        return self.message.text

    @property
    def kind(self):
        return self.message.kind

    @property
    def sender(self):
        return self.message.user

    @property
    def date(self):
        return self.message.date_added
