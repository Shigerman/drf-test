from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User


def make_uuid_str():
    return uuid4().hex


class Item(models.Model):
    name = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}: {self.name} IS OWNED BY {self.user.username}"


class TradeOffer(models.Model):
    # Assume users are NOT deleted, otherwise item transfer gets messy.
    sender = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='item_sender')
    receiver = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='item_receiver')
    # Assume items are NOT deleted, otherwise item transfer gets messy.
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    # New, unaccepted TradeOffer.
    STATUS_PENDING = 2
    # TradeOffer accepted by its receiver.
    STATUS_ACCEPTED = 3
    # Accepted by other receiver (if TradeOffer was offered to multiple).
    STATUS_EXPIRED = 4

    _STATUS_CHOICES = (
        (STATUS_PENDING, 2),
        (STATUS_ACCEPTED, 3),
        (STATUS_EXPIRED, 4),
    )
    status = models.IntegerField(choices=_STATUS_CHOICES, default=2)
    offer_code = models.TextField(default=make_uuid_str)

    def __str__(self):
        return f"{self.id}: {self.sender.username} IS SENDING \
            {self.item.name} TO {self.receiver.username}"
