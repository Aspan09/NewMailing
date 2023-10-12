from django.utils import timezone  # Импортируйте timezone
from django.core.validators import RegexValidator
from django.db import models


class Mailing(models.Model):
    id = models.AutoField(primary_key=True)
    start_datetime = models.DateTimeField(default=timezone.now)  # Используйте timezone.now() для текущего времени
    end_datetime = models.DateTimeField(blank=True, null=True)  # Разрешите пустое значение для end_datetime
    message_text = models.TextField()
    client_filter_operator_code = models.CharField(max_length=10)
    client_filter_tag = models.CharField(max_length=255)

    def __str__(self):
        return f"Рассылка {self.id}"


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    phone_number = models.CharField(max_length=12, unique=True, validators=[
        RegexValidator(r'^7\d{10}$', message='Phone number must be in the format 7XXXXXXXXXX')])

    operator_code = models.CharField(max_length=10)
    tag = models.CharField(max_length=255)
    timezone = models.CharField(max_length=255)

    def __str__(self):
        return f"Клиент {self.id}"


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return f"Сообщении {self.id}"

