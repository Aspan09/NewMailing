from celery import shared_task
from datetime import datetime
from .models import Mailing, Message
from .models import Client  # Импортируйте модель Client


@shared_task
def process_mailing(mailing_id):
    try:
        mailing = Mailing.objects.get(pk=mailing_id)
        if mailing.start_datetime <= datetime.now() <= mailing.end_datetime:
            clients = Client.objects.filter(
                operator_code=mailing.client_filter_operator_code,
                tag=mailing.client_filter_tag
            )
            for client in clients:
                Message.objects.create(
                    status='Pending',
                    mailing=mailing,
                    client=client
                )
    except Mailing.DoesNotExist:
        pass  # Обработка ошибки, если рассылка не найдена или уже закончилась

