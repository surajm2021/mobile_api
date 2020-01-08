from datetime import date, datetime

import math
import random

import requests
from rest_framework import authentication
from rest_framework.authtoken.models import Token

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Employee, Otp, UserManager, User
from django.contrib.auth import authenticate, login
from .backends import MyAuthBackend
from channel.models import channel_model
from video.models import video_class
from pymongo import MongoClient


def logger_history_function(username, activity):
    flag = 0
    # print('call')
    if User.objects.filter(username=username):
        # print('username found in database')
        flag = 1

    if Token.objects.filter(key=username):
        # print('Token found in database')
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
        # print('today date : ' + today)
        activity_and_time = str(datetime.now()) + '    ' + activity
        # print(username)
        if username in db.list_collection_names():
            # print('usename found in document ')
            result = mycollection.update({
                'date': today
            }, {
                '$push': {
                    "activity": activity_and_time,
                }
            })
            # print(str(result['updatedExisting']) + ' date not found create new database')
            if not result['updatedExisting']:
                mycollection.insert({
                    'user': username,
                    "activity": [activity_and_time],
                    "date": today
                })
                # print('new document create successful')
        else:
            # print('usename not found in document')
            mycollection.insert({
                'user': username,
                "activity": [activity_and_time],
                "date": today
            })
    else:
        print('username not found')
    return


def delete_user_mongo_history(username):
    client = MongoClient('mongodb://127.0.0.1:27017')
    print('database connection successfully')
    db = client.geniobits
    mycol = db[username]
    mycol.drop()


@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    if request.method == 'GET':
        username = request.POST.get('username')
        activity = request.POST.get('activity')
        print(datetime.now())
        # logger_history_function(username, activity)
        # video_logger('3','11','dislike','python,php')
    return Response({'message': 'okk'})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = MyAuthBackend.authenticate(request, username=username, password=password)
        if user is not None:
            # login(request, user)
            print(MyAuthBackend.get_user(request, user.id))
            if Token.objects.filter(user=user).exists():
                token = Token.objects.get(user=user)
                token.delete()
            token = Token.objects.create(user=user)
            user = User.objects.get(username=token.user.username)
            print(user.username)
            if not user.is_verify:
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
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        tags = request.POST.get('tags')
        if password == re_password:
            if User.objects.filter(phone=phone).exists() or phone is None:
                message = 'phone no already exist or empty!! try another phone number'
                token = 'empty'
                error = 'True'
            elif User.objects.filter(email=email).exists():
                message = 'email already exist!! try another email id '
                token = 'empty'
                error = 'True'
            elif not User.objects.filter(username=username).exists():
                user = User.objects.create_new_user(phone, username, email, tags, password)
                user.save()
                # login(request, user)

                token = Token.objects.create(user=user)
                print(token.key)
                digits = "0123456789"
                OTP = ""
                for i in range(6):
                    OTP += digits[math.floor(random.random() * 10)]
                if not Otp.objects.filter(user=user):
                    obj = Otp(user=user, attempts=5, OTP=OTP)
                    obj.save()
                obj = Otp.objects.get(user=user)
                if obj.get_time_diff() > 3600:
                    obj = Otp(user=user, attempts=5, OTP=OTP)
                    obj.save()
                text_message = 'Hi,Your account verification code is  : '+OTP+'  Enter this code within 300 seconds to verify your account.Thanks'

                URL = 'https://www.sms4india.com/api/v1/sendCampaign'
                response = sendPostRequest(URL, '600XK5ONNJVYPIO66ZHUTX4PXBCGA7NT', '9TFM3V54JHDYK127', 'stage',
                                           '+91' + phone, '012345', text_message)
                print(response.text)
                message = 'user registration successful'
                token = token.key
                error = 'False'
            else:
                message = 'username already exist !! try another username'
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


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    if request.method == "POST":
        token = request.POST.get('token')
        if Token.objects.filter(key=token).exists():
            token_obj = Token.objects.get(key=token)
            # print(token_obj.key)
            token_obj.delete()
            message = 'User logout successful'
            error = 'False'
            data = {'message': message, 'error': error, 'token': token}
            return Response(data)

        else:
            message = 'User already logout'
            error = 'True'
            data = {'message': message, 'error': error, 'token': token}
            return Response(data)


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
            phone = token.user.phone
            error = 'False'
            token = 'empty'
            data = {'message': message, 'username': username, 'email': email, 'phone': phone, 'error': error,
                    'token': token}
            logger_history_function(username, 'user get profile information')
            return Response(data)
        else:
            message = 'invalid token '
            username = 'empty'
            email = 'empty'
            phone = 'empty'
            token = 'empty'
            error = 'True'
            data = {'message': message, 'username': username, 'email': email, 'phone': phone, 'error': error,
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
            if user.is_verify:
                message = 'phone number already verify no need to verify again'
                username = user.username
                phone = user.phone
                error = 'Flase'
                data = {'message': message, 'username': username, 'phone': phone, 'error': error, }
                logger_history_function(token, message)
                return Response(data)
            elif not Otp.objects.filter(user=user):
                message = 'user has no longer otp found. firsr create otp'
                username = 'empty'
                phone = 'empty'
                error = 'False'
                data = {'message': message, 'username': username, 'phone': phone, 'error': error, }
                logger_history_function(token, message)
                return Response(data)
            otp_object = Otp.objects.get(user=user)
            print(otp_object.OTP)
            print(otp_object.attempts)
            print(otp)
            if otp_object.get_time_diff() > 1800:
                message = 'Otp expired try later'
                username = 'empty'
                phone = 'empty'
                error = 'True'
                data = {'message': message, 'username': username, 'phone': phone, 'error': error, }
                logger_history_function(token, message)
                return Response(data)
            elif otp_object.attempts < 0:
                message = 'you try more than 5 time'
                username = 'empty'
                phone = 'empty'
                error = 'True'
                data = {'message': message, 'username': username, 'phone': phone, 'error': error, }
                logger_history_function(token, message)
                return Response(data)
            elif int(otp_object.OTP) == int(otp):
                otp_object.is_verify = "True"
                username = user.username
                message = "Otp successfully verify " + username
                phone = user.phone
                error = 'False'
                otp_object.is_verify = "True"
                data = {'message': message, 'username': username, 'phone': phone, 'error': error}
                user.is_verify = True
                user.save()
                otp_object.delete()
                logger_history_function(token, message)
                return Response(data)
            else:
                otp_object.attempts = otp_object.attempts - 1
                otp_object.save()
                username = user.username
                message = "Otp not match try later"
                phone = user.phone
                error = 'True'
                data = {'message': message, 'username': username, 'phone': phone, 'error': error}
                logger_history_function(token, message)
                return Response(data)
        else:

            message = 'Token Not verify'
            username = 'empty'
            phone = 'empty'
            error = 'True'
            data = {'message': message, 'username': username, 'phone': phone, 'error': error, }
            return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def mobile_no_change(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        phone = request.POST.get('phone')
        print(Token.objects.filter(key=token).count())
        if Token.objects.filter(key=token).count()==1:
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            phone_old = user.phone
            if phone != phone_old:
                user.phone = phone
                user.is_verify = False
                user.save
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
        message = "Token is not present or phone is not present."
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
            # employee = Employee.objects.get(user=
            print(user.channel_id)
            if not user.channel_id is None:
                if channel_model.objects.filter(id=user.channel_id):
                    channel_obj = channel_model.objects.get(id=user.channel_id)
                    channel_id = channel_obj.id
                    channel = channel_model.objects.get(id=channel_id)
                    video_ids = channel.video_id
                    # print(video_ids)
                    video_list = video_ids.split(",")
                    # print(video_list)
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
                    delete_user_mongo_history(user.username)
                    user.delete()
                else:
                    message = 'channel exit but not found in database'
                    error = 'False'
                    data = {'message': message, 'error': error}
                    logger_history_function(token, message)
                    delete_user_mongo_history(user.username)
                    user.delete()
            else:
                delete_user_mongo_history(user.username)
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

#
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def resend_reset_otp(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         if User.objects.filter(username=username).exists():
#             user = User.objects.get(username=username)
#             if Employee.objects.filter(user=user).exists():
#                 emp_obj = Employee.objects.get(user=user)
#                 phone = emp_obj.phone
#                 # duration = (datetime.now().time() - Otp.time_generate_otp);
#                 digits = "0123456789"
#                 OTP = ""
#                 # duration = (datetime.now().time() - Otp.time_generate_otp);
#                 for i in range(6):
#                     OTP += digits[math.floor(random.random() * 10)]
#                 if Otp.objects.filter(user=user).exists():
#                     otp_obj = Otp.objects.get(user=user)
#                     otp_obj.delete()
#                 obj = Otp(user=user, attempts=5, OTP=OTP)
#                 obj.save()
#                 error = 'False'
#                 message = 'otp sent successfully'
#                 token = 'empty'
#                 data = {'error': error, 'message': message, 'token': token}
#                 logger_history_function(username, message)
#                 return Response(data)
#             error = 'True'
#             message = 'username my be admin'
#             token = 'empty'
#             data = {'error': error, 'message': message, 'token': token}
#             logger_history_function(username, message)
#             return Response(data)
#         error = 'True'
#         message = 'user not exists'
#         token = 'empty'
#         data = {'error': error, 'message': message, 'token': token}
#         logger_history_function(username, message)
#         return Response(data)

#
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def verify_otp_reset(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         otp = request.POST.get('otp')
#         if User.objects.filter(username=username).exists():
#             user = User.objects.get(username=username)
#             if Otp.objects.filter(user=user).exists():
#                 otp_obj = Otp.objects.get(user=user)
#                 otp_in_table = otp_obj.OTP
#                 print("-----------------------------------")
#                 print(otp_in_table)
#                 print(otp)
#                 print("-----------------------------------")
#                 if otp_in_table == int(otp) and otp_obj.attempts > 0:
#                     otp_obj.delete()
#                     if Token.objects.filter(user=user).exists():
#                         token_obj = Token.objects.get(user=user)
#                     else:
#                         token_obj = Token.objects.create(user=user)
#                     error = 'False'
#                     message = 'otp varify successfully'
#                     token = token_obj.key
#                     data = {'error': error, 'message': message, 'token': token}
#                     logger_history_function(username, message)
#                     return Response(data)
#                 otp_obj.attempts -= 1
#                 otp_obj.save()
#                 if otp_obj.attempts <= 0:
#                     digits = "0123456789"
#                     digit = "123456789"
#                     OTP = ""
#                     # duration = (datetime.now().time() - Otp.time_generate_otp);
#                     for i in range(6):
#                         if i == 0:
#                             OTP += digit[math.floor(random.random() * 10)]
#                         else:
#                             OTP += digits[math.floor(random.random() * 10)]
#                     if Otp.objects.filter(user=user).exists():
#                         otp_obj = Otp.objects.get(user=user)
#                         otp_obj.delete()
#                     obj = Otp(user=user, attempts=5, OTP=OTP)
#                     obj.save()
#                     error = 'True'
#                     message = 'new otp generated due to max wrong attempts'
#                     token = 'empty'
#                     data = {'error': error, 'message': message, 'token': token}
#                     logger_history_function(username, message)
#                     return Response(data)
#                 error = 'True'
#                 message = 'wrong attempts'
#                 token = 'empty'
#                 data = {'error': error, 'message': message, 'token': token}
#                 logger_history_function(username, message)
#                 return Response(data)
#             error = 'True'
#             message = 'first tap on send otp.'
#             token = 'empty'
#             data = {'error': error, 'message': message, 'token': token}
#             logger_history_function(username, message)
#             return Response(data)
#         error = 'True'
#         message = 'invalid username'
#         token = 'empty'
#         data = {'error': error, 'message': message, 'token': token}
#         return Response(data)


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
