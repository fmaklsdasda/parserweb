from datetime import date, timedelta
from typing import Any, Dict, List
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from filetime.utils.timeparser import ScheduleParser


def next_week_start() -> date:
    today: date = timezone.now().date()
    next_monday: date = today + timedelta(days=(7 - today.weekday()))
    return next_monday


def next_week_end() -> date:
    next_monday: date = next_week_start()
    next_friday: date = next_monday + timedelta(days=6)
    return next_friday


class Lesson(models.Model):
    name = models.CharField(max_length=255, verbose_name="Предмет")
    room = models.CharField(max_length=50, verbose_name="Кабинет")
    teacher = models.CharField(max_length=100, verbose_name="ФИО преподавателя")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"


class Schedule(models.Model):
    day = models.DateField(verbose_name="День")
    lessons = models.ManyToManyField(
        Lesson, through="ScheduleLesson", related_name="schedules", verbose_name="Пары"
    )

    def __str__(self) -> str:
        return f"Schedule for {self.day}"

    class Meta:
        ordering = ["day"]
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"


class ScheduleLesson(models.Model):
    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, verbose_name="Schedule"
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="Lesson")
    group = models.CharField(max_length=50, verbose_name="Группа")
    order = models.PositiveSmallIntegerField(
        verbose_name="Order",
        help_text="Lesson order for the day (e.g. 1st period, 2nd period, etc.)",
    )

    def __str__(self) -> str:
        return f"{self.lesson} on {self.schedule.day} (Order {self.order})"

    class Meta:
        ordering = ["order"]
        verbose_name = "Scheduled Lesson"
        verbose_name_plural = "Scheduled Lessons"
        # unique_together = (("schedule", "order"),)


class FileTime(models.Model):
    start_date = models.DateField(default=next_week_start, verbose_name="Дата начала")
    end_date = models.DateField(default=next_week_end, verbose_name="Дата завершения")
    file = models.FileField(upload_to="uploads/", verbose_name="Файл")
    schedules = models.ManyToManyField(
        Schedule, verbose_name="Расписание", blank=True, null=True
    )

    def __str__(self) -> str:
        return f"FileTime: {self.start_date} - {self.end_date}"

    def clean(self) -> None:
        if self.start_date >= self.end_date:
            raise ValidationError("Start date must be before end date.")

        overlapping = FileTime.objects.filter(
            start_date__lt=self.end_date, end_date__gt=self.start_date
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)
        if overlapping.exists():
            raise ValidationError("Time interval overlaps with an existing record.")

        # if self.pk:
        #    for schedule in self.schedules.all():
        #        if schedule.day < self.start_date or schedule.day > self.end_date:
        #            raise ValidationError(
        #                f"Schedule day {schedule.day} must be within the FileTime interval."
        #            )

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "FileTime"
        verbose_name_plural = "FileTimes"


def save_schedule_from_parser(
    filetime_instance: FileTime, parser: ScheduleParser
) -> None:

    schedule_data: Dict[date, Dict[int, str]] = {}

    for row in parser.days:
        for pair in row:
            dt: date = pair["dt"]
            group: int = pair["group"]

            if dt not in schedule_data:
                schedule_data[dt] = {}

            schedule_data[dt][group] = pair

    for dt, lessons in schedule_data.items():
        schedule = Schedule.objects.create(day=dt)
        for group, pair in lessons.items():
            lesson, _ = Lesson.objects.get_or_create(
                name=pair["subj"], teacher=pair["teacher"], defaults={"room": ""}
            )
            ScheduleLesson.objects.create(
                schedule=schedule, lesson=lesson, order=pair["lesson_num"], group=group
            )
        filetime_instance.schedules.add(schedule)


@receiver(post_save, sender=FileTime)
def post_process_document(
    sender: Any, instance: FileTime, created: bool, **kwargs: Any
) -> None:
    if created and instance.file:
        parser: ScheduleParser = ScheduleParser(instance.file.path)
        parser.parse_schedule()
        save_schedule_from_parser(instance, parser)
