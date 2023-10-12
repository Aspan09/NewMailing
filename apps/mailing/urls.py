from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, MessageListByMailingView, MailingStatisticsView, MailingViewSet, SendMessageView

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'mailings', MailingViewSet)
router.register(r'messages', MessageListByMailingView, basename='message')


urlpatterns = [

    path('', include(router.urls)),

    # path('mailings/<int:mailing_id>/messages/', MessageListByMailingView.as_view(), name='message-list-by-mailing'),
    path('about_mailings/<int:mailing_id>/', include(router.urls)),

    path('mailings/<int:mailing_id>/statistics/', MailingStatisticsView.as_view(), name='mailing-statistics'),

    path('send_message/', SendMessageView.as_view(), name='send_message'),

]

# clients/<int: id>/ - GET, POST, PUT, DELETE
# mailings/<int: id>/ - GET, POST, PUT, DELETE
