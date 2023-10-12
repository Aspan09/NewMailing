import os
from django.shortcuts import render
from rest_framework import viewsets, generics, status
from .serializers import ClientSerializer, MessageSerializer, MailingSerializer
from .models import Client, Mailing, Message
from django.db.models import Count
from rest_framework.response import Response
from datetime import datetime
from django.db import transaction
from .tasks import process_mailing  # Создайте задачу для обработки рассылки
from django.utils import timezone  # Импортируйте timezone
from rest_framework.views import APIView
import requests
import jwt


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class MailingViewSet(viewsets.ModelViewSet):
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        start_datetime_str = data.get('start_datetime')
        end_datetime_str = data.get('end_datetime')

        current_datetime = timezone.now()  # Используйте timezone.now() для текущего времени

        if start_datetime_str:
            start_datetime = timezone.make_aware(datetime.strptime(start_datetime_str, "%Y-%m-%dT%H:%M:%S"))
        else:
            start_datetime = current_datetime

        if end_datetime_str:
            end_datetime = timezone.make_aware(datetime.strptime(end_datetime_str, "%Y-%m-%dT%H:%M:%S"))
        else:
            end_datetime = None

        if end_datetime is not None and start_datetime <= current_datetime <= end_datetime:
            # Если текущее время внутри интервала, начать рассылку немедленно
            with transaction.atomic():
                mailing = Mailing.objects.create(**data)
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
            return Response(MailingSerializer(mailing).data, status=status.HTTP_201_CREATED)

        if end_datetime is not None and current_datetime < start_datetime:
            # Если начало рассылки в будущем, запланировать ее старт
            mailing = Mailing.objects.create(**data)
            process_mailing.apply_async(args=(mailing.id,), eta=start_datetime)
            return Response(MailingSerializer(mailing).data, status=status.HTTP_201_CREATED)

        return Response({'error': 'Invalid start and end times'}, status=status.HTTP_400_BAD_REQUEST)


class MessageListByMailingView(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        mailing_id = self.kwargs['mailing_id']
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
            return Message.objects.filter(mailing=mailing)
        except Mailing.DoesNotExist:
            return Message.objects.none()


class MailingStatisticsView(generics.RetrieveAPIView):
    serializer_class = MailingSerializer

    def get_object(self):
        mailing_id = self.kwargs.get('mailing_id')
        return Mailing.objects.get(pk=mailing_id)

    def retrieve(self, request, *args, **kwargs):
        mailing = self.get_object()
        message_statuses = Message.objects.filter(mailing=mailing).values('status').annotate(count=Count('id'))
        return Response({'mailing': MailingSerializer(mailing).data, 'message_statuses': message_statuses})


class SendMessageView(APIView):
    # Функция для отправки сообщения
    @staticmethod
    def send_message(message_text, recipient_phone):
        # Определите ваш JWT-токен и базовый URL
        jwt_token = os.environ.get("JWT_TOKEN")
        base_url = 'https://probe.fbrq.cloud/v1'

        # Создайте заголовок с JWT-токеном
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }

        # Создайте тело запроса с данными для отправки сообщения
        data = {
            'message_text': message_text,
            'recipient_phone': recipient_phone
        }

        # Отправьте POST-запрос к внешнему сервису для отправки сообщения
        try:
            response = requests.post(f'{base_url}/send_message/', json=data, headers=headers)
            response.raise_for_status()  # Проверьте статус ответа на ошибки
            return response.json()  # Верните JSON-ответ в виде словаря
        except requests.exceptions.RequestException as e:
            print(f'Ошибка при отправке сообщения: {e}')
            return None

    # Обработка POST-запроса
    def post(self, request):
        # Получите данные для отправки сообщения из запроса
        message_text = request.data.get('message_text', '')
        recipient_phone = request.data.get('recipient_phone', '')

        # Проверьте наличие текста сообщения и номера получателя
        if not message_text or not recipient_phone:
            return Response({'error': 'Необходим текст сообщения и номер получателя'}, status=status.HTTP_400_BAD_REQUEST)

        # Отправьте сообщение и получите ответ
        response_data = self.send_message(message_text, recipient_phone)

        if response_data:
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Ошибка при отправке сообщения'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
