from rest_framework import serializers
from .models import Client, Mailing, Message


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'phone_number', 'operator_code', 'tag', 'timezone']


class MailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = ['id', 'start_datetime', 'end_datetime', 'message_text',
                  'client_filter_operator_code', 'client_filter_tag']


class MessageSerializer(serializers.ModelSerializer):
    client = ClientSerializer()  # Используйте ваш сериализатор для клиентов

    class Meta:
        model = Message
        fields = '__all__'
