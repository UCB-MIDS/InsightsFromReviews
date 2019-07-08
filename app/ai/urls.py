from django.urls import path

from . import views

app_name = 'ai'
urlpatterns = [
    path('', views.index, name='index'),
    path('result/', views.result, name='result'),
    path('update/', views.update, name='update'),
]