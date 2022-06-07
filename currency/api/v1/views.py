from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from currency.models import *
from .serializers import *


@api_view(['GET'])
@permission_classes([])
def currency_details(request, sympol):

    home_currency = request.user.home_currency if request.user.is_authenticated else Currency.objects.get(sympol=request.GET.get(
        'home', 'EGP'))

    qs = Currency.objects.filter(sympol=sympol)
    if qs.exists():
        currency = qs.first()
        ser_currency = CurrencySerializer(instance=currency, context={
                                          'home': home_currency}).data
        # data = ser_currency
        # value = ComparisonDetails.objects.filter(
        #     normal_currency=currency,
        #     comparison__base_currency=base_currency
        # ).first().value
        # data['value'] = value
        return Response(
            data=ser_currency,
            status=status.HTTP_200_OK
        )
    else:
        return Response(data={'error': 'currency not found in our database'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([])
def get_all_currencies(request, type):

    instance = Currency.objects.filter(currency_type__name=type)
    try:
        home_currency = request.user.home_currency if request.user.is_authenticated and hasattr(request.user, 'home_value') else Currency.objects.get(
            sympol=request.GET.get('home', 'USD'))

        ser_data = AllCurrencySerializer(
            instance=instance,
            many=True,
            context={"home": home_currency}
        ).data

        return Response(
            data=ser_data,
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            data={'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([])
def get_all_sympols(request):
    sympols = CurrencySympolsSerializer(
        instance=Currency.objects.all(),
        many=True
    )
    return Response(data=sympols.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def handle_favorites(request, **kwargs):
    currency = get_object_or_404(Currency, pk=kwargs['pk'])
    favorites, created = UserFavorite.objects.get_or_create(user=request.user)
    data = {}
    if kwargs['operation'] == 'add':
        favorites.currencies.add(currency)
        data = {'success': 'item added to your favorites'}
    elif kwargs['operation'] == 'remove':
        favorites.currencies.remove(currency)
        data = {'success': 'item removed your favorites'}
    return Response(data=data, status=status.HTTP_200_OK)
