from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from filetime.utils.timeparser import ScheduleParser

def next_week_start():
    today = timezone.now().date()
    next_monday = today + timedelta(days=(7 - today.weekday()))
    return next_monday

def next_week_end():
    next_monday = next_week_start()
    next_friday = next_monday + timedelta(days=6)
    return next_friday


class Lesson(models.Model):
    name = models.CharField(max_length=255, verbose_name="Предмет")
    room = models.CharField(max_length=50, verbose_name="Кабинет")
    teacher = models.CharField(max_length=100, verbose_name="ФИО преподавателя")
    group = models.CharField(max_length=50, verbose_name="Группа")

    def __str__(self):
        return self.name  

    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"


class Schedule(models.Model):
    day = models.DateField(verbose_name="День")
    lessons = models.ManyToManyField(
        Lesson,
        through='ScheduleLesson',
        related_name='schedules',
        verbose_name="Пары"
    )

    def __str__(self):
        return f"Schedule for {self.day}"

    class Meta:
        ordering = ['day']
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"


class ScheduleLesson(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name="Schedule")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="Lesson")
    order = models.PositiveSmallIntegerField(
        verbose_name="Order",
        help_text="Lesson order for the day (e.g. 1st period, 2nd period, etc.)"
    )

    def __str__(self):
        return f"{self.lesson} on {self.schedule.day} (Order {self.order})"

    class Meta:
        ordering = ['order']
        verbose_name = "Scheduled Lesson"
        verbose_name_plural = "Scheduled Lessons"
        unique_together = (('schedule', 'order'),)  


class FileTime(models.Model):
    start_date = models.DateField(default=next_week_start, verbose_name="Дата начала")
    end_date = models.DateField(default=next_week_end, verbose_name="Дата завершения")
    file = models.FileField(upload_to='uploads/', verbose_name="Файл")
    schedules = models.ManyToManyField(Schedule, verbose_name="Расписание")

    def __str__(self):
        return f"FileTime: {self.start_date} - {self.end_date}"

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("Start date must be before end date.")

        overlapping = FileTime.objects.filter(
            start_date__lt=self.end_date,
            end_date__gt=self.start_date
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)
        if overlapping.exists():
            raise ValidationError("Time interval overlaps with an existing record.")

        # Validate that each associated schedule's day is within the FileTime interval.
        # Note: For a new FileTime instance (unsaved), the many-to-many data is not yet available.
        #if self.pk:
        #    for schedule in self.schedules.all():
        #        if schedule.day < self.start_date or schedule.day > self.end_date:
        #           raise ValidationError(
        #                f"Schedule day {schedule.day} must be within the FileTime interval."
        #            )

    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "FileTime"
        verbose_name_plural = "FileTimes"


@receiver(post_save, sender=FileTime)
def post_process_document(sender, instance, created, **kwargs):
    if created and instance.file:
        parser = ScheduleParser(instance.file.path)
        parser.parse_schedule()
        print(parser.days)