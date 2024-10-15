from django.contrib import admin
from .models import Task,Track

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id','name','discription')

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('id','user','task','time_start','time_end')
