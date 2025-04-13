from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class WorkSchedule(models.Model):
    """
    Model representing work schedules for employees.
    Defines when employees are expected to work.
    """
    # Schedule Type Choices
    SCHEDULE_TYPE_REGULAR = 'regular'
    SCHEDULE_TYPE_SHIFT = 'shift'
    SCHEDULE_TYPE_FLEXIBLE = 'flexible'
    
    SCHEDULE_TYPE_CHOICES = [
        (SCHEDULE_TYPE_REGULAR, _('Regular')),
        (SCHEDULE_TYPE_SHIFT, _('Shift')),
        (SCHEDULE_TYPE_FLEXIBLE, _('Flexible')),
    ]
    
    # Days of the Week
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
    
    DAY_CHOICES = [
        (MONDAY, _('Monday')),
        (TUESDAY, _('Tuesday')),
        (WEDNESDAY, _('Wednesday')),
        (THURSDAY, _('Thursday')),
        (FRIDAY, _('Friday')),
        (SATURDAY, _('Saturday')),
        (SUNDAY, _('Sunday')),
    ]
    
    name = models.CharField(_('Schedule Name'), max_length=100)
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        related_name='work_schedules',
        verbose_name=_('Department'),
        null=True,
        blank=True
    )
    schedule_type = models.CharField(
        _('Schedule Type'),
        max_length=20,
        choices=SCHEDULE_TYPE_CHOICES,
        default=SCHEDULE_TYPE_REGULAR
    )
    start_time = models.TimeField(_('Start Time'))
    end_time = models.TimeField(_('End Time'))
    working_days = models.JSONField(
        _('Working Days'),
        help_text=_('Days of the week when this schedule applies'),
        default=list
    )
    break_duration = models.PositiveIntegerField(
        _('Break Duration (minutes)'),
        default=60,
        validators=[MinValueValidator(0), MaxValueValidator(240)]
    )
    is_active = models.BooleanField(_('Active'), default=True)
    effective_date = models.DateField(_('Effective Date'))
    expiration_date = models.DateField(_('Expiration Date'), null=True, blank=True)
    description = models.TextField(_('Description'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Work Schedule')
        verbose_name_plural = _('Work Schedules')
        ordering = ['name']

    def __str__(self):
        return self.name
