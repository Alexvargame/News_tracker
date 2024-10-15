from .models import Track,Task
from users.models import User
from datetime import date, datetime, timedelta


def weak_works(request):
    result = {}
    period = 0
    for task in Task.objects.all():
        tracks = task.task_tracks.filter(user=User.objects.get(id=request.user.id),
                                         time_start__range=[datetime.now()- timedelta(days=7), datetime.now()])
        if tracks:
            for track in tracks:
                period += (track.time_end - track.time_start).seconds
                result[task.id] = {'часы': period // 3600, 'минуты': period // 60 - (period // 3600) * 60}
    result = sorted(result.items(), key=lambda x: x[1]['часы'] * 60 + x[1]['минуты'])
    return {'weak_works':f"часы: {period // 3600}, минуты: {period // 60 - (period // 3600) * 60}"}
