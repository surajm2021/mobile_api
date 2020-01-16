from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import channel_model, course, course_session
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
            message = 'channel name already register by same name ' + title
            error = 'True'
            data = {'message ': message, 'error': error}
            logger_history_function(token, message)
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
                    message = 'channel create successfully channel name ' + title
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
                    video_ids = channel.video_id
                    print(video_ids)
                    video_list = video_ids.split(",")
                    print(video_list)
                    video_list = [s for s in video_list if s.isdigit()]
                    for id in video_list:
                        print(id)
                        if video_class.objects.filter(id=id):
                            video_obj = video_class.objects.get(id=id)
                            # video_obj.delete()
                        else:
                            print(f'{id},video not found')
                    course_id = channel.courses_id
                    course_id_list = course_id.split(",")
                    print(video_list)
                    course_id_list = [s for s in course_id_list if s.isdigit()]
                    for course_id in course_id_list:
                        if course.objects.filter(id=course_id):
                            course_obj = course.objects.get(id=course_id)
                            course_session_id = course_obj.session_id
                            if not course_session_id is None:
                                course_session_id_list = course_session_id.split(",")
                                course_session_id_list = [s for s in course_session_id_list if s.isdigit()]
                                for session_id in course_session_id_list:
                                    print(f'session id : {session_id}')
                                    session_obj=course_session.objects.get(id=session_id)
                                    session_obj.delete()
                            course_obj.delete()
                    user.channel_id = None
                    user.save()
                    channel.delete()
                    message = 'channel delete successfully : ' + title
                    error = 'False'
                    data = {'message ': message, 'error': error}
                    logger_history_function(token, message)

        else:  # if  Token not found in database means user not exit
            message = 'token not found'
            error = 'True'
            data = {'message ': message, 'error': error}
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_course(request):
    data = {}
    if request.method == "POST":
        token = request.POST.get('token')
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        description = request.POST.get('description')
        requirement = request.POST.get('requirement')
        level = request.POST.get('level')
        if Token.objects.filter(key=token):
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user.is_verify:
                if title is None or subtitle is None:
                    message = 'title and subtitle is require while creating new course '
                    error = 'True'
                    data = {'message ': message, 'error': error}
                    logger_history_function(token, message)
                elif course.objects.filter(title=title, channel_id=user.channel_id).exists():
                    message = 'user has same course name found try another title ' + title
                    error = 'False'
                    data = {'message ': message, 'error': error}
                    logger_history_function(token, message)
                elif not channel_model.objects.filter(id=user.channel_id):
                    message = 'User has not created channel yet.'
                    error = 'False'
                    data = {'message ': message, 'error': error}
                    logger_history_function(token, message)

                else:
                    course_obj = course(title=title, channel_id=user.channel_id, subtitle=subtitle,
                                        requirement=requirement,
                                        level=level, description=description)
                    course_obj.save()
                    channel_obj = channel_model.objects.get(id=user.channel_id)
                    if channel_obj.courses_id is None:
                        channel_obj.courses_id = ""
                    temp_course_id = str(channel_obj.courses_id) + str(course_obj.id) + ","
                    channel_obj.courses_id = temp_course_id
                    print(channel_obj.courses_id)
                    channel_obj.save()
                    message = 'course create successfully course name ' + title
                    error = 'False'
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
def delete_course(request):
    data = {}
    if request.method == "POST":
        token = request.POST.get('token')
        course_id = request.POST.get('course_id')
        if Token.objects.filter(key=token):
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user.is_verify:
                if not channel_model.objects.filter(id=user.channel_id):
                    message = 'User has not created channel yet.'
                    error = 'False'
                    data = {'message ': message, 'error': error}
                    logger_history_function(token, message)
                elif course.objects.filter(id=course_id).exists():
                    course_obj = course.objects.get(id=course_id)
                    channel_obj = channel_model.objects.get(id=user.channel_id)
                    courses_id_list = (channel_obj.courses_id).split(",")
                    print(courses_id_list)
                    if course_id in courses_id_list:
                        if not course_obj.session_id is None:
                            print(course_obj.session_id)
                            session_id_in_list = (course_obj.session_id).split(",")
                            print(course_obj.session_id)
                            print(session_id_in_list)
                            for session_id in session_id_in_list:
                                if session_id == '':
                                    pass
                                elif course_session.objects.filter(id=session_id):
                                    session_obj = course_session.objects.get(id=session_id)
                                    session_obj.delete()
                                    print(session_id)
                        channel_course_list = channel_obj.courses_id.split(",")

                        print(str(course_obj.id))
                        print(channel_course_list)
                        channel_course_list.remove(str(course_obj.id))
                        channel_course_id = ",".join(channel_course_list)
                        channel_obj.courses_id = channel_course_id
                        print(channel_course_id)
                        print('-----------------------')
                        # print(channel_course_id)
                        channel_obj.save()
                        course_obj.delete()
                        message = 'course  delete  successfully'
                        error = 'False'
                        data = {'message ': message, 'error': error}
                    else:
                        message = 'course not created this user'
                        error = 'True'
                        data = {'message ': message, 'error': error}
                else:
                    message = 'channel not found first create or course is not belong to user channel'
                    error = 'True'
                    data = {'message ': message, 'error': error}
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


def position(temp_video_id_in_session, video_id, video_position):
    temp_video_id_in_session_list = temp_video_id_in_session.split(',')
    if video_id in temp_video_id_in_session_list:
        temp_video_id_in_session_list.remove(video_id)
    if len(temp_video_id_in_session_list) < int(video_position):
        temp_video_id_in_session_list.insert(int(video_position) - 1, video_id)
    else:
        temp_video_id_in_session_list.append(video_id)
    temp_video_id_in_session = ",".join(temp_video_id_in_session_list)
    print(temp_video_id_in_session)
    return temp_video_id_in_session


@api_view(['POST'])
@permission_classes([AllowAny])
def update_or_create_course_session(request):
    data = {}
    if request.method == "POST":
        token = request.POST.get('token')
        video_id = request.POST.get('video_id')
        course_session_id = request.POST.get('course_session_id')
        course_session_name = request.POST.get('title')
        course_id = request.POST.get('course_id')
        video_position = request.POST.get('video_position')
        if course_session_id is None:
            course_session_id = 0
        if Token.objects.filter(key=token):
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if course_session_name is None:
                message = 'session title is required during creating new session'
                error = 'False'
                data = {'message ': message, 'error': error}
            elif user.is_verify:
                if channel_model.objects.filter(id=user.channel_id):
                    channel_obj = channel_model.objects.get(id=user.channel_id)
                    if course.objects.filter(id=course_id):
                        course_obj = course.objects.get(id=course_id)
                        if channel_obj.id == course_obj.channel_id:
                            if video_class.objects.filter(id=video_id):
                                video_obj = video_class.objects.get(id=video_id)
                                if video_obj.channel_id == channel_obj.id:
                                    if not course_session.objects.filter(id=course_session_id):
                                        print(course_session_name)
                                        course_session_obj = course_session(title=course_session_name, video_id=str(
                                            video_id))  # , channel_model=channel_obj)
                                        course_session_obj.save()
                                        if course_obj.session_id is None:
                                            course_obj.session_id = ""
                                        temp_video_session_id = str(course_obj.session_id)
                                        temp_video_session_id_list = temp_video_session_id.split(",")
                                        temp_video_session_id_list.append(str(course_session_obj.id))
                                        course_obj.session_id = ",".join(temp_video_session_id_list)
                                        course_obj.save()
                                        message = 'Course Session is newly created'
                                        error = 'False'
                                        data = {'message ': message, 'error': error}
                                    else:
                                        course_session_obj = course_session.objects.get(id=course_session_id)
                                        course_session_obj.video_id = position(course_session_obj.video_id, video_id,
                                                                               video_position)
                                        course_session_obj.save()
                                        message = 'Course session is already present and inserted into the course.'
                                        error = 'False'
                                        data = {'message ': message, 'error': error}
                                else:
                                    message = 'video is not related to that channel'
                                    error = 'True'
                                    data = {'message ': message, 'error': error}
                            else:
                                message = 'video id not found'
                                error = 'True'
                                data = {'message ': message, 'error': error}

                        else:
                            message = 'Channel is not related to this course.'
                            error = 'True'
                            data = {'message ': message, 'error': error}
                    else:
                        message = 'Course not found first create course'
                        error = 'True'
                        data = {'message ': message, 'error': error}
                else:
                    message = 'channel not created yet.'
                    error = 'True'
                    data = {'message ': message, 'error': error}
            else:
                message = 'User is not verified.'
                error = 'True'
                data = {'message ': message, 'error': error}
        else:
            message = 'Token is not available.'
            error = 'True'
            data = {'message ': message, 'error': error}

        return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_session(request):
    data = {}
    token = request.POST.get('token')
    session_id = request.POST.get('session_id')
    course_id = request.POST.get('course_id')
    if session_id is None or course_id is None:
        message = 'session id and course id required to delete session.'
        error = 'True'
        data = {'message ': message, 'error': error}
        logger_history_function(token, message)
    elif Token.objects.filter(key=token):
        token_obj = Token.objects.get(key=token)
        user = token_obj.user
        if user.is_verify:
            if not channel_model.objects.filter(id=user.channel_id):
                message = 'User has not created channel yet.'
                error = 'False'
                data = {'message ': message, 'error': error}
                logger_history_function(token, message)
            elif course.objects.filter(id=course_id).exists():
                course_obj = course.objects.get(id=course_id)
                channel_obj = channel_model.objects.get(id=user.channel_id)
                courses_id_list = (channel_obj.courses_id).split(",")
                print(courses_id_list)
                if course_id in courses_id_list:
                    if not course_obj.session_id is None:
                        print(course_obj.session_id)
                        session_id_in_list = (course_obj.session_id).split(",")
                        print(course_obj.session_id)
                        print(session_id_in_list)
                        session_delete_successful = False
                        for course_session_id in session_id_in_list:
                            if session_id == '':
                                pass
                            if course_session_id == session_id:
                                if course_session.objects.filter(id=session_id):
                                    session_obj = course_session.objects.get(id=session_id)
                                    session_obj.delete()
                                    print(session_id)
                                    course_session_list = course_obj.session_id.split(",")
                                    print(str(session_id))
                                    print(course_session_list)
                                    course_session_list.remove(str(session_id))
                                    course_session_list = ",".join(course_session_list)
                                    course_obj.session_id = course_session_list
                                    print(course_session_list)
                                    print('-----------------------')
                                    # print(channel_course_id)
                                    course_obj.save()
                                    session_delete_successful = True
                        if session_delete_successful:
                            message = 'session  delete  successfully'
                            error = 'False'
                            data = {'message ': message, 'error': error}
                        else:
                            message = 'session not found'
                            error = 'True'
                            data = {'message ': message, 'error': error}
                    else:
                        message = 'course has no session found'
                        error = 'True'
                        data = {'message ': message, 'error': error}
                else:
                    message = 'course not created this user'
                    error = 'True'
                    data = {'message ': message, 'error': error}
            else:
                message = 'channel not found first create or course is not belong to user channel'
                error = 'True'
                data = {'message ': message, 'error': error}
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
def delete_video_from_session(request):
    video_id = request.POST.get('video_id')
    session_id = request.POST.get('session_id')
    course_id = request.POST.get('course_id')
    token = request.POST.get('token')
    if session_id is None or course_id is None:
        message = 'session id and course id required to delete session.'
        error = 'True'
        data = {'message ': message, 'error': error}
        logger_history_function(token, message)
    elif Token.objects.filter(key=token):
        token_obj = Token.objects.get(key=token)
        user = token_obj.user
        if user.is_verify:
            if not channel_model.objects.filter(id=user.channel_id):
                message = 'User has not created channel yet.'
                error = 'False'
                data = {'message ': message, 'error': error}
                logger_history_function(token, message)
            elif course.objects.filter(id=course_id).exists():
                course_obj = course.objects.get(id=course_id)
                channel_obj = channel_model.objects.get(id=user.channel_id)
                courses_id_list = channel_obj.courses_id.split(",")
                print(courses_id_list)
                if course_id in courses_id_list:
                    if not course_obj.session_id is None:
                        print(course_obj.session_id)
                        session_id_in_list = course_obj.session_id.split(",")
                        print(course_obj.session_id)
                        print(session_id_in_list)
                        session_delete_successful = False
                        for course_session_id in session_id_in_list:
                            if session_id == '':
                                pass
                            if course_session_id == session_id:
                                if course_session.objects.filter(id=session_id):
                                    session_obj = course_session.objects.get(id=session_id)
                                    video_ids = session_obj.video_id
                                    video_ids = video_ids.split(",")
                                    if video_id in video_ids:
                                        video_ids.remove(video_id)
                                    session_obj.video_id = ",".join(video_ids)
                                    session_obj.save()
                                    video_delete_successful = True
                        if video_delete_successful:
                            message = 'video  deleted from session successfully'
                            error = 'False'
                            data = {'message ': message, 'error': error}
                        else:
                            message = 'session not found'
                            error = 'True'
                            data = {'message ': message, 'error': error}
                    else:
                        message = 'course has no session found'
                        error = 'True'
                        data = {'message ': message, 'error': error}
                else:
                    message = 'course not created this user'
                    error = 'True'
                    data = {'message ': message, 'error': error}
            else:
                message = 'channel not found first create or course is not belong to user channel'
                error = 'True'
                data = {'message ': message, 'error': error}
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