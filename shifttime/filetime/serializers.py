from rest_framework import serializers
from .models import Lesson, ScheduleLesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('name', 'teacher', 'room')

class ScheduleLessonSerializer(serializers.ModelSerializer):
    # Извлекаем дату из связанной модели Schedule
    day = serializers.DateField(source='schedule.day')
    lesson = LessonSerializer()

    class Meta:
        model = ScheduleLesson
        fields = ('day', 'lesson', 'group', 'order')
