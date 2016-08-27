from django.test import TestCase
from django.contrib.auth import get_user_model

from .forms import MessageForm
from .models import Room
from .models import Message
from .serializers import MessageSerializer


class TestMessageForm(TestCase):
    users = []

    def setUp(self):
        user_model_class = get_user_model()
        # create 4 users
        self.users = []
        for x in range(0, 4):
            user = user_model_class(
                first_name="User %s" % (x+1,),
                email="user_%s@email.com" % (x+1,)
            )
            user.set_password('@120804a')
            user.save()
            self.users.append(user)

    def send_message(self, sender, recipients):
        form = MessageForm(sender, data={
            'to_users': recipients,
            'text': "Hello, Liesel!"
        })
        return form

    def test_two_participants(self):
        sender = self.users[0]
        recipient = self.users[1]
        form = self.send_message(sender, str(recipient.pk))

        self.assertTrue(form.is_valid(), form.errors)
        room = form.save()

        self.assertTrue(Room.objects.get_chat_room([sender, recipient, ]))
        self.assertEqual(Message.objects.filter(room=room).count(), 2)
        self.assertEqual(Room.objects.all().count(), 1)

        form = self.send_message(recipient, str(sender.pk))

        self.assertTrue(form.is_valid(), form.errors)
        room = form.save()

        self.assertTrue(Room.objects.get_chat_room([sender, recipient, ]))
        self.assertEqual(Room.objects.all().count(), 1)
        self.assertEqual(Message.objects.filter(room=room).count(), 4)

        form = self.send_message(sender, str(recipient.pk))

        self.assertTrue(form.is_valid(), form.errors)
        room = form.save()

        self.assertTrue(Room.objects.get_chat_room([sender, recipient, ]))
        self.assertEqual(Room.objects.all().count(), 1)
        self.assertEqual(Message.objects.filter(room=room).count(), 6)

    def test_three_participants(self):
        sender = self.users[0]
        recipient1 = self.users[1]
        recipient2 = self.users[2]

        recipients = str(recipient1.pk) + ',' + str(recipient2.pk)

        form = self.send_message(sender, recipients)

        self.assertTrue(form.is_valid(), form.errors)
        room = form.save()

        self.assertTrue(Room.objects.get_chat_room([sender, recipient1, recipient2]))
        self.assertEqual(Message.objects.filter(room=room).count(), 3)
        self.assertEqual(Room.objects.all().count(), 1)

        recipients = str(sender.pk) + ',' + str(recipient2.pk)

        form = self.send_message(recipient1, recipients)

        self.assertTrue(form.is_valid(), form.errors)
        room = form.save()

        self.assertTrue(Room.objects.get_chat_room([sender, recipient1, recipient2]))
        self.assertEqual(Room.objects.all().count(), 1)
        self.assertEqual(Message.objects.filter(room=room).count(), 6)

        # now we will check for clashing 3 on 2 with many to many mess
        recipients = str(recipient1.pk)

        form = self.send_message(sender, recipients)

        self.assertTrue(form.is_valid(), form.errors)
        room = form.save()

        self.assertTrue(Room.objects.get_chat_room([sender, recipient1]))
        self.assertEqual(Room.objects.all().count(), 2)
        messages = Message.objects.filter(room=room)
        self.assertEqual(messages.count(), 2)

        recipients = str(sender.pk)

        form = self.send_message(recipient1, recipients)

        self.assertTrue(form.is_valid(), form.errors)
        room = form.save()

        self.assertTrue(Room.objects.get_chat_room([sender, recipient1]))
        self.assertEqual(Room.objects.all().count(), 2)
        messages = Message.objects.filter(room=room)
        self.assertEqual(messages.count(), 4)

        messages = Message.objects.get_room_messages(recipient1, [sender.pk, ])
        self.assertEqual(messages.count(), 2)

        messages = Message.objects.get_room_messages(sender, [recipient1.pk, ])
        self.assertEqual(messages.count(), 2)


