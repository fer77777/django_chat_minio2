from django.urls import path
from .views import *

urlpatterns = [
    path('', chat_view, name='home'),
    path('limpiar/', limpiar_chat_view, name='limpiar_chat'),
]
