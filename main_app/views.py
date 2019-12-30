from datetime import date
import math
import random

import requests
from rest_framework.authtoken.models import Token

from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Employee, Otp
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from channel.models import channel_model
from video.models import video_class

from pymongo import MongoClient


def logger_history_function(username, activity):
    flag = 0
    print('calll')
    if User.objects.filter(username=username):
        print('username found in database')
        flag = 1

    if Token.objects.filter(key=username):
        print('Token found in database')
        token = Token.objects.get(key=username)
        username = token.user.username
        flag = 1

    if flag == 1:
        client = MongoClient('mongodb://127.0.0.1:27017')
        print('database connection successfully')
        db = client.geniobits
        mycollection = db[username]
        today = date.today()
        today = str(today)
        # today = '2019-12-31'
        print('today date : ' + today)
        print(username)
        if username in db.list_collection_names():
            print('usename found in document ')
            result = mycollection.update({
                'date': today
            }, {
                '$push': {
                    "activity": activity,
                }
            })
            print(str(result['updatedExisting']) + ' date not found create new database')
            if not result['updatedExisting']:
                mycollection.insert({
                    'user': username,
                    "activity": [activity],
                    "date": today
                })
                print('new document create successful')
        else:
            print('usename not found in document')
            mycollection.insert({
                'user': username,
                "activity": [activity],
                "date": today
            })
    else:
        print('username not found')
    return


@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    if request.method == 'GET':
        username = request.POST.get('username')
        activity = request.POST.get('activity')
        logger_history_function(username, activity)
    return Response({'message': 'okk'})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if Token.objects.filter(user=user).exists():
                token = Token.objects.get(user=user)
                token.delete()
            token = Token.objects.create(user=user)
            user = User.objects.get(username=token.user.username)
            print(user.username)
            emp_object = Employee.objects.get(user=user)
            if not emp_object.is_verify:
                message = 'user register but mobile number not verify '
                token = token.key
                error = 'False'
                data = {'message': message, 'error': error, 'token': token}
                logger_history_function(username, message)
                return Response(data)
            else:
                message = 'user login successfully'
                token = token.key
                error = 'False'
                data = {'message': message, 'error': error, 'token': token}
                logger_history_function(username, message)
                return Response(data)
        else:
            data = {'message': 'username and password not match ', 'error': 'True', 'token': 'empty'}
            print(data)
            return Response(data)


def sendPostRequest(reqUrl, apiKey, secretKey, useType, phoneNo, senderId, textMessage):
    req_params = {
        'apikey': apiKey,
        'secret': secretKey,
        'usetype': useType,
        'phone': phoneNo,
        'message': textMessage,
        'senderid': senderId
    }
    return requests.post(reqUrl, req_params)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        if password == re_password:
            if User.objects.filter(username=username).exists():
                message = 'username already exist!! try another username'
                token = 'empty'
                error = 'True'
            else:
                if not Employee.objects.filter(phone_no=phone_no).exists():
                    user = User.objects.create_user(username, email, password)
                    user.save()
                    emp_obj = Employee(user=user, phone_no=phone_no)
                    emp_obj.save()
                    login(request, user)
                    token = Token.objects.create(user=user)
                    print(token.key)
                    digits = "0123456789"
                    OTP = ""
                    # duration = (datetime.now().time() - Otp.time_generate_otp);
                    for i in range(6):
                        OTP += digits[math.floor(random.random() * 10)]
                    if not Otp.objects.filter(user=user):
                        obj = Otp(user=user, attempts=5, OTP=OTP)
                        obj.save()
                    obj = Otp.objects.get(user=user)
                    if obj.get_time_diff() > 3600:
                        obj = Otp(user=user, attempts=5, OTP=OTP)
                        obj.save()
                    text_message = 'your OTP is : ' + OTP

                    URL = 'https://www.sms4india.com/api/v1/sendCampaign'
                    response = sendPostRequest(URL, '600XK5ONNJVYPIO66ZHUTX4PXBCGA7NT', '9TFM3V54JHDYK127', 'stage',
                                               '+91' + phone_no, '012345', text_message)
                    print(response.text)
                    message = 'user registration successful'
                    token = token.key
                    error = 'False'
                else:
                    message = 'phone number already register with another account'
                    token = 'empty'
                    error = 'True'

        else:
            message = 'password and re_enter password not match'
            token = 'empty'
            error = 'True'

    data = {'message': message, 'error': error, 'token': token}
    logger_history_function(username, message)
    return Response(data)


#
# @api_view(['POST'])
# @login_required
# def create_token(request,user):
#     # user = User.objects.get(username=request.data.get('username'))
#     return HttpResponse({'token': token.key})
#
#


def logout(request):
    auth_logout(request)

    return render(request, "main_app/home.html")


