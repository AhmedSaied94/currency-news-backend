from rest_framework.response import Response
from oauth2_provider.models import AccessToken, RefreshToken
from rest_framework import status
from account.utils import Util
from .serializers import UserSerializer, UpdatePasswordSerializer, UserDataSerializer, resetPasswordCompleteSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect

User = get_user_model()


@api_view(['POST'])
@permission_classes([])
def sign_up(request):
    print(request.data)
    ser_user = UserSerializer(data=request.data)
    if ser_user.is_valid():
        user = ser_user.save()
        try:
            obj = AccessToken.objects.get(user__email=user.email)
            tokens = {
                'access_token': obj.token,
                'expires_in': 36000,
                'token_type': 'Bearer',
                'scope': obj.scope,
                'refresh_token': RefreshToken.objects.get(user__email=user.email).token
            }
        except Exception as e:
            tokens = {
                'msg': str(e)
            }
        # Util.send_email({
        #     'email_subject': f"Welcome to Fox Source code",
        #     'email_body': f"Hello {user.fullname} \n welcome to our site we hope you get the best experience with us \n enjoy our market place as a buyer or upload your code and become seller with us and start gaining money \n  please fill free to contact us if you faced any problem at: \n support@foxsourcecode.com",
        #     'to_email': user.email
        # })
        return Response(data=tokens, status=status.HTTP_201_CREATED)
    return Response(data=ser_user.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_profile(request):
    ser_user = UserSerializer(
        instance=request.user,
        data=request.data,
        partial=True
    )
    if ser_user.is_valid():
        ser_user.update(instance=request.user, validated_data=request.data)
        return Response(data={'success': 'updated successfully'}, status=status.HTTP_202_ACCEPTED)
    return Response(data=ser_user.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_password(request):
    serializer = UpdatePasswordSerializer(
        data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(data={'success': 'password changed successfuly'}, status=status.HTTP_200_OK)
    return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def user_details(request, **kwargs):
    try:
        if kwargs:
            ser_user = UserDataSerializer(
                instance=User.objects.get(pk=kwargs['pk']))
        else:
            if not request.user.is_authenticated:
                return Response(data={'user': 'AnonymousUser'}, status=status.HTTP_401_UNAUTHORIZED)
            print(request.user)
            ser_user = UserDataSerializer(instance=request.user)
        return Response(data=ser_user.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([])
def resetPasswordRequest(request):
    email = request.data['email']
    if User.objects.filter(email=email).exists():
        print('good')
        user = User.objects.get(email=email)
        uid64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        redirect_url = request.data['redirect_url']
        current_site = 'foxsourcecode.com'
        relative_site = reverse(
            'password-reset-check',
            kwargs={'uid64': uid64, 'token': token}
        )
        absurl = f"https://{current_site}{relative_site}"
        email_body = f"you requested an email to reset your password \n please use the link below \n {absurl}?redirect_url={redirect_url}"
        data = {
            'email_body': email_body,
            'email_subject': 'reset password request',
            'to_email': [user.email]
        }
        Util.send_email(data)

        return Response({'success': 'we sent an email to reset your password'}, status=status.HTTP_200_OK)
    return Response({'error': f"{email} isn't in our database"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([])
def resetPasswordCheck(request, uid64, token):
    redirect_url = request.GET.get('redirect_url')
    try:
        id = smart_str(urlsafe_base64_decode(uid64))
        user = User.objects.get(id=id)
        print(user)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return redirect(f"{redirect_url}?token_valid=false")

        return redirect(f"{redirect_url}?token_valid=true&uid64={uid64}&token={token}")

    except DjangoUnicodeDecodeError as error:
        return redirect(f"{redirect_url}?token_valid=false")


@api_view(['PUT'])
@permission_classes([])
def resetPasswordComplete(request):
    serializer = resetPasswordCompleteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(data={'success': 'Password reseted successfully'}, status=status.HTTP_200_OK)

    return Response(data=serializer.errors)
