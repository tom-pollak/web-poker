from django.urls import path
from . import views

urlpatterns = [
     path('', views.index, name='index'),
     path('reset-money/', views.resetMoney, name='resetMoney'),
     path('create-table/', views.createTable, name='tableCreateView')
]