from django.shortcuts import render
from .paystack import PayStack
from django.conf import settings
# Create your views here.


#Initizing PayStack package
PAYSTACK = PayStack(settings.PAY_SECRET_KEY)