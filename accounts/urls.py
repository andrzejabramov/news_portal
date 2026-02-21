from django.urls import path
from .views import become_author

app_name = 'accounts'

urlpatterns = [
    path('become-author/', become_author, name='become_author'),
]