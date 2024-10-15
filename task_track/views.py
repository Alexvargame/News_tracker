from django.shortcuts import render,reverse,redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from django.contrib.auth.models import User

from datetime import datetime,timedelta

from tracker.settings import END_TIME

from .serializers import (
    TrackSerializer,TaskSerializer,
    TrackCreateSerializer,TrackTimeSerializer,
    TrackDateSerializer,TrackUserSerializer)

from .models import Track,Task
def main_page(request):
    return render(request,'task_track/main_page.html')

class CreateTrack(APIView):
    def post(self,request):
        serializer=TrackCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201)
        return Response(serializer.errors)

class StopTracker(APIView):
    def post(self,request,pk):
        track=Track.objects.get(id=pk)
        #serializer=TrackSerialiser(track,data=request.data)
        track.time_end=datetime.now()
        track.save()
        return Response(status=201)

class ListUserTrackers(APIView):
    def get(self,request,pk):

        user=User.objects.get(id=pk)
        tracks=Track.objects.filter(user=user)
        serializer=TrackSerializer(tracks,many=True)
        return Response(serializer.data)
class ListTrackers(APIView):
    def get(self,request):
        tracks=Track.objects.all()
        serializer=TrackSerializer(tracks,many=True)
        return Response(serializer.data)

class ListTasks(APIView):
    def get(self,request):
        tasks=Task.objects.all()
        serializer=TrackSerialiser(tasks,many=True)
        return Response(serializer.data)

