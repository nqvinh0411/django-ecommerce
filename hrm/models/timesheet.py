from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone


class Timesheet(models.Model):
    """
    Model representing employee time tracking.
    Records check-in and check-out times for calculating work hours.
    """
    # Timesheet Status Choices
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_APPROVED, _('Approved')),
        (STATUS_REJECTED, _('Rejected')),
    ]
    
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='timesheets',
        verbose_name=_('Employee')
    )
    date = models.DateField(_('Date'), default=timezone.now)
    check_in = models.DateTimeField(_('Check In Time'))
    check_out = models.DateTimeField(_('Check Out Time'), null=True, blank=True)
    break_duration = models.PositiveIntegerField(
        _('Break Duration (minutes)'),
        default=0
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    approved_by = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_timesheets',
        verbose_name=_('Approved By')
    )
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Timesheet')
        verbose_name_plural = _('Timesheets')
        ordering = ['-date', '-check_in']
        unique_together = [['employee', 'date', 'check_in']]

    def __str__(self):
        return f"{self.employee} - {self.date.strftime('%Y-%m-%d')}"
    
    def clean(self):
        """
        Custom validation to ensure check_out is after check_in.
        """
        if self.check_in and self.check_out and self.check_in >= self.check_out:
            raise ValidationError(_('Check-out time must be after check-in time.'))
    
    @property
    def work_duration(self):
        """
        Calculate work duration in hours, excluding breaks.
        """
        if self.check_in and self.check_out:
            total_seconds = (self.check_out - self.check_in).total_seconds()
            break_seconds = self.break_duration * 60
            work_seconds = max(0, total_seconds - break_seconds)
            return round(work_seconds / 3600, 2)  # Convert to hours
        return 0
