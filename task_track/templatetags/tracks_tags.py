from django import template
from ..models import Task,Track
#from users.model import User
from datetime import datetime,timedelta
register=template.Library()

@register.simple_tag
def total_costs():
    result = {}
    for task in Task.objects.all():
        tracks = task.task_tracks.filter(user=User.objects.get(id=request.GET['user']),
                                         time_start__range=[datetime.now-timedelta(days=7), datetime.now])
        print(tracks)
        period = 0
        if tracks:
            for track in tracks:
                if track.time_end is not None:
                    if datetime(track.time_end.year, track.time_end.month, track.time_end.day, track.time_end.hour,
                                track.time_end.minute) < datetime.strptime(request.GET['time_end'].replace('T', ' '),
                                                                           '%Y-%m-%d %H:%M'):
                        period += (track.time_end - track.time_start).seconds
                    else:
                        period += (d_end - datetime(
                            *[int(t) for t in track.time_start.strftime("%Y %m %d %I %M").split()])).seconds
                else:
                    period += (datetime.now() - datetime(
                        *[int(t) for t in track.time_start.strftime("%Y %m %d %I %M").split()])).seconds - 7200

                result[task.id] = {'часы': period // 3600, 'минуты': period // 60 - (period // 3600) * 60}
    result = sorted(result.items(), key=lambda x: x[1]['часы'] * 60 + x[1]['минуты'])
    print(result)
    return result

#
# @register.simple_tag
# def total_addmoneys():
#     return AddMoney.objects.count()
#
# @register.inclusion_tag('costs/latest_costs.html')
# def show_latest_costs(count=5):
#     latest_costs=Cost.objects.order_by('-cost_date')[:count]
#
#     return {'latest_costs':latest_costs}
