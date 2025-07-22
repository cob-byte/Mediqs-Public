from django.db import models
from healthcenter.models import User
from django.utils import timezone
from django.contrib.auth import get_user_model

class ChatSession(models.Model):
    user_one = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sessions_as_user_one')
    user_two = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sessions_as_user_two')
    last_message_time = models.DateTimeField(auto_now=True)

class chatMessages(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    message = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', null=True)
    notified = models.BooleanField(default=False)  # True if a notification has been sent for this chat, False otherwise
    def __str__(self):
        return self.message