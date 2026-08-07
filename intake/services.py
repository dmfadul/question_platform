from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Invitation


def get_valid_invitation(token):
    invitation = get_object_or_404(
        Invitation.objects.select_related("collection"),
        token=token,
        is_active=True,
    )

    collection = invitation.collection

    if not collection.is_open:
        raise PermissionDenied(
            "This question collection is closed."
        )

    if (
        collection.deadline is not None
        and timezone.now() > collection.deadline
    ):
        raise PermissionDenied(
            "The submission deadline has passed."
        )

    Invitation.objects.filter(pk=invitation.pk).update(
        last_accessed_at=timezone.now(),
    )

    return invitation