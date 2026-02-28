from django.urls import path
from .api_agent import generate_agent_cases, save_agent_cases

urlpatterns = [
    path('agent/generate/', generate_agent_cases, name='generate_agent_cases'),
    path('agent/save-cases/', save_agent_cases, name='save_agent_cases'),
]
