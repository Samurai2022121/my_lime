from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin

from utils import permissions as perms

from .filters import BuyerCountFilter, OfferFilterSet
from .models import BuyerCount, LoyaltyCard, Offer, Range, Voucher
from .serializers import (
    BuyerCountSerializer,
    LoyaltyCardSerializer,
    OfferApplySerializer,
    OfferSerializer,
    RangeSerializer,
    VoucherSerializer,
)


class OfferViewSet(ModelViewSet):
    serializer_class = OfferSerializer
    queryset = Offer.objects.order_by("-created_at")
    lookup_field = "id"
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OfferFilterSet
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_all,
            write=perms.allow_staff,
            apply=perms.allow_staff,
        ),
    )

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(methods=("post",), detail=True)
    @transaction.atomic
    def apply(self, request, **kwargs):
        offer = self.get_object()
        current_time = timezone.now()
        if not all(
            [
                offer.is_active,
                offer.started_at <= current_time,
                offer.ended_at >= current_time,
            ]
        ):
            raise ValidationError("Offer is not available.")

        match offer.type:
            case Offer.TYPES.site:
                offer.application_count += 1
                # `site_limit == 0` means unlimited offer
                if 0 < offer.site_limit <= offer.application_count:
                    offer.is_active = False
                offer.save()

            case Offer.TYPES.buyer:
                request_serializer = OfferApplySerializer(data=request.data)
                request_serializer.is_valid(raise_exception=True)
                phone_number = request_serializer.validated_data.get("phone_number")
                if not phone_number:
                    raise ValidationError("Phone number is required.")

                buyer = get_object_or_404(
                    get_user_model().objects,
                    phone_number=phone_number,
                )
                count, _ = offer.buyer_counts.get_or_create(buyer=buyer)
                # `buyer_limit == 0` means no limit for a single buyer
                if 0 < offer.buyer_limit <= count.application_count:
                    raise ValidationError(f"Offer is out of limits for {buyer}.")
                else:
                    count.application_count += 1
                    count.save()

            case other_type:
                raise ValidationError(f"Wrong offer type: {other_type}.")  # noqa: F821

        response_serializer = self.get_serializer(offer)
        return Response(response_serializer.data)


class BuyerCountViewSet(NestedViewSetMixin, ReadOnlyModelViewSet):
    serializer_class = BuyerCountSerializer
    queryset = BuyerCount.objects.all()
    lookup_field = "id"
    parent_lookup_kwargs = {
        "offer_id": "offer__id",
    }
    filter_backends = (DjangoFilterBackend,)
    filterset_class = BuyerCountFilter
    permission_classes = (perms.ReadWritePermission(read=perms.allow_authenticated),)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return qs

        return qs.filter(buyer=user)


class RangeViewSet(ModelViewSet):
    serializer_class = RangeSerializer
    queryset = Range.objects.order_by("name")
    lookup_field = "id"
    permission_classes = (
        perms.ReadWritePermission(read=perms.allow_all, write=perms.allow_staff),
    )


class VoucherViewSet(ModelViewSet):
    serializer_class = VoucherSerializer
    queryset = Voucher.objects.order_by("-created_at")
    lookup_field = "id"
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            write=perms.allow_staff,
            apply=perms.allow_staff,
        ),
    )

    @action(methods=("post",), detail=True)
    @transaction.atomic
    def apply(self, request, **kwargs):
        voucher = self.get_object()
        if not voucher.is_active:
            raise ValidationError("Voucher can not be applied more than once.")

        current_time = timezone.now()
        if not all(
            [
                voucher.offer.is_active,
                voucher.offer.started_at <= current_time,
                voucher.offer.ended_at >= current_time,
            ]
        ):
            raise ValidationError("Offer is not available.")

        voucher.offer.application_count += 1
        voucher.offer.save()
        voucher.is_active = False
        voucher.save()
        serializer = self.get_serializer(voucher)
        return Response(serializer.data)


class LoyaltyCardViewSet(ModelViewSet):
    serializer_class = LoyaltyCardSerializer
    queryset = LoyaltyCard.objects.order_by("-created_at")
    lookup_field = "id"
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_authenticated,
            write=perms.allow_staff,
            apply=perms.allow_staff,
        ),
    )

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return qs

        return qs.filter(buyer=user)

    @action(methods=("post",), detail=True)
    @transaction.atomic
    def apply(self, request, **kwargs):
        card = self.get_object()
        if not card.is_active:
            raise ValidationError("Card is inactive.")

        current_time = timezone.now()
        if not all(
            [
                card.offer.is_active,
                card.offer.started_at <= current_time,
                card.offer.ended_at >= current_time,
            ]
        ):
            raise ValidationError("Offer is not available.")

        card.application_count += 1
        card.save()

        serializer = self.get_serializer(card)
        return Response(serializer.data)
