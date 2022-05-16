from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from currency.models import *
from .serializers import *


@api_view(['GET'])
def currency_details(request, pk):

    base_currency = request.user.base_currency

    qs = Currency.objects.filter(pk=pk)
    if qs.exists():
        currency = qs.first()
        ser_currency = CurrencySerializer(instance=currency).data
        data = ser_currency
        value = ComparisonDetails.objects.filter(
            normal_currency=currency,
            comparison__base_currency=base_currency
        ).first().value
        data['value'] = value
        return Response(
            data=data,
            status=status.HTTP_200_OK
        )
    else:
        return Response(data={'error': 'currency not found in our database'}, status=status.HTTP_404_NOT_FOUND)


def get_all_currencies(request):
    try:
        base_currency = request.user.base_currency

        ser_data = CurrencySerializer(
            instance=Currency.objects.all(),
            many=True
        ).data

        currencies = ser_data
        for cur in currencies:
            qs = ComparisonDetails.objects.filter(
                normal_currency=cur,
                comparison__base_currency=base_currency
            ).first()
            value = qs.value
            cur['value'] = value
        return Response(
            data=currencies,
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            data={'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
