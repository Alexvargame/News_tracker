from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse

from datetime import datetime

class Task(models.Model):

    name=models.CharField(max_length=50)
    discription=models.TextField()

    class Meta:
        verbose_name='Задача'
        verbose_name_plural='Задачи'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('task_detail_fr_url',kwargs={'pk':self.id})
    def get_delete_url(self):
        return reverse('task_delete_fr_url',kwargs={'pk':self.id})
    def get_update_url(self):
        return reverse('task_update_fr_url',kwargs={'pk':self.id})

class Track(models.Model):

    user=models.ForeignKey(User,related_name='user_tracks',on_delete=models.DO_NOTHING)
    task=models.ForeignKey(Task,related_name='task_tracks',on_delete=models.DO_NOTHING)
    time_start=models.DateTimeField(default=datetime.now())
    time_end=models.DateTimeField(default=datetime(datetime.now().year,datetime.now().month,datetime.now().day,23,59),null=True,blank=True)

    class Meta:
        verbose_name = 'Трекер'
        verbose_name_plural = 'Трекеры'

    def __str__(self):
        return f'{self.id}:{self.user}-{self.task}'
    def get_absolute_url(self):
        return reverse('track_detail_fr_url',kwargs={'pk':self.id})
    def get_update_url(self):
        return reverse('track_update_fr_url',kwargs={'pk':self.id})
    def get_delete_url(self):
        return reverse('track_delete_fr_url',kwargs={'pk':self.id})



