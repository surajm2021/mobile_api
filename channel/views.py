from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from main_app.models import Employee
from .models import channel_model
from django.contrib.auth.models import User




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
            message = 'channel name already register by same name'
            error = 'True'
            data = {'message ': message, 'error': error}
        elif Token.objects.filter(key=token):
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            employee = Employee.objects.get(user=user)
            if employee.channel_id == 0:
                channel_obj = channel_model(logo=logo, title=title, description=description)
                channel_obj.save()
                channel_obj = channel_model.objects.get(title=title)
                employee.channel_id = channel_obj.id
                print(channel_obj.id)
                employee.save()
                message = 'channel create successfull'
                error = 'False'
                data = {'message ': message, 'error': error}
            else:  # if channel already exist for same user
                channel = channel_model.objects.get(id=employee.channel_id)
                message = 'channel already exist with channel name : ' + channel.title
                error = 'true'
                data = {'message ': message, 'error': error}

        else:  # if  Token not found in database means user not exit
            message = 'token not found'
            error = 'True'
            data = {'message ': message, 'error': error}
    return Response(data)


