# urls.py
from django.urls import path
from .views import GroupScheduleView

urlpatterns = [
    path('api/schedule/', GroupScheduleView.as_view(), name='group_schedule'),
]