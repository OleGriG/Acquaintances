from django.urls import path
from .views import RegistrUserView

app_name = 'api'

urlpatterns = [
    path('clients/create/', RegistrUserView.as_view(), name='registr'),
]
