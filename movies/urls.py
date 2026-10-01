from django.urls import path

from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.genre_list, name='genre_list'),
    path('recomendaciones/<int:genre_id>/', views.recommendations, name='recommendations'),
]
