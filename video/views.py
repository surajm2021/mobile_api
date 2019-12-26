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
            video_obj = video_class(title=title, channel_id=channel_id, video=video, length_of_video=length_of_video
                                    , thumb_image=thumb_image, description=description, is_downloadable=is_downloadable,
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
            message = 'Video uploaded successfull'
            error = 'False'
            data = {'message ': message, 'error': error}
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
                if video_class.objects.filter(id=video_id,channel_id=channel_id):
                    video_obj = video_class.objects.get(id=video_id)
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
                    channel_obj.video_id=video_ids
                    channel_obj.save()
                    message = 'Video delete successfull'
                    error = 'False'
                    data = {'message ': message, 'error': error}
                else:
                    message = 'Video Not uploaded this user'
                    error = 'True'
                    data = {'message ': message, 'error': error}
            else:
                message = 'Video not found'
                error = 'True'
                data = {'message ': message, 'error': error}
        else:
            message = 'Token Not verify '
            error = 'True'
            data = {'message ': message, 'error': error}
    return Response(data)



