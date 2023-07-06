from django.urls import path
from .views import RegistrUserView, match, UserListView

app_name = 'api'

urlpatterns = [
    path('clients/create/', RegistrUserView.as_view(), name='registr'),
    path('clients/<int:pk>/match/', match, name='match'),
    path('list/', UserListView.as_view(), name='list-users')
]
