import random

from django.db.models import Q
from nltk import collections
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from channel.models import channel_model
from .models import video_class
from rest_framework.authtoken.models import Token
from datetime import datetime
from main_app.views import logger_history_function
from pymongo import MongoClient
from . import all_languages


def filter_language(title):
    programming_language = []
    imp_tags = []
    title_list = title.split(" ")
    for tag in title_list:
        if title.lower() in all_languages.languages_list:
            programming_language.append(title)
        elif tag.lower() in all_languages.unnessary_word:
            pass
        else:
            imp_tags.append(tag)
    video_tags = programming_language + imp_tags
    print(video_tags)
    video_tags = list(set(video_tags))
    print(video_tags)
    return video_tags


@api_view(['POST'])
@permission_classes([AllowAny])
def search_video(request):
    if request.method == "POST":
        search_string = request.POST.get('search_string')
        if search_string:
            search_list = search_string.split(" ")
            search_list_remove_unnessary_word = []
            for search_word in search_list:
                if search_word.lower() in all_languages.unnessary_word:
                    pass
                else:
                    search_list_remove_unnessary_word.append(search_word)
            search_list = search_list_remove_unnessary_word
            programming_language = False
            for search_word in search_list:
                # print(search_word)
                if search_word in all_languages.all_languages:
                    programming_language = search_word
                    # print(search_word)
            video_ids = []
            if programming_language:
                programming_match_video = video_class.objects.filter(Q(title__icontains=programming_language))
                for search_word in search_list:
                    print(search_word)
                    match_video = programming_match_video.filter(Q(title__icontains=search_word))
                    for find_video_ids in match_video:
                        print(find_video_ids.id)
                        video_ids.append(find_video_ids.id)
            else:
                for search_word in search_list:
                    match_video = video_class.objects.filter(Q(title__icontains=search_word))
                    for find_video_ids in match_video:
                        video_ids.append(find_video_ids.id)
            if video_ids:
                # print(video_ids)
                print(collections.Counter(video_ids))
                video_match_word = list(zip(*collections.Counter(video_ids).items()))
                print(video_match_word[0])
                hit_points_of_video = []
                for index, video_id in enumerate(video_match_word[0]):
                    video_obj = video_class.objects.get(id=video_id)
                    # print(index)
                    hit_points = int(video_match_word[1][index]) * 1000
                    # print(video_match_word[0])
                    if not video_obj.views == 0:
                        hit_points += video_obj.like / video_obj.views * 1000
                        hit_points -= video_obj.dislike / video_obj.views * 1000
                        # hit_points += video_obj.views
                    hit_points_of_video.append(hit_points)
                print(hit_points_of_video)
                final_output = [x for _, x in sorted(zip(hit_points_of_video, video_match_word[0]), reverse=True)]
                print(final_output)
                # video_ids=sorted(set(video_ids), key=lambda ele: video_ids.count(ele))
                # video_ids=video_ids[::-1]
                # # print(video_ids)
                # find_video_object=[]
                find_video_title = []
                for video_id in final_output:
                    video_obj = video_class.objects.get(id=video_id)
                    find_video_title.append(video_obj.title)
                return Response({'result ': find_video_title})
            else:
                return Response({'result ': 'not result found'})
    return Response({'result': search_string})


@api_view(['POST'])
@permission_classes([AllowAny])
def random_like_dislike(request):
    if request.method == "POST":
        for v in video_class.objects.all():
            imp_tags = []
            title_list = v.title.split(" ")
            for tag in title_list:
                if tag in all_languages.unnessary_word:
                    print(tag)
                    pass
                else:
                    imp_tags.append(tag)
            v.tags = imp_tags
            v.like = random.randint(100, 900)
            v.dislike = random.randint(0, 400)
            v.views = random.randint(200, 3000)
            v.save()
    return Response({'okk': 'okk'})


@api_view(['POST'])
@permission_classes([AllowAny])
def trending_video(request):
    if request.method == "POST":
        token = request.POST.get('token')
        if Token.objects.filter(key=token):
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            tags = user.tags
            tags = tags.split(',')
            score = []
            video_ids = []
            for v in video_class.objects.all():
                for user_tags in tags:
                    # print(user_tags)
                    print(v.tags)
                    if user_tags in v.tags:
                        print(user_tags)
                        video_score = v.views + v.like * 2 - v.dislike * 0.5 / v.get_time_diff()
                        #
                        # if v.id in video_ids:
                        #     video_score=video_score*1.2
                        score.append(video_score)
                        video_ids.append(v.id)
            if video_ids:
                score, video_ids = zip(*sorted(zip(score, video_ids)))
            return Response({'video_ids : ': video_ids[0:10]})
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
        print('username not found in document')
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
            channel_id = user.channel_id
            if not channel_model.objects.filter(id=channel_id):
                message = 'user has no channel to upload video first create channel'
                error = 'True'
                data = {'message ': message, 'error': error}
                logger_history_function(token, message)
            else:
                video_tags= tags.split(' ')
                programming_tags = filter_language(title)
                for tag in programming_tags:
                    video_tags.append(tag)
                # print(programming_tags)
                video_obj = video_class(title=title, channel_id=channel_id, video=video, length_of_video=length_of_video
                                        , thumb_image=thumb_image, description=description,
                                        is_downloadable=is_downloadable,
                                        is_sharable=is_sharable, tags=video_tags)
                video_obj.save()
                video_obj = video_class.objects.get(id=video_obj.id)
                channel_obj = channel_model.objects.get(id=channel_id)
                video_ids = channel_obj.video_id
                # print(video_ids)
                # print(video_obj.id)
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
                channel_id = user.channel_id
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
            like_ids = user.likes
            dislike_ids = user.dislikes
            dislike_ids = str(dislike_ids).split(",")
            if video_id in dislike_ids:
                dislike_ids.remove(video_id)
                video_obj.dislike -= 1
                dislike_ids = ",".join(dislike_ids)
                user.dislikes = dislike_ids
            if like_ids == "":
                like_ids = video_id
            else:
                like_ids = str(like_ids).split(",")
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
            user.likes = like_ids
            video_obj.like += 1
            user.save()
            video_obj.save()
            error = "False"
            message = "video liked successfully  : " + title
            token = token
            data = {'error': error, 'message': message, 'token': token}
            video_logger(user.id, video_obj.id, 'like', video_obj.tags)
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
            dislike_ids = user.dislikes
            like_ids = user.likes
            like_ids = str(like_ids).split(",")
            if video_id in like_ids:
                like_ids.remove(video_id)
                video_obj.like -= 1
                like_ids = ",".join(like_ids)
                user.likes = like_ids
            if dislike_ids == "":
                dislike_ids = video_id
            else:
                dislike_ids = str(dislike_ids).split(",")
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
            user.dislikes = dislike_ids
            video_obj.dislike += 1
            user.save()
            video_obj.save()
            error = "False"
            message = "video disliked successfully : " + title
            token = token
            data = {'error': error, 'message': message, 'token': token}
            video_logger(user.id, video_obj.id, 'dislike', video_obj.tags)
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
