from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # This is a placeholder for now, we'll add actual views later
    path('', views.home, name='home'),
]