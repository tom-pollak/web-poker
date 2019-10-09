from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from poker.consumers import PokerConsumer
from tables.consumers import MoneyConsumer

application = ProtocolTypeRouter({
    #http to views is default
    'websocket': AuthMiddlewareStack(URLRouter([
        path('ws/user/<str:username>/', MoneyConsumer), 
        path('ws/tables/<int:pk>/', PokerConsumer),
        ])),
})