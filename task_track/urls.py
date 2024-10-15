from django.urls import path
from .views import *

urlpatterns = [
    path('', main_page,name='main_page_url'),
    path('api-auth/track/create/',CreateTrack.as_view(),name='create_track_url'),
    path('api-auth/track/<int:pk>/stop/',StopTracker.as_view(),name='stop_track_url'),

    path('api-auth/<int:pk>/tracks/',ListUserTrackers.as_view(),name='list_user_tracks_url'),
    path('api-auth/tracks/',ListTrackers.as_view(),name='list_tracks_url'),
    path('api-auth/tasks/',ListTasks.as_view(),name='list_tasks_url'),


    path('api-auth/work/<int:pk>/tasks/',TaskWorkUser.as_view(),name='work_user_list_tasks_url'),
    path('api-auth/work/<int:pk>/tasks_sum/',SumTaskWorkUser.as_view(),name='sum_work_user_list_tasks_url'),
    path('api-auth/work/<int:pk>/intervals/',IntervalWorkUser.as_view(),name='work_user_list_intervals_url'),
    path('api-auth/work/<int:pk>/tracks_delete/',DeleteUserTracks.as_view(),name='delete_user_tracks_url'),


    path('tracks/create/',CreateTrackFrontendView.as_view(),name='track_create_fr_url'),
    path('tracks/list/',ListTrackersFrontendView.as_view(),name='tracks_list_fr_url'),
    path('tracks/<int:pk>/list/',ListUserTrackersFrontendView.as_view(),name='user_tracks_list_fr_url'),
    path('tracks/<int:pk>/',TrackDetailFrontendView.as_view(),name='track_detail_fr_url'),
    path('tracks/<int:pk>/stop/',StopTrackerFrontendView.as_view(),name='track_stop_fr_url'),
    path('tracks/<int:pk>/update/',TrackUpdateFrontendView.as_view(),name='track_update_fr_url'),
    path('tracks/<int:pk>/delete/',TrackDeleteFrontendView.as_view(),name='track_delete_fr_url'),
    path('tracks/delete/',DeleteUserTracksFrontandView.as_view(),name='tracks_delete_fr_url'),

    path('tasks/list/',ListTasksFrontendView.as_view(),name='tasks_list_fr_url'),
    path('tasks/create/',TaskCreateFrontendView.as_view(),name='task_create_fr_url'),
    path('tasks/list/<int:pk>/',TaskDetailFrontendView.as_view(),name='task_detail_fr_url'),
    path('tasks/<int:pk>/delete/',TaskDeleteFrontendView.as_view(),name='task_delete_fr_url'),
    path('tasks/<int:pk>/update/',TaskUpdateFrontendView.as_view(),name='task_update_fr_url'),

    path('tasks/work/tasks/',TaskWorkUserFrontendView.as_view(),name='work_user_list_tasks_fr_url'),
    path('tasks/work/intervals/',IntervalWorkUserFrontendView.as_view(),name='intervals_work_fr_url'),

]
