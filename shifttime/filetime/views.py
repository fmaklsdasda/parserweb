from django.shortcuts import render
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Schedule, ScheduleLesson
from .serializers import ScheduleLessonSerializer

class GroupScheduleView(APIView):
    """
    API для получения всех занятий для указанной группы на конкретную дату.
    Параметры запроса:
      - group: идентификатор группы
      - date: дата в формате YYYY-MM-DD
    """
    def get(self, request, *args, **kwargs):
        group = request.query_params.get('group')
        date_str = request.query_params.get('date')
        if not group or not date_str:
            return Response(
                {'error': 'Параметры "group" и "date" обязательны.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            day = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Дата должна быть в формате YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Находим расписание на указанный день
        schedules = Schedule.objects.filter(day=day)
        # Отбираем занятия для заданной группы (через связующую модель ScheduleLesson)
        lessons = ScheduleLesson.objects.filter(schedule__in=schedules, group=group).order_by('order')
        serializer = ScheduleLessonSerializer(lessons, many=True)
        return Response(serializer.data)

