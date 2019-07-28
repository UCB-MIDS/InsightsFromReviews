from django.urls import path

from . import views

app_name = 'ai'
urlpatterns = [
	path('', views.home, name='home'),
	path('about/', views.about, name='about'),
    path('actionableinsight/', views.actionableinsight, name='actionableinsight'),
    path('result/', views.result, name='result'),
    path('update/', views.update, name='update'),
]