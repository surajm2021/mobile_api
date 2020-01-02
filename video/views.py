import string

from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
# Create your views here.
from channel.models import channel_model
from .models import video_class
from main_app.models import Employee
from rest_framework.authtoken.models import Token
from datetime import datetime
from main_app.views import logger_history_function
from pymongo import MongoClient
from . import all_languages


def filter_language(title):
    title_list = title.split(' ')
    for title in title_list:
        if title.lower() in all_languages.languages_list:
            print('---------------------------------------------------------------------------')
            print(title)
            print('---------------------------------------------------------------------------')
            return title
        else:
            print('not found any language name')
    return title


@api_view(['POST'])
@permission_classes([AllowAny])
def trending_video(request):
    if request.method == "POST":
        token = request.POST.get('token')
        if Token.objects.filter(key=token):
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            tags = user.employee.tags
            print(tags)
            score = []
            video_ids = []
            for v in video_class.objects.all():
                video_score = v.views + 2 * (v.like - v.dislike) / v.get_time_diff()
                score.append(video_score)
                video_ids.append(v.id)
            score, video_ids = zip(*sorted(zip(score, video_ids)))

            print(score)
            print(video_ids)
            return Response({'score : ': score, 'video_ids : ': video_ids})
        else:
            return Response({'message': 'token Not found'})