class TaskWorkUser(APIView):
    def post(self,request,pk):
        result={}
        d_start=datetime.strptime(request.data['start'],'%Y-%m-%d %H:%M')
        d_end = datetime.strptime(request.data['end'],'%Y-%m-%d %H:%M')
        for task in Task.objects.all():
            tracks = task.task_tracks.filter(user=User.objects.get(id=pk), time_start__range=[d_start, d_end])
            period=0
            if tracks:
                for track in tracks:
                    if track.time_end is not None:
                        if datetime(*[int(t) for t in track.time_end.strftime("%Y %m %d %H %M").split()])<d_end:
                            period+=(track.time_end-track.time_start).seconds
                        else:
                            period += (d_end - datetime(*[int(t) for t in track.time_start.strftime("%Y %m %d %I %M").split()])).seconds
                    else:
                        period+=(datetime.now()-datetime(*[int(t) for t in track.time_start.strftime("%Y %m %d %I %M").split()])).seconds-7200

                    result[task.id]= {'часы':period//3600,'минуты':period//60-(period//3600)*60}
        result=sorted(result.items(), key=lambda x: x[1]['часы']*60+x[1]['минуты'])[::-1]
        return Response (result)
class SumTaskWorkUser(APIView):
    def post(self,request,pk):
        period=0
        d_start=datetime.strptime(request.data['start'],'%Y-%m-%d %H:%M')
        d_end = datetime.strptime(request.data['end'],'%Y-%m-%d %H:%M')
        for task in Task.objects.all():
            tracks=task.task_tracks.filter(user=User.objects.get(id=pk),time_start__range=[d_start,d_end])
            if tracks:
                for track in tracks:
                    if track.time_end is not None:
                        if datetime(*[int(t) for t in track.time_end.strftime("%Y %m %d %H %M").split()])<d_end:
                            period+=(track.time_end-track.time_start).seconds
                        else:
                            period+=(d_end - datetime(*[int(t) for t in track.time_start.strftime("%Y %m %d %I %M").split()])).seconds
                    else:
                        period+=(datetime.now()-datetime(*[int(t) for t in track.time_start.strftime("%Y %m %d %I %M").split()])).seconds-7200
        return Response (f'Трудозатраты с {d_start} до {d_end} составляют {period//3600} часов {period//60-(period//3600)*60} минут')
class IntervalWorkUser(APIView):
    def post(self,request,pk):
        d_start=datetime.strptime(request.data['start']+' 00:00','%Y-%m-%d %H:%M')
        d_end = datetime.strptime(request.data['end']+' 23:59','%Y-%m-%d %H:%M')
        count_days=(d_end-d_start).days+1
        start_period=d_start
        intervals_dict={}
        for d in range(1,count_days+1):
            end_period=start_period+timedelta(days=1)
            intervals_dict[str(d)] = {'start_interval': start_period,'end_interval': end_period, 'tasks': []}
            start_period=end_period
        intervals_sort=sorted(intervals_dict.items(), key=lambda x: x[0])
        tracks=Track.objects.filter(user=User.objects.get(id=pk),time_start__range=(datetime(2023,1,1,0,0),intervals_sort[-1][1]['end_interval']))
        for key,value in intervals_dict.items():
            tracks_lst=[]
            for track in Track.objects.filter(user=User.objects.get(id=pk),
                                 time_start__range=(datetime(2023, 1, 1, 0, 0), intervals_dict[key]['end_interval']),
                                 time_end__range=(intervals_dict[key]['start_interval'], datetime(2026, 1, 1, 0, 0))):
                track_dict={}
                track_dict['user']=track.user.id
                track_dict['task']=TaskSerializer(track.task).data
                if datetime(*[int(t) for t in track.time_start.strftime("%Y %m %d %H %M").split()])>intervals_dict[key]['start_interval']:
                    track_dict['time_start']=datetime(*[int(t) for t in track.time_start.strftime("%Y %m %d %H %M").split()])
                else:
                    track_dict['time_start']=intervals_dict[key]['start_interval']
                if datetime(*[int(t) for t in track.time_end.strftime("%Y %m %d %H %M").split()]) <  \
                            intervals_dict[key]['end_interval']:
                        track_dict['time_end'] = datetime(
                            *[int(t) for t in track.time_end.strftime("%Y %m %d %H %M").split()])
                else:
                        track_dict['time_end'] = intervals_dict[key]['end_interval']
                tracks_lst.append(track_dict)
            intervals_dict[key]['tasks']=tracks_lst
        return Response (intervals_dict)

class DeleteUserTracks(APIView):
    def post(self,request,pk):
        user=User.objects.get(id=pk)
        tracks=Track.objects.filter(user=user)
        for track in tracks:
            track.delete()
        tracks=Track.objects.filter(user=user)
        serialiser=TrackSerializer(tracks,many=True)
        return Response(serialiser.data)

"""Frontend"""


class CreateTrackFrontendView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'task_track/track_create.html'
    def get(self,request):
        serializer=TrackCreateSerializer()
        return Response({'serializer':serializer})
    def post(self,request):

        serializer=TrackCreateSerializer(data=request.data)
        print(request.data, request.data['user'],type(request.data['user']))
        if serializer.is_valid():
            serializer.save()
            return redirect(reverse('user_tracks_list_fr_url',kwargs={'pk':request.data['user']}))

        return Response({'serializer':serializer,'message':f"По данной задаче есть незакрытый трекер"})
class TrackDetailFrontendView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'task_track/track_detail.html'
    def get(self,request,pk):

        track=Track.objects.get(id=pk)
        print('DDDDDDETAIL', track.id)
        user=User.objects.filter(id=track.user.id)[0]#request.user.id)
        duration=track.time_end-track.time_start
        serializer=TrackSerializer(track)
        return Response({'track':serializer.data,'user':user,'duration':duration,'task':track.task.name,'track_id':track.id})
class TrackUpdateFrontendView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'task_track/track_update.html'
    def get(self,request,pk):
        print('EE')
        track=Track.objects.get(id=pk)
        user=User.objects.filter(id=track.user.id)[0]#request.user.id)
        duration=track.time_end-track.time_start
        serializer=TrackSerializer(track)
        return Response({'serializer':serializer,'track':track})
    def post(self,request,pk):
        track=Track.objects.get(id=pk)
        user = User.objects.filter(id=track.user.id)[0]
        serializer=TrackSerializer(track,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect(reverse('track_detail_fr_url',kwargs={'pk':track.id}))
        else:
            return Response({'track':track,'serializer':serializer})


class TrackDeleteFrontendView(APIView):
    def get(self, request, pk):
        track = Track.objects.get(id=pk)
        return render(request, 'task_track/track_delete.html',{'track':track})

    def post(self, request, pk):
        track = Track.objects.get(id=pk)
        user = User.objects.filter(id=track.user.id)[0]
        track.delete()
        return redirect(reverse('user_tracks_list_fr_url',kwargs={'pk':user.id}))

class StopTrackerFrontendView(APIView):
    def get(self, request, pk):
        track = Track.objects.get(id=pk)
        return render(request, 'task_track/track_stop.html', {'track': track})
    def post(self,request,pk):
        track=Track.objects.get(id=pk)
        if datetime.now()<datetime(track.time_end.year,track.time_end.month,track.time_end.day,track.time_end.hour,track.time_end.minute):
            track.time_end=datetime.now()
            track.save()
        return redirect(track)

class ListUserTrackersFrontendView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'task_track/tracks_list.html'
    def get(self,request,pk):
        user=User.objects.get(id=pk)
        tracks=Track.objects.filter(user=user)
        serializer=TrackSerializer(tracks,many=True)
        return Response({'tracks':tracks,'user':user})

class ListTrackersFrontendView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'task_track/tracks_list.html'
    def get(self,request):
        tracks=Track.objects.all()
        serializer=TrackSerializer(tracks,many=True)
        return Response({'tracks':tracks})

class ListTasksFrontendView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'task_track/tasks_list.html'
    def get(self,request):
        tasks=Task.objects.all()
        return Response({'tasks':tasks})
class TaskDetailFrontendView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'task_track/task_detail.html'
    def get(self,request,pk):
        task=Task.objects.get(id=pk)
        work_tracks=task.task_tracks.filter(time_end__gte=datetime.now())
        return Response({'task':task,'tracks':work_tracks,'count_tracks':len(work_tracks),'users':len(User.objects.all())})

class TaskCreateFrontendView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'task_track/task_create.html'
    def get(self,request):
        serializer=TaskSerializer()
        return Response({'serializer':serializer})
    def post(self,request):
        serializer=TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect('tasks_list_fr_url')
        else:
            return Response({'serializer':serializer})
class TaskDeleteFrontendView(APIView):
    def get(self, request, pk):
        task = Task.objects.get(id=pk)
        return render(request, 'task_track/task_delete.html',{'task':task})

    def post(self, request, pk):
        task = Task.objects.get(id=pk)
        task.delete()
        return redirect('tasks_list_fr_url')
class TaskUpdateFrontendView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'task_track/task_update.html'
    def get(self,request,pk):
        task=Task.objects.get(id=pk)
        serializer=TaskSerializer(task)
        return Response({'serializer':serializer,'task':task})
    def post(self,request,pk):
        task=Task.objects.get(id=pk)
        serializer=TaskSerializer(task,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect(reverse('task_detail_fr_url',kwargs={'pk':task.id}))
        else:
            return Response({'task':task,'serializer':serializer})
class TaskWorkUserFrontendView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'task_track/task_list_user.html'
    def get(self,request):
        if request.GET:
            serializer=TrackTimeSerializer()
            result={}
            for task in Task.objects.all():
                tracks = task.task_tracks.filter(user=User.objects.get(id=request.GET['user']), time_start__range=[request.GET['time_start'], request.GET['time_end']])
                period=0
                if tracks:
                    for track in tracks:
                        if track.time_end is not None:
                            if datetime(track.time_end.year,track.time_end.month,track.time_end.day,track.time_end.hour,track.time_end.minute)<datetime.strptime(request.GET['time_end'].replace('T',' '),'%Y-%m-%d %H:%M'):
                                period+=(track.time_end-track.time_start).seconds
                            else:
                                period += (d_end - datetime(*[int(t) for t in track.time_start.strftime("%Y %m %d %I %M").split()])).seconds
                        else:
                            period+=(datetime.now()-datetime(*[int(t) for t in track.time_start.strftime("%Y %m %d %I %M").split()])).seconds-7200

                        result[task.id]= {'часы':period//3600,'минуты':period//60-(period//3600)*60}
            result=sorted(result.items(), key=lambda x: x[1]['часы']*60+x[1]['минуты'])
            print(result)
            return Response({'serializer': serializer,'result':result})
        else:
            serializer = TrackTimeSerializer()
            return Response({'serializer':serializer})
# class SumTaskWorkUserFrontend(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     template_name = 'task_track/sum_task_list_user.html'
#     def get(self,request):
#         period=0
#         d_start=datetime.strptime(request.data['start'],'%Y-%m-%d %H:%M')
#         d_end = datetime.strptime(request.data['end'],'%Y-%m-%d %H:%M')
#         for task in Task.objects.all():
#             tracks=task.task_tracks.filter(user=User.objects.get(id=request.user.id),time_start__range=[d_start,d_end])
#             if tracks:
#                 for track in tracks:
#                     if track.time_end is not None:
#                         if datetime(*[int(t) for t in track.time_end.strftime("%Y %m %d %H %M").split()])<d_end:
#                             period+=(track.time_end-track.time_start).seconds
#                         else:
#                             period+=(d_end - datetime(*[int(t) for t in track.time_start.strftime("%Y %m %d %I %M").split()])).seconds
#                     else:
#                         period+=(datetime.now()-datetime(*[int(t) for t in track.time_start.strftime("%Y %m %d %I %M").split()])).seconds-7200
#         return Response (f'Трудозатраты с {d_start} до {d_end} составляют {period//3600} часов {period//60-(period//3600)*60} минут')
class IntervalWorkUserFrontendView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'task_track/interval_work_user.html'
    def get(self,request):
        if request.GET:
            serializer = TrackDateSerializer()
            d_start=datetime.strptime(request.GET['time_start'].replace('T',' ')+' 00:00','%Y-%m-%d %H:%M')
            d_end = datetime.strptime(request.GET['time_end'].replace('T',' ')+' 23:59','%Y-%m-%d %H:%M')
            print('sss',d_start,d_end)
            count_days=(d_end-d_start).days+1
            start_period=d_start
            intervals_dict={}
            print(count_days)
            for d in range(1,count_days+1):
                end_period=start_period+timedelta(days=1)
                intervals_dict[str(d)] = {'start_interval': start_period,'end_interval': end_period, 'tasks': []}
                start_period=end_period
            intervals_sort=sorted(intervals_dict.items(), key=lambda x: x[0])
            tracks=Track.objects.filter(user=User.objects.get(id=request.GET['user']),time_start__range=(datetime(2024,1,1,0,0),intervals_sort[-1][1]['end_interval']))
            print('tracks',tracks)
            for key,value in intervals_dict.items():
                tracks_lst=[]
                for track in Track.objects.filter(user=User.objects.get(id=request.GET['user']),
                                     time_start__range=(datetime(2023, 1, 1, 0, 0), intervals_dict[key]['end_interval']),
                                     time_end__range=(intervals_dict[key]['start_interval'], datetime(2026, 1, 1, 0, 0))):
                    track_dict={}
                    track_dict['user']=track.user.id
                    track_dict['task']=TaskSerializer(track.task).data
                    if datetime(*[int(t) for t in track.time_start.strftime("%Y %m %d %H %M").split()])>intervals_dict[key]['start_interval']:
                        track_dict['time_start']=datetime(*[int(t) for t in track.time_start.strftime("%Y %m %d %H %M").split()])
                    else:
                        track_dict['time_start']=intervals_dict[key]['start_interval']
                    if datetime(*[int(t) for t in track.time_end.strftime("%Y %m %d %H %M").split()]) <  \
                                intervals_dict[key]['end_interval']:
                            track_dict['time_end'] = datetime(
                                *[int(t) for t in track.time_end.strftime("%Y %m %d %H %M").split()])
                    else:
                            track_dict['time_end'] = intervals_dict[key]['end_interval']
                    tracks_lst.append(track_dict)
                intervals_dict[key]['tasks']=tracks_lst
            print(intervals_dict)
            print('vv',[list(v.values()) for v in list(intervals_dict.values())])
            context={
                'serializer':serializer,
                'intervals_dict':[list(v.values()) for v in list(intervals_dict.values())],
                'time_start':list(intervals_dict.values())[0]['start_interval'],
                'time_end':list(intervals_dict.values())[-1]['end_interval'],
                'user':User.objects.get(id=request.GET['user']),
            }
            return Response (context)
        else:
            serializer = TrackDateSerializer()
            return Response({'serializer':serializer})


class DeleteUserTracksFrontandView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'task_track/tracks_delete.html'
    def get(self,request):
        serializer=TrackUserSerializer()
        return Response({'serializer':serializer})

    def post(self,request):
        user=User.objects.get(id=request.data['user'])
        tracks=Track.objects.filter(user=user)
        serializer = TrackUserSerializer(data=request.data)
        if serializer.is_valid():
            for track in tracks:
                track.delete()
            return redirect(reverse('user_tracks_list_fr_url',kwargs={'pk':request.data['user']}))
        else:
            return Response({'serializer':serializer})
