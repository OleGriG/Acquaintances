from django.urls import path
from .views import RegistrUserView, match

app_name = 'api'

urlpatterns = [
    path('clients/create/', RegistrUserView.as_view(), name='registr'),
    path('clients/<int:pk>/match/', match, name='match'),
]
