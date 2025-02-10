from django.contrib import admin
from .models import FileTime, Lesson, Schedule, ScheduleLesson

# Inline admin to manage ScheduleLesson objects within a Schedule
class ScheduleLessonInline(admin.TabularInline):
    model = ScheduleLesson
    extra = 1  # Number of extra blank forms to display
    ordering = ('order',)
    fields = ('lesson', 'order')


# Admin for the Schedule model
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('day',)
    list_filter = ('day',)
    search_fields = ('day',)
    inlines = [ScheduleLessonInline]


# Admin for the Lesson model
class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'group', 'room')
    list_filter = ('teacher', 'group')
    search_fields = ('name', 'teacher', 'group', 'room')


# Admin for the FileTime model, updated to handle multiple schedules
class FileTimeAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'file')
    list_filter = ('start_date', 'end_date')
    search_fields = ('start_date', 'end_date')
    fields = ('start_date', 'end_date', 'file', 'schedules')

    def get_schedules(self, obj):
        # Return a comma-separated list of schedule days
        return ", ".join(str(schedule.day) for schedule in obj.schedules.all())
    get_schedules.short_description = "Расписания"


# Admin for the ScheduleLesson model (optional registration)
class ScheduleLessonAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'lesson', 'order')
    list_filter = ('schedule', 'order')
    search_fields = ('schedule__day', 'lesson__name')


# Register all models with their corresponding admin classes
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(FileTime, FileTimeAdmin)
admin.site.register(ScheduleLesson, ScheduleLessonAdmin)
