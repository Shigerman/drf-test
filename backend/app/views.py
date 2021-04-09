from __future__ import annotations
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
from backend.app.serializers import ItemSerializer, UserSerializer
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
def register_user(request):
    username: str = request.data.get("username")
    password: str = request.data.get("password")

    if None in (username, password):
        return Response({"error": "need username, password"}, status=400)
    if 0 in list(map(len, [username, password])):
        return Response({"error": "username, password len > 0"}, status=400)

    if User.objects.filter(username=username).first():
        return Response({"error": "username already used"}, status=400)
    user: User = User.objects.create_user( # type: ignore
        username, email := None, password)
    if not user:
        return Response({"error": "can't create"}, status=500)
    return Response({"success": "user created"}, status=201)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
@parser_classes([JSONParser])
def login(request):
    username: str = request.data.get("username")
    password: str = request.data.get("password")

    if None in (username, password):
        return Response({"error": "need username, password"}, status=400)
    if 0 in list(map(len, [username, password])):
        return Response({"error": "username, password len > 0"}, status=400)

    user = django_authenticate(username=username, password=password)
    if not user:
        return Response({"error": "auth error"}, status=400)

    # the method returns a tuple, and we do not need the second element
    token: Token
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated,])
@parser_classes([JSONParser])
def create_item(request):
    name: str = request.data.get("name")
    if not name or len(name) == 0:
        return Response({"error": "need name"}, status=400)

    # Assume we can have many items with same name
    item: Item = Item.objects.create(name=name, user=request.user)
    return Response({"item_id": item.id}, status=201) # type: ignore


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated,])
@parser_classes([JSONParser])
def send_item_to_user(request):
    """ a user can offer an item to another user """

    item_to_send_id: int = request.data.get("item_id")
    receiver_name: str = request.data.get("username")

    if None in (item_to_send_id, receiver_name):
        return Response({"error": "item_id & username required"}, status=400)

    # Allow more than one /send via transaction records
    with transaction.atomic():

        item_to_send: Item = Item.objects.get(id=item_to_send_id)
        if not item_to_send:
            return Response({"error": "no such item"}, status=404)

        receiver: User | None = User.objects.filter(
            username=receiver_name).first()
        if not receiver:
            return Response({"error": "receiver not found"}, status=404)

        trade_offer: TradeOffer = TradeOffer.objects.create(
            sender=request.user,
            receiver=receiver,
            item=item_to_send,
            status=TradeOffer.STATUS_PENDING)

        return Response({"offer_code": trade_offer.offer_code})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated,])
@parser_classes([JSONParser])
def get_item_from_user(request):
    """ a user can receive an item from another user """

    offer_code: str = request.data.get("offer_code")
    if not offer_code:
        return Response({"error": "offer_code required"}, status=400)

    receiver: User = request.user

    # inside transaction so that other transactions do not interfere
    with transaction.atomic():
        # find the trade offer to execute by the offer code (guid)
        trade_offer: TradeOffer | None = TradeOffer.objects.filter(
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

        return Response({"success": "trade offer was accepted"})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated,])
@parser_classes([JSONParser])
def get_item_list_for_user(request):
    """ get all items of the logged-in user """
    items = Item.objects.filter(user=request.user)
    return Response({"items": [ItemSerializer(v).data for v in items]})
