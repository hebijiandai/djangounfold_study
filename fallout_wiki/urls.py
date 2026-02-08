from django.urls import path
from . import views

app_name = 'fallout_wiki'

urlpatterns = [
    path('', views.wiki_index, name='wiki_index'),
    path('<str:model_name>/<int:pk>/', views.wiki_detail, name='wiki_detail'),
]
