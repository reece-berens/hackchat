from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('<str:roomName>/', views.room, name='room')
]
