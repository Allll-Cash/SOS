from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from minio import S3Error
from requests import get
from telebot.types import Message

from bot.management.commands.bot import bot
from studreply.integrations import minio


class Student(models.Model):
    telegram_id = models.IntegerField(null=False, db_index=True)
    previous_state = models.TextField(default="new")
    state = models.TextField(default="new")
    telegram_username = models.TextField(default="")
    telegram_name = models.TextField(default="")

    def set_state(self, state: str):
        self.previous_state = self.state
        self.state = state

    def rollback(self):
        self.state = self.previous_state

    @property
    def requests(self):
        return Request.objects.filter(student=self)

    @property
    def last_request(self):
        return Request.objects.filter(student=self).last()


class Request(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_index=True)
    status = models.IntegerField(default=1)  # 0 - взята, 1 - вакантна, 2 - выполнена
    destination = models.TextField(db_index=True, null=True)
    anonymous = models.BooleanField(default=False)
    reason = models.TextField(default="")
    faculty = models.TextField(default="")
    ready = models.BooleanField(default=False)

    @property
    def last_message(self):
        return TelegramMessage.objects.filter(request=self).last()

    @property
    def unreplied(self):
        last = self.last_message
        if last is None:
            return False
        return not self.last_message.sent_by_operator and self.status != 2

    @property
    def messages(self):
        return TelegramMessage.objects.filter(request=self).order_by("time_sent")


class TelegramMessage(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, db_index=True)
    text = models.TextField()
    time_sent = models.DateTimeField(default=timezone.now)
    sent_by_operator = models.BooleanField(default=False)

    def attach_photo(self, message: Message):
        photo = message.photo
        if photo is not None:
            photo = get(bot.get_file_url(photo[-1].file_id)).content
            minio.put_object(f"photos/{self.id}.jpg", photo)

    def has_photo(self):
        try:
            minio.get_object(f"photos/{self.id}.jpg")
            return True
        except S3Error:
            return False


@receiver(post_delete, sender=TelegramMessage)
def delete_file_hook(sender, instance, using, **kwargs):
    minio.remove_object(f"photos/{instance.id}.jpg")
