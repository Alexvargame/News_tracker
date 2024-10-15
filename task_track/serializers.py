from rest_framework import serializers
from .models import Track,Task
from django.contrib.auth.models import User


from datetime import datetime,timedelta
class TrackCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model=Track
        fields=('user','task')

    def validate(self,data):
        e_time=data.get('time_end',datetime(2026,1,1,0,0))
        s_time=data.get('time_start',datetime.now())

        if len(Track.objects.filter(user=data['user'],task=data['task'],time_end__gt=s_time))>0:
            raise serializers.ValidationError(f"По данной задаче есть незакрытый трекер")
        return data

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model=Task
        fields=('name','discription')

class TrackSerializer(serializers.ModelSerializer):

    time_start=serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    time_end = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    class Meta:
        model=Track
        fields=('user','task','time_start','time_end')

class WorkUserSerializer(serializers.Serializer):
    task=serializers.CharField(max_length=50)
def default_date():
    return datetime.now()
class TrackTimeSerializer(serializers.Serializer):
    user=serializers.ChoiceField(choices=[(u.id,u.username) for u in User.objects.all()],style={'base_template':'select.html'})
    time_start=serializers.DateTimeField(format='%Y-%m-%d %H:%M',default=default_date)
    time_end = serializers.DateTimeField(format='%Y-%m-%d %H:%M',default=default_date)
class TrackDateSerializer(serializers.Serializer):
    user=serializers.ChoiceField(choices=[(u.id,u.username) for u in User.objects.all()],style={'base_template':'select.html'})
    time_start=serializers.DateField(format='%Y-%m-%d',default=default_date)
    time_end = serializers.DateField(format='%Y-%m-%d',default=default_date)

class TrackUserSerializer(serializers.Serializer):
    user=serializers.ChoiceField(choices=[(u.id,u.username) for u in User.objects.all()],style={'base_template':'select.html'})
