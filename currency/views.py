import mimetypes

from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from .models import *
from currency.api.v1.serializers import CurrencySerializer, ComparisonDetailsSerializer
import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

ar_curs_sympols = ['EGP', 'AED', 'IQD', 'BHD', 'QAR', 'OMR', 'KWD', 'JOD',
                   'LBP', 'LYD', 'DZD', 'MAD', 'SAR', 'YER', 'TRY', 'SDG', 'TND']
bases = ["AED", "CAD", "CHF", "CNY", "EUR",
         "GBP", "JPY", "KWD", "OMR", "QAR", "SAR", "USD"]

# Create your views here.


@xframe_options_exempt
def iframe(request):
    return render(request, 'currency/iframe.js', content_type='text/javascript')


def bases_to_arabic(request):
    # data = {}
    # for base in bases:
    #     data[base] = []
    #     for cur in ar_curs_sympols:
    #         com = ComparisonDetails.objects.filter(
    #             comparison__base_currency__sympol=base,
    #             normal_currency__sympol=cur
    #         ).order_by('-comparison__date').first()
    #         data[base].append(ComparisonDetailsSerializer(instance=com).data)
    data = []
    for cur in ar_curs_sympols:
        com = ComparisonDetails.objects.filter(
            comparison__base_currency__sympol='USD',
            normal_currency__sympol=cur
        ).order_by('-comparison__date').first()
        data.append(
            ComparisonDetailsSerializer(
                instance=com).data

        )

    return render(
        request,
        'currency/bases_script.js',
        context={'data': data, "bases": bases},
        content_type='text/javascript'
    )


@api_view(['POST'])
@permission_classes([])
def frame_data(request):
    data = []
    for cur in ar_curs_sympols:
        data.append(
            ComparisonDetails.objects.filter(
                comparison__base_currency__sympol=request.data['sympol'],
                normal_currency__sympol=cur
            ).order_by('-comparison__date').first()
        )
    ser_data = ComparisonDetailsSerializer(instance=data, many=True)
    return Response(data=ser_data.data, status=status.HTTP_200_OK)
