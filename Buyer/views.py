from multiprocessing import context
from typing import Generic
from .models import Customer
from django.contrib.auth import authenticate
import pyotp
import base64
import time
from twilio.rest import Client
# api libs
from rest_framework import status 
from rest_framework.response import Response
from Buyer import serializers
from rest_framework.decorators import APIView,api_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from rest_framework.generics import GenericAPIView # IMP Class for api in swagger 

from rest_framework.generics import GenericAPIView


#import token
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.

# @api_view(['GET','POST'])
# def add_new_buyer(request): 
#     if request.method == 'POST':
#        data=request.data
#        buy=Buyer_Info()
#        buy.First_Name=data['First_Name']
#        buy.Last_Name=data['Last_Name']
#        buy.Email=data['Email']
#        buy.Password=data['Password']
#        buy.save()
#        return Response({'msg':'buyer add'})
#     else:
#        return Response({'msg':'add buyer','format':{
#         "First_Name": "First name of a buyer",
#         "Last_Name": "last Name of a Buyer",
#         "Email": "email_id",
#         "Password": "Password"
#  }})


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# class add_new_buyer(generics.CreateAPIView):
#    queryset=Buyer_Info
#    serializer_class=serializers.BuyerSerializer

# class update_buyer(generics.RetrieveUpdateDestroyAPIView):
#    queryset=Buyer_Info
#    serializer_class=serializers.BuyerSerializer

# class views_all_buyer(generics.ListAPIView):
#    queryset=Buyer_Info.objects.all()
#    serializer_class=serializers.BuyerSerializer

# class CustomerRegistration(APIView):
#    def post(self,request,format=None):
#       serializer=serializers.CustomerRegistrationSerializer(data=request.data)
#       if serializer.is_valid(raise_exception=True):
#          user=serializer.save()
#          return Response({'msg':'Registration Success'},status=status.HTTP_201_CREATED )
#       return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

base32secret = pyotp.random_base32()
totp = pyotp.TOTP(base32secret,interval=120)

class CustomerRegistration(generics.CreateAPIView):
   queryset=Customer
   serializer_class=serializers.CustomerRegistrationSerializer

class CustomerLoginView(GenericAPIView):
   serializer_class=serializers.CustomerloginSerializer
   def post(self,request,format=None):
      serializer=serializers.CustomerloginSerializer(data=request.data)
      if serializer.is_valid(raise_exception=True):
         email=serializer.data.get('email')
         password=serializer.data.get('password')
         user=authenticate(email=email,password=password)
         # print('OTP code:', totp.now())
         # account_sid = "AC0a30640b4a04fa3ab7a22f387bd7e460"
         # auth_token = "da9f185cd2a2fef9e7d8ca7e15d7847a"
         # client = Client(account_sid, auth_token)
         # message = client.messages.create(
         #             body="your otp is "+str(totp.now()),
         #             from_='+14245776994',
         #             to='+919165165814'
         #         )
         # print(message.sid)
         if user is not None:
            token=get_tokens_for_user(user)
            return Response({"Token":token,'mag':'Login Success'},status=status.HTTP_200_OK)
         else:
            return Response({'errors':{'non_field_errors':['Email or password is not Valid']}},status=status.HTTP_404_NOT_FOUND)

class Chk_otp(APIView):
   def post(self,request,format=None):
      serializer=serializers.Chk_opt_Seriliser(data=request.data)
      if serializer.is_valid(raise_exception=True):
         otp=serializer.data.get('enter_otp')
         veryfy_otp=totp.verify(otp)
         if veryfy_otp == True:
            return Response({'msg':'verifyed'},status=status.HTTP_200_OK)
         return Response({'mag':'enter the valid otp'},status=status.HTTP_401_UNAUTHORIZED)

class CustomerProfileView(APIView):
   permission_classes=[IsAuthenticated]
   def get(self,request,format=None):
      serializer=serializers.CustomerProfileView(request.user)
      base32secret = pyotp.random_base32()
      return Response(serializer.data,status=status.HTTP_200_OK)

class CustomerChangePassword(APIView):
   permission_classes=[IsAuthenticated]
   def post(self,request,format=None):
      serializer=serializers.CustomerChangePasswordSerializer(data=request.data, context={'user':request.user})
      if serializer.is_valid(raise_exception=True):
         return Response({'msg':'Password Changed Successfully'},status=status.HTTP_200_OK)
      return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class SendPasswordRestEmailView(APIView):
   def post(self,request,format=None):
      serializer=serializers.SendPasswordRestEmailSerializer(data=request.data)
      if serializer.is_valid(raise_exception=True):
           return Response({'mag':'we send a Reset password link on your email'})
      return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class CustomerPasswordResetView(APIView):
   def post(self,request,uid,token,format=None):
      serializer=serializers.CustomerPasswordRestSerializer(data=request.data, context={'uid':uid,'token':token})
      if serializer.is_valid(raise_exception=True):
         return Response({'msg':'Password Reset Successfully'},status=status.HTTP_200_OK)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


