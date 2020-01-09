from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import channel_model
from django.contrib.auth.models import User
from video.models import video_class
from main_app.views import logger_history_function


@api_view(['POST'])
@permission_classes([AllowAny])
def create_channel(request):
    data = {}
    if request.method == "POST":
        token = request.POST.get('token')
        logo = request.FILES.get('logo')
        title = request.POST.get('title')
        description = request.POST.get('description')
        if channel_model.objects.filter(title=title):
            message = 'channel name already register by same name '+title
            error = 'True'
            data = {'message ': message, 'error': error}
            logger_history_function(token,message)
        elif Token.objects.filter(key=token):
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user.is_verify:
                if user.channel_id is None:
                    channel_obj = channel_model(logo=logo, title=title, description=description)
                    channel_obj.save()
                    channel_obj = channel_model.objects.get(title=title)
                    user.channel_id = channel_obj.id
                    print(channel_obj.id)
                    user.save()
                    message = 'channel create successfully channel name '+title
                    error = 'False'
                    data = {'message ': message, 'error': error}
                    logger_history_function(token, message)
                else:  # if channel already exist for same user
                    channel = channel_model.objects.get(id=user.channel_id)
                    message = 'channel already exist with channel name : ' + channel.title
                    error = 'True'
                    data = {'message ': message, 'error': error}
                    logger_history_function(token, message)
            else:
                message = 'phone number not verify first verify your phone number'
                error = 'True'
                data = {'message ': message, 'error': error}
                logger_history_function(token, message)
        else:  # if  Token not found in database means user not exit
            message = 'token not found'
            error = 'True'
            data = {'message ': message, 'error': error}
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_channel(request):
    data = {}
    if request.method == "POST":
        token = request.POST.get('token')
        channel_id = request.POST.get('channel_id')
        if Token.objects.filter(key=token):
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user.channel_id is None:
                message = 'This User has no channel exit'
                error = 'False'
                data = {'message ': message, 'error': error}
                logger_history_function(token, message)
            else:  # if channel already exist for same user
                if not channel_model.objects.filter(id=channel_id):
                    message = 'cannot delete channel channel ids wrong '
                    error = 'True'
                    data = {'message ': message, 'error': error}
                    logger_history_function(token, message)

                else:
                    channel = channel_model.objects.get(id=channel_id)
                    title = channel.title
                    video_ids =channel.video_id
                    print(video_ids)
                    video_list = video_ids.split(",")
                    print(video_list)
                    video_list = [s for s in video_list if s.isdigit()]
                    for id in video_list :
                        print(id)
                        if video_class.objects.filter(id=id) :
                            video_obj = video_class.objects.get(id=id)
                            video_obj.delete()
                        else:
                            print(f'{id},video not found')
                    user.channel_id=None
                    user.save()
                    channel.delete()
                    message = 'channel delete successfully : '+title
                    error = 'False'
                    data = {'message ': message, 'error': error}
                    logger_history_function(token, message)

        else:  # if  Token not found in database means user not exit
            message = 'token not found'
            error = 'True'
            data = {'message ': message, 'error': error}
    return Response(data)


