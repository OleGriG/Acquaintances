from django.http import JsonResponse
from django.core.mail import send_mail

from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from geopy import distance

from .models import User, Like
from .serializers import UserRegistrSerializer, UserSerializer
from acquaintances import settings


class RegistrUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['response'] = True
            return Response(data, status=status.HTTP_200_OK)
        else: 
            data = serializer.errors
            return Response(data)


def match(request, pk):
    try:
        participant = request.user
        liked_participant = User.objects.get(id=pk)
        if Like.objects.filter(participant=liked_participant,
                               liked_participant=participant).exists():
            send_mail(
                'Взаимная симпатия',
                f'Вы понравились {participant.get_full_name()}!' +
                f' Почта участника: {participant.email}',
                settings.DEFAULT_FROM_EMAIL,
                [participant.email, liked_participant.email],
                fail_silently=False,
            )
            return JsonResponse({'message': 'Взаимная симпатия'})
        Like.objects.create(participant=request.user,
                            liked_participant=liked_participant)
        return JsonResponse({'message': 'Успешно оценено'})
    except User.DoesNotExist:
        return JsonResponse({'message': 'Участник не найден'})
    

class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['sex', 'first_name', 'last_name']
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        queryset = User.objects.all().exclude(id=self.request.user.id)
        distparam = self.request.GET.get('distance')
        if distparam:
            filtered_queryset = []
            for user in queryset:
                from_loc = (self.request.user.latitude,
                            self.request.user.longitude)
                self_loc = (user.latitude, user.longitude)
                distancee = distance.distance(from_loc, self_loc).m
                if distancee < float(distparam):
                    filtered_queryset.append(user)
            return User.objects.filter(
                id__in=[user.id for user in filtered_queryset])
        return queryset