class TestMessageSerializer(TestCase):
    users = []

    def setUp(self):
        user_model_class = get_user_model()
        # create 4 users
        self.users = []
        for x in range(0, 4):
            user = user_model_class(
                first_name="User %s" % (x+1,),
                email="user_%s@email.com" % (x+1,)
            )
            user.set_password('@120804a')
            user.save()
            self.users.append(user)

    def send_message(self, sender, recipients, room=None):
        context = {
            'user': sender
        }
        if room is not None:
            context['room'] = room
        return MessageSerializer(
            context=context, data={
                'to_users': recipients,
                'text': "Hello, Liesel!"
            })

    def test_two_participants(self):
        user1 = self.users[0]
        user2 = self.users[1]

        # user 1 sends message to user 2
        serializer = self.send_message(user1, str(user2.pk))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        message = serializer.save()

        self.assertTrue(Room.objects.get_chat_room([user1, user2, ]))
        self.assertTrue(message.is_watched)
        self.assertTrue(message.user == user1)
        self.assertEqual(Message.objects.filter(room=message.room).count(), 2)
        self.assertEqual(Room.objects.all().count(), 1)

        # user 2 replies to previous message, just swap sender and recipient
        serializer = self.send_message(user2, str(user1.pk))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        message = serializer.save()

        self.assertTrue(Room.objects.get_chat_room([user1, user2, ]))
        self.assertTrue(message.is_watched)
        self.assertTrue(message.user == user2)
        self.assertEqual(Message.objects.filter(room=message.room).count(), 4)
        self.assertEqual(Room.objects.all().count(), 1)

        # user 1 replies to previous message of user 2, swap sender and recipient again
        serializer = self.send_message(user1, str(user2.pk))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        message = serializer.save()

        self.assertTrue(Room.objects.get_chat_room([user1, user2, ]))
        self.assertTrue(message.is_watched)
        self.assertTrue(message.user == user1)
        self.assertEqual(Message.objects.filter(room=message.room).count(), 6)
        self.assertEqual(Room.objects.all().count(), 1)

    def test_three_participants(self):
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]

        # user1 sends message to user2 and user3
        recipients = str(user2.pk) + ',' + str(user3.pk)

        serializer = self.send_message(user1, recipients)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        message = serializer.save()
        self.assertTrue(message.is_watched)
        self.assertTrue(message.user == user1)
        self.assertTrue(Room.objects.get_chat_room([user1, user2, user3]))
        self.assertEqual(Message.objects.filter(room=message.room).count(), 3)
        self.assertEqual(Room.objects.all().count(), 1)

        # user2 replies on message of user1
        recipients = str(user1.pk) + ',' + str(user3.pk)

        serializer = self.send_message(user2, recipients)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        message = serializer.save()
        self.assertTrue(message.is_watched)
        self.assertTrue(message.user == user2)
        self.assertTrue(Room.objects.get_chat_room([user1, user2, user3]))
        self.assertEqual(Message.objects.filter(room=message.room).count(), 6)
        self.assertEqual(Room.objects.all().count(), 1)

        # user3 replies on message of user1
        recipients = str(user1.pk) + ',' + str(user2.pk)

        serializer = self.send_message(user3, recipients)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        message = serializer.save()
        self.assertTrue(message.is_watched)
        self.assertTrue(message.user == user3)
        self.assertTrue(Room.objects.get_chat_room([user1, user2, user3]))
        self.assertEqual(Message.objects.filter(room=message.room).count(), 9)
        self.assertEqual(Room.objects.all().count(), 1)

        room_cache = message.room

        # check that another separated room is created
        # when user1 writes to user2 without user3
        recipients = str(user2.pk)

        serializer = self.send_message(user1, recipients)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        message = serializer.save()
        self.assertTrue(message.is_watched)
        self.assertTrue(message.user == user1)
        self.assertTrue(Room.objects.get_chat_room([user1, user2, user3]))

        self.assertEqual(Room.objects.all().count(), 2)
        # amount of messages in previous room of three should stay same
        self.assertEqual(Message.objects.filter(room=room_cache).count(), 9)
        self.assertEqual(Message.objects.filter(room=message.room).count(), 2)

        # now user3 writes in private to user2 (probably something criminal)
        recipients = str(user2.pk)

        serializer = self.send_message(user3, recipients)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        message = serializer.save()
        self.assertTrue(message.is_watched)
        self.assertTrue(message.user == user3)
        self.assertTrue(Room.objects.get_chat_room([user1, user2, user3]))

        self.assertEqual(Room.objects.all().count(), 3)
        # amount of messages in previous room of three should stay same
        self.assertEqual(Message.objects.filter(room=room_cache).count(), 9)
        self.assertEqual(Message.objects.filter(room=message.room).count(), 2)

    def test_explicitly_set_room(self):
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]

        room = Room(
            label='test_room',
        )
        room.save()
        room.users.add(user1, user2, user3)

        # user1 sends message to user2 and user3
        recipients = str(user2.pk) + ',' + str(user3.pk)

        serializer = self.send_message(user1, recipients, room=room)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        message = serializer.save()
        self.assertTrue(message.room.pk == room.pk)
        self.assertTrue(message.is_watched)
        self.assertTrue(message.user == user1)
        self.assertTrue(Room.objects.get_chat_room([user1, user2, user3]))
        self.assertEqual(Message.objects.filter(room=message.room).count(), 3)
        self.assertEqual(Room.objects.all().count(), 1)







