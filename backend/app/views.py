from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes
)
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from backend.app.serializers import UserSerializer, ItemSerializer
from backend.app.models import Item
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
@parser_classes([JSONParser])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if None in (username, password):
        return Response({"error": "username & password required"}, status=400)
    if 0 in list(map(len, [username, password])):
        return Response({"error": "username & password len > 0"}, status=400)
    email = None
    user = User.objects.create_user(username, email, password) # type: ignore
    if not user:
        return Response({"error": "already exists"}, status=400)
    return Response({"success": "user created"})


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
@parser_classes([JSONParser])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if None in (username, password):
        return Response({"error": "username & password required"}, status=400)
    if 0 in list(map(len, [username, password])):
        return Response({"error": "username & password len > 0"}, status=400)
    user = django_authenticate(username=username, password=password)
    if not user:
        return Response({"error": "auth error"}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


@api_view(['POST'])
@parser_classes([JSONParser])
def send(request): ...

@api_view(['POST'])
@parser_classes([JSONParser])
def get(request): ...
