from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes
)
from backend.app.serializers import UserSerializer, ItemSerializer
from backend.app.models import Item, TradeOffer


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
    return Response({"success": "user created"}, status=201)


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
    # the method returns a tuple, and we do not need the second element
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key}, status=200)


@api_view(['POST'])
@parser_classes([JSONParser])
def send(request):
    item_to_send_id = request.data.get("item_id")
    receiver_name = request.data.get("username")
    if None in (item_to_send_id, receiver_name):
        return Response({"error": "item_id & username required"}, status=400)

    # Allow more than one /send via transaction records
    with transaction.atomic():

        item_to_send = Item.objects.get(id=item_to_send_id)
        if not item_to_send:
            return Response({"error": "no such item"}, status=404)

        receiver = User.objects.filter(username=receiver_name).first()
        if not receiver:
            return Response({"error": "receiver not found"}, status=404)

        trade_offer = TradeOffer.objects.create(
            sender=request.user,
            receiver=receiver,
            item=item_to_send,
            status=TradeOffer.STATUS_PENDING)

        return Response({"offer_code": trade_offer.offer_code})


@api_view(['POST'])
@parser_classes([JSONParser])
def get(request):

    offer_code = request.data.get("offer_code")
    if not offer_code:
        return Response({"error": "offer_code required"}, status=400)
    receiver = request.user

    # inside transaction so that other transactions do not interfere
    with transaction.atomic():
        # find the trade offer to execute by the offer code (guid)
        trade_offer = TradeOffer.objects.filter(
            offer_code=offer_code,
            receiver=receiver,
            status=TradeOffer.STATUS_PENDING).first()
        if not trade_offer:
            return Response({"error": "no trade offer"}, status=404)

        # assign the item to the receiver of the offer
        trade_offer.item.user = receiver
        trade_offer.item.save()

        # assign accepted status to the offer, other offers - expired
        trade_offer.status = TradeOffer.STATUS_ACCEPTED
        trade_offer.save()

        all_offers = TradeOffer.objects.filter(
            sender=trade_offer.sender,
            item=trade_offer.item,
            status=TradeOffer.STATUS_PENDING)
        for offer in all_offers:
            offer.status = TradeOffer.STATUS_EXPIRED
            offer.save()

        return Response({"success": "trade offer was accepted"}, status=200)