@api_view(['POST'])
@permission_classes([AllowAny])
def profileinfo(request):
    if request.method == "POST":
        token = request.POST.get('token')
        if Token.objects.filter(key=token).exists():
            token = Token.objects.get(key=token)
            message = 'token present'
            username = token.user.username
            email = token.user.email
            phone_no = token.user.employee.phone_no
            error = 'False'
            token = 'empty'
            data = {'message': message, 'username': username, 'email': email, 'phone_no': phone_no, 'error': error,
                    'token': token}
            logger_history_function(username, 'user get profile information')
            return Response(data)
        else:
            message = 'invalid token '
            username = 'empty'
            email = 'empty'
            phone_no = 'empty'
            token = 'empty'
            error = 'True'
            data = {'message': message, 'username': username, 'email': email, 'phone_no': phone_no, 'error': error,
                    'token': token}
            return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_opt(request):
    if request.method == "POST":
        token = request.POST.get('token')
        otp = request.POST.get('otp')
        if Token.objects.filter(key=token):
            token_obj = Token.objects.get(key=token)
            print(token_obj.key)
            user = token_obj.user
            print(user.username)
            otp_object = Otp.objects.get(user=user)
            print(otp_object.OTP)
            print(otp_object.attempts)
            print(otp)
            if otp_object.get_time_diff() > 1800:
                message = 'Otp expired try later'
                username = 'empty'
                phone_no = 'empty'
                error = 'True'
                data = {'message': message, 'username': username, 'phone_no': phone_no, 'error': error, }
                logger_history_function(token, message)
                return Response(data)
            elif otp_object.attempts < 0:
                message = 'you try more than 5 time'
                username = 'empty'
                phone_no = 'empty'
                error = 'True'
                data = {'message': message, 'username': username, 'phone_no': phone_no, 'error': error, }
                logger_history_function(token, message)
                return Response(data)
            elif int(otp_object.OTP) == int(otp):
                otp_object.is_verify = "True"
                username = user.username
                message = "Otp successfully verify " + username
                phone_no = user.employee.phone_no
                error = 'False'
                otp_object.is_verify = "True"
                data = {'message': message, 'username': username, 'phone_no': phone_no, 'error': error}
                logger_history_function(token, message)
                return Response(data)
            else:
                otp_object.attempts = otp_object.attempts - 1
                otp_object.save()
                username = user.username
                message = "Otp not match try later"
                phone_no = user.employee.phone_no
                error = 'True'
                data = {'message': message, 'username': username, 'phone_no': phone_no, 'error': error}
                logger_history_function(token, message)
                return Response(data)
        else:

            message = 'Token Not verify'
            username = 'empty'
            phone_no = 'empty'
            error = 'True'
            data = {'message': message, 'username': username, 'phone_no': phone_no, 'error': error, }
            return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def mobile_no_change(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        phone_no = request.POST.get('phone_no')
        if Token.objects.filter(key=token).exists:
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if Employee.objects.filter(user=user).exists():
                obj = Employee.objects.get(user=user)
                phone_no_old = obj.phone_no
                if phone_no != phone_no_old:
                    emp_obj = Employee.objects.get(user=user)
                    emp_obj.phone_no = phone_no
                    emp_obj.is_verify = False
                    emp_obj.save
                    error = "False"
                    message = "User phone number is updated.Phone number not verify please verify it"
                    token = token
                    data = {"error": error, "message": message, "token": token}
                    logger_history_function(token, message)
                    return Response(data)
                else:
                    error = "False"
                    message = "User phone number is already correct."
                    token = token
                    data = {"error": error, "message": message, "token": token}
                    logger_history_function(token, message)
                    return Response(data)
        error = "True"
        message = "Token is not present or phone_no is not present."
        token = "empty"
        data = {"error": error, "message": message, "token": token}
        return Response(data)
    return Response()


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_user(request):
    data = {}
    if request.method == "POST":
        token = request.POST.get('token')
        if Token.objects.filter(key=token):
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            print(user.username)
            # employee = Employee.objects.get(user=user)
            if not user.employee.channel_id == 0:
                if channel_model.objects.filter(id=user.employee.channel_id):
                    channel_obj = channel_model.objects.get(id=user.employee.channel_id)
                    channel_id = channel_obj.id
                    channel = channel_model.objects.get(id=channel_id)
                    video_ids = channel.video_id
                    print(video_ids)
                    video_list = video_ids.split(",")
                    print(video_list)
                    video_list = [s for s in video_list if s.isdigit()]
                    for id in video_list:
                        print(id)
                        if video_class.objects.filter(id=id):
                            video_obj = video_class.objects.get(id=id)
                            video_obj.delete()
                        else:
                            print(f'{id},video not found')

                    message = 'channel delete successful with user'
                    error = 'False'
                    data = {'message ': message, 'error': error}
                    logger_history_function(token, message)
                    channel.delete()
                    user.delete()
                else:
                    message = 'channel exit but not found in database'
                    error = 'False'
                    data = {'message': message, 'error': error}
                    logger_history_function(token, message)
                    user.delete()
            else:
                user.delete()
                message = 'user delete succssfully user has no any channel found'
                error = 'False'
                data = {'message': message, 'error': error}
                logger_history_function(token, message)
        else:
            message = 'token not valid'
            error = 'True'
            data = {'message': message, 'error': error}
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_reset_otp(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if Employee.objects.filter(user=user).exists():
                emp_obj = Employee.objects.get(user=user)
                phone_no = emp_obj.phone_no
                digits = "0123456789"
                digit = "123456789"
                OTP = ""
                # duration = (datetime.now().time() - Otp.time_generate_otp);
                for i in range(6):
                    if i == 0:
                        OTP += digit[math.floor(random.random() * 10)]
                    else:
                        OTP += digits[math.floor(random.random() * 10)]
                if Otp.objects.filter(user=user).exists():
                    otp_obj = Otp.objects.get(user=user)
                    otp_obj.delete()
                obj = Otp(user=user, attempts=5, OTP=OTP)
                obj.save()
                error = 'False'
                message = 'otp sent successfully'
                token = 'empty'
                data = {'error': error, 'message': message, 'token': token}
                logger_history_function(username, message)
                return Response(data)
            error = 'True'
            message = 'username my be admin'
            token = 'empty'
            data = {'error': error, 'message': message, 'token': token}
            logger_history_function(username, message)
            return Response(data)
        error = 'True'
        message = 'user not exists'
        token = 'empty'
        data = {'error': error, 'message': message, 'token': token}
        logger_history_function(username, message)
        return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_reset(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        otp = request.POST.get('otp')
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if Otp.objects.filter(user=user).exists():
                otp_obj = Otp.objects.get(user=user)
                otp_in_table = otp_obj.OTP
                print("-----------------------------------")
                print(otp_in_table)
                print(otp)
                print("-----------------------------------")
                if otp_in_table == int(otp) and otp_obj.attempts > 0:
                    otp_obj.delete()
                    if Token.objects.filter(user=user).exists():
                        token_obj = Token.objects.get(user=user)
                    else:
                        token_obj = Token.objects.create(user=user)
                    error = 'False'
                    message = 'otp varify successfully'
                    token = token_obj.key
                    data = {'error': error, 'message': message, 'token': token}
                    logger_history_function(username, message)
                    return Response(data)
                otp_obj.attempts -= 1
                otp_obj.save()
                if otp_obj.attempts <= 0:
                    digits = "0123456789"
                    digit = "123456789"
                    OTP = ""
                    # duration = (datetime.now().time() - Otp.time_generate_otp);
                    for i in range(6):
                        if i == 0:
                            OTP += digit[math.floor(random.random() * 10)]
                        else:
                            OTP += digits[math.floor(random.random() * 10)]
                    if Otp.objects.filter(user=user).exists():
                        otp_obj = Otp.objects.get(user=user)
                        otp_obj.delete()
                    obj = Otp(user=user, attempts=5, OTP=OTP)
                    obj.save()
                    error = 'True'
                    message = 'new otp generated due to max wrong attempts'
                    token = 'empty'
                    data = {'error': error, 'message': message, 'token': token}
                    logger_history_function(username, message)
                    return Response(data)
                error = 'True'
                message = 'wrong attempts'
                token = 'empty'
                data = {'error': error, 'message': message, 'token': token}
                logger_history_function(username, message)
                return Response(data)
            error = 'True'
            message = 'first tap on send otp.'
            token = 'empty'
            data = {'error': error, 'message': message, 'token': token}
            logger_history_function(username, message)
            return Response(data)
        error = 'True'
        message = 'invalid username'
        token = 'empty'
        data = {'error': error, 'message': message, 'token': token}
        return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_change(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        token = request.POST.get('token')
        if password == re_password:
            if Token.objects.filter(key=token).exists():
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
                if user.password == password:
                    error = 'True'
                    message = 'password can\'t be old one'
                    token = token
                    data = {'error': error, 'message': message, 'token': token}
                    logger_history_function(token, message)
                    return Response(data)
                user.password = password
                user.save()
                error = 'False'
                message = 'password reset successfully'
                token = token
                data = {'error': error, 'message': message, 'token': token}
                logger_history_function(token, message)
                return Response(data)
            error = 'True'
            message = 'user is invalid'
            token = 'empty'
            data = {'error': error, 'message': message, 'token': token}
            return Response(data)
        error = 'True'
        message = 'password not match'
        token = 'empty'
        data = {'error': error, 'message': message, 'token': token}
        return Response(data)