def video_logger(user_id, video_id, activity, tag):
    client = MongoClient('mongodb://127.0.0.1:27017')
    print('database connection successfully')
    db = client.geniobits
    mycollection = db['video_log']
    if mycollection.find({'user_id': user_id}).count() > 0:
        print('true')
        print('usename found in document ')
        result = mycollection.update({
            'user_id': user_id
        }, {
            '$push': {
                "activity": {'activity ': activity, 'video_id': video_id, 'tag': tag, 'time': str(datetime.now())}
            }
        })
        print(str(result['updatedExisting']) + ' user_id not found create new database')
        if not result['updatedExisting']:
            mycollection.insert({
                'user_id': user_id,
                "activity": [{'activity ': activity, 'video_id': video_id, 'tag': tag, 'time': str(datetime.now())}]
            })
            print('new document create successful')
    else:
        print('usename not found in document')
        mycollection.insert({
            'user_id': user_id,
            "activity": [{'activity ': activity, 'video_id': video_id, 'tag': tag, 'time': str(datetime.now())}]
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_video(request):
    data = {}
    if request.method == "POST":
        token = request.POST.get('token')
        video = request.FILES.get('video')
        length_of_video = request.POST.get('length_of_video')
        thumb_image = request.FILES.get('thumb_image')
        description = request.POST.get('description')
        tags = request.POST.get('tags')
        title = request.POST.get('title')
        is_downloadable = request.POST.get('is_downloadable')
        is_sharable = request.POST.get('is_sharable')
        # if  video_class.objects.filter(title=title):
        #     message = 'Video name alread exist with another video'
        #     error = 'True'
        #     data = {'message ': message, 'error': error}

        if Token.objects.filter(key=token):
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            channel_id = user.employee.channel_id
            if not channel_model.objects.filter(id=channel_id):
                message = 'user has no channel to upload video first create channel'
                error = 'True'
                data = {'message ': message, 'error': error}
                logger_history_function(token, message)
            else:
                programming_language = filter_language(title)
                print(programming_language)

                video_obj = video_class(title=title, channel_id=channel_id, video=video, length_of_video=length_of_video
                                        , thumb_image=thumb_image, description=description,
                                        is_downloadable=is_downloadable,
                                        is_sharable=is_sharable, tags=tags)
                video_obj.save()
                video_obj = video_class.objects.get(id=video_obj.id)
                channel_obj = channel_model.objects.get(id=channel_id)
                video_ids = channel_obj.video_id
                print(video_ids)
                print(video_obj.id)
                video_ids = str(video_ids) + str(video_obj.id) + ","
                channel_obj.video_id = video_ids
                channel_obj.save()
                message = 'Video uploaded successful :  ' + title
                error = 'False'
                data = {'message ': message, 'error': error}
                logger_history_function(token, message)
        else:
            message = 'Token Not verify '
            error = 'True'
            data = {'message ': message, 'error': error}
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_video(request):
    data = {}
    if request.method == "POST":
        token = request.POST.get('token')
        video_id = request.POST.get('video_id')
        if Token.objects.filter(key=token):
            if video_class.objects.filter(id=video_id):
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
                channel_id = user.employee.channel_id
                if video_class.objects.filter(id=video_id, channel_id=channel_id):
                    video_obj = video_class.objects.get(id=video_id)
                    title = video_obj.title
                    channel_obj = channel_model.objects.get(id=channel_id)
                    video_ids = channel_obj.video_id
                    video_list = video_ids.split(",")
                    video_list = [s for s in video_list if s.isdigit()]
                    print(video_list)
                    video_list.remove(video_id)
                    print(video_list)
                    video_ids = ","
                    video_ids = video_ids.join(video_list)
                    print(video_ids)
                    video_obj.delete()
                    channel_obj.video_id = video_ids
                    channel_obj.save()
                    message = 'Video delete successfully  : ' + title
                    error = 'False'
                    data = {'message ': message, 'error': error}
                    logger_history_function(token, message)
                else:
                    message = 'user try to delete video that not upload by this user'
                    error = 'True'
                    data = {'message ': message, 'error': error}
                    logger_history_function(token, message)
            else:
                message = 'Video not found'
                error = 'True'
                data = {'message ': message, 'error': error}
                logger_history_function(token, message)
        else:
            message = 'Token Not verify '
            error = 'True'
            data = {'message ': message, 'error': error}
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def like_video(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        video_id = request.POST.get('video_id')
        if Token.objects.filter(key=token).exists() and video_class.objects.filter(id=video_id).exists():
            video_obj = video_class.objects.get(id=video_id)
            title = video_obj.title
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if Employee.objects.filter(user=user).exists():
                emp_obj = Employee.objects.get(user=user)
                like_ids = emp_obj.liked
                dislike_ids = emp_obj.disliked
                dislike_ids = dislike_ids.split(",")
                if video_id in dislike_ids:
                    dislike_ids.remove(video_id)
                    video_obj.dislike -= 1
                    dislike_ids = ",".join(dislike_ids)
                    emp_obj.disliked = dislike_ids
                if like_ids == "":
                    like_ids = video_id
                else:
                    like_ids = like_ids.split(",")
                    if video_id not in like_ids:
                        like_ids.append(video_id)
                    else:
                        error = "True"
                        message = "video already liked  : " + title
                        token = token
                        data = {'error': error, 'message': message, 'token': token}
                        logger_history_function(token, message)
                        return Response(data)
                    like_ids = ",".join(like_ids)
                emp_obj.liked = like_ids
                video_obj.like += 1
                emp_obj.save()
                video_obj.save()
                error = "False"
                message = "video liked successfully  : " + title
                token = token
                data = {'error': error, 'message': message, 'token': token}
                video_logger(user.id, video_obj.id, 'like', video_obj.tags)
                logger_history_function(token, message)
                return Response(data)
            error = "True"
            message = "user is not having proper data may be admin"
            token = token
            data = {'error': error, 'message': message, 'token': token}
            logger_history_function(token, message)
            return Response(data)
        error = "True"
        message = "invalid token received or video id not correct "
        token = "empty"
        data = {'error': error, 'message': message, 'token': token}
        return Response(data)
    error = "True"
    message = "invalid request received"
    token = "empty"
    data = {'error': error, 'message': message, 'token': token}
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def dislike_video(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        video_id = request.POST.get('video_id')
        if Token.objects.filter(key=token).exists() and video_class.objects.filter(id=video_id).exists():
            video_obj = video_class.objects.get(id=video_id)
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            title = video_obj.title
            if Employee.objects.filter(user=user).exists():
                emp_obj = Employee.objects.get(user=user)
                dislike_ids = emp_obj.disliked
                like_ids = emp_obj.liked
                like_ids = like_ids.split(",")
                if video_id in like_ids:
                    like_ids.remove(video_id)
                    video_obj.like -= 1
                    like_ids = ",".join(like_ids)
                    emp_obj.liked = like_ids
                if dislike_ids == "":
                    dislike_ids = video_id
                else:
                    dislike_ids = dislike_ids.split(",")
                    if video_id not in dislike_ids:
                        dislike_ids.append(video_id)
                    else:
                        error = "True"
                        message = "video already disliked : " + title
                        token = token
                        data = {'error': error, 'message': message, 'token': token}
                        logger_history_function(token, message)
                        return Response(data)
                dislike_ids = ",".join(dislike_ids)
                emp_obj.disliked = dislike_ids
                video_obj.dislike += 1
                emp_obj.save()
                video_obj.save()
                error = "False"
                message = "video disliked successfully : " + title
                token = token
                data = {'error': error, 'message': message, 'token': token}
                video_logger(user.id, video_obj.id, 'dislike', video_obj.tags)
                logger_history_function(token, message)
                return Response(data)
            error = "True"
            message = "user is not having proper data may be admin"
            token = token
            data = {'error': error, 'message': message, 'token': token}
            logger_history_function(token, message)
            return Response(data)
        error = "True"
        message = "invalid token received"
        token = "empty"
        data = {'error': error, 'message': message, 'token': token}
        return Response(data)
    error = "True"
    message = "invalid request received"
    token = "empty"
    data = {'error': error, 'message': message, 'token': token}
    return Response(data)
