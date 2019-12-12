from django.urls import path
from . import views

urlpatterns = [
    path('', views.enter, name='marks_parser_enter'),
]