from urllib import response
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from currency.models import *
from .serializers import *
import requests


@api_view(['GET'])
@permission_classes([])
def currency_details(request, sympol):

    qs = Currency.objects.filter(sympol=sympol)
    if qs.exists():
        currency = qs.first()
        if currency.currency_type.base_currency:
            home_currency = request.user.home_currency if request.user.is_authenticated else Currency.objects.get(sympol=request.GET.get(
                'home', 'EGP'))
            context = {'home': home_currency}
        else:
            context = {'base': Currency.objects.get(
                sympol=request.GET.get('base', 'USD'))}

        ser_currency = CurrencySerializer(
            instance=currency, context=context).data
        # data = ser_currency
        # value = ComparisonDetails.objects.filter(
        #     normal_currency=currency,
        #     comparison__base_currency=base_currency
        # ).first().value
        # data['value'] = value
        trequest = requests.get(
            f'https://api.twitter.com/2/tweets/search/recent?query={currency.sympol}', headers={'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAHjkdQEAAAAAbvEaPCN%2BULMVVjjtPU9nAyMLPmk%3DSyCnWxnAxYsaoefpXztHEDF6JRjd7X56GdsldCfEuWMkpoEnJw'})
        data = trequest.json()

        return Response(
            data={**ser_currency, "tweets": data['data']},
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


@api_view(['POST'])
def handle_favorites(request):
    currency = get_object_or_404(Currency, pk=request.data['id'])
    favorites, created = UserFavorite.objects.get_or_create(user=request.user)
    data = {}
    if request.data['oper'] == 'add':
        if currency not in favorites.currencies.all():
            favorites.currencies.add(currency)
            data = {'data': {'success': 'item added to your favorites'},
                    'status': status.HTTP_200_OK}
        else:
            data = {
                'data': {'error': 'this currency already in your favorites'},
                'status': status.HTTP_400_BAD_REQUEST
            }
    elif request.data['oper'] == 'remove':
        if currency in favorites.currencies.all():
            favorites.currencies.remove(currency)
            data = {'data': {'success': 'currency removed your favorites'},
                    'status': status.HTTP_200_OK}
        else:
            data = {
                'data': {'error': 'this currency is not in your favorites'},
                'status': status.HTTP_400_BAD_REQUEST
            }
    else:
        data = {
            'data': {'error': 'invalid operation'},
            'status': status.HTTP_400_BAD_REQUEST
        }
    return Response(data=data['data'], status=data['status'])


@api_view(['GET'])
@permission_classes([])
def get_news(request, **kwargs):
    if kwargs['filter'] == 'all':
        instance = News.objects.all()
        ser_news = NewsSerializer(instance=instance, many=True)

    else:
        instance = get_object_or_404(News, pk=kwargs['pk'])
        ser_news = NewsSerializer(
            instance=instance, context={'addtional': True})
    return Response(data=ser_news.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def handle_likes(request):
    news = get_object_or_404(News, pk=request.data['id'])
    likes, created = Like.objects.get_or_create(news=news)
    response = {}
    qs = likes.user.filter(pk=request.user.id)

    if request.data['oper'] == 'like':
        if qs.exists():
            response = {'data': {'error': 'you already liked this news'},
                        'status': status.HTTP_403_FORBIDDEN}
        else:
            likes.user.add(request.user)
            response = {
                'data': {'success': 'you liked this news'},
                'status': status.HTTP_200_OK
            }
    elif request.data['oper'] == 'unlike':
        if qs.exists():
            likes.user.remove(request.user)
            response = {
                'data': {'success': 'you unliked this news'},
                'status': status.HTTP_200_OK
            }
        else:
            response = {
                'data': {'error': "you already don't like this news"},
                'status': status.HTTP_403_FORBIDDEN
            }
    else:
        response = {
            'data': {'error': 'unsupported operation'},
            'status': status.HTTP_400_BAD_REQUEST
        }
    return Response(data=response['data'], status=response['status'])


@api_view(['POST'])
def handle_comments(request):
    response = {}
    if request.data['oper'] == 'create':
        data = {**request.data, 'user': request.user.id}
        ser_comment = CommentSerialzer(data=data)
        if ser_comment.is_valid():
            ser_comment.save()
            response = {
                'data': ser_comment.data,
                'status': status.HTTP_200_OK
            }
        else:
            response = {
                'data': ser_comment.errors,
                'status': status.HTTP_400_BAD_REQUEST
            }
    elif request.data['oper'] == 'delete':
        comment = get_object_or_404(Comment, pk=request.data['id'])
        if request.user != comment.user:
            response = {
                'data': {'error': "you cant't perform this action"},
                'status': status.HTTP_403_FORBIDDEN
            }
        else:
            comment.delete()
        response = {
            'data': {'success': 'comment deleted successfully'},
            'status': status.HTTP_200_OK
        }
    else:
        response = {
            'data': {'error': 'unsupported operation'},
            'status': status.HTTP_400_BAD_REQUEST
        }
    return Response(data=response['data'], status=response['status'])


@api_view(['POST'])
@permission_classes([])
def calculator(request):
    first_currency = Currency.objects.get(
        sympol=request.data['first_currency'])
    second_currency = Currency.objects.get(
        sympol=request.data['second_currency'])
    data = {}
    if first_currency.currency_type.base_currency:
        value = ComparisonDetails.objects.filter(
            comparison__base_currency=first_currency,
            normal_currency=second_currency,
        ).order_by('-comparison__date').first().bye_value
        data = {'result': str(
            round(value*float(request.data['amount']), 2)) + f' {second_currency.sympol}'}
    elif second_currency.currency_type.base_currency:
        value = ComparisonDetails.objects.filter(
            comparison__base_currency=second_currency,
            normal_currency=first_currency,
        ).order_by('-comparison__date').first().bye_value
        data = {'result': str(
            round(1/value*float(request.data['amount']), 2)) + f' {second_currency.sympol}'}
    else:
        crequest = requests.get(
            f'https://api.metalpriceapi.com/v1/latest?api_key=6d738f6d27f371d626809920ef29112f&base={first_currency.sympol}&currencies={second_currency.sympol}')
        res = crequest.json()
        print(res)
        data = {'result': str(round(
            float(res['rates'][second_currency.sympol]) *
            float(request.data['amount']), 2
        )) + f' {second_currency.sympol}'}
    return Response(data=data, status=status.HTTP_200_OK)
