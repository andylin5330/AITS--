from django.urls import path
from . import views

urlpatterns = [
    path('trigger-ws-task/', views.trigger_celery_ws_task, name='trigger_ws_task'),
]
