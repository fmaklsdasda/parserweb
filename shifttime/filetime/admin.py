from django.contrib import admin
from .models import FileTime, Lesson, Schedule, ScheduleLesson

class ScheduleLessonInline(admin.TabularInline):
    model = ScheduleLesson
    extra = 1 
    ordering = ('order',)
    fields = ('lesson', 'order')


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('day',)
    list_filter = ('day',)
    search_fields = ('day',)
    inlines = [ScheduleLessonInline]


class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'room')
    list_filter = ('teacher',)
    search_fields = ('name', 'teacher', 'room')


class FileTimeAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'file')
    list_filter = ('start_date', 'end_date')
    search_fields = ('start_date', 'end_date')
    fields = ('start_date', 'end_date', 'file', 'schedules')

    def get_schedules(self, obj):
        return ", ".join(str(schedule.day) for schedule in obj.schedules.all())
    get_schedules.short_description = "Расписания"


class ScheduleLessonAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'lesson', 'group', 'order')
    list_filter = ('schedule', 'group', 'order')
    search_fields = ('schedule__day', 'group', 'lesson__name')


admin.site.register(Lesson, LessonAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(FileTime, FileTimeAdmin)
admin.site.register(ScheduleLesson, ScheduleLessonAdmin)
