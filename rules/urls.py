from django.urls import path
from . import views

urlpatterns = [
     path('', views.pokerRules, name='pokerRules'),
]