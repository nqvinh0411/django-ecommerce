from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class LeaveRequest(models.Model):
    """
    Model representing employee leave/time-off requests.
    Tracks different types of leave and approval status.
    """
    # Leave Type Choices
    LEAVE_TYPE_ANNUAL = 'annual'
    LEAVE_TYPE_SICK = 'sick'
    LEAVE_TYPE_MATERNITY = 'maternity'
    LEAVE_TYPE_PATERNITY = 'paternity'
    LEAVE_TYPE_BEREAVEMENT = 'bereavement'
    LEAVE_TYPE_UNPAID = 'unpaid'
    LEAVE_TYPE_OTHER = 'other'
    
    LEAVE_TYPE_CHOICES = [
        (LEAVE_TYPE_ANNUAL, _('Annual Leave')),
        (LEAVE_TYPE_SICK, _('Sick Leave')),
        (LEAVE_TYPE_MATERNITY, _('Maternity Leave')),
        (LEAVE_TYPE_PATERNITY, _('Paternity Leave')),
        (LEAVE_TYPE_BEREAVEMENT, _('Bereavement Leave')),
        (LEAVE_TYPE_UNPAID, _('Unpaid Leave')),
        (LEAVE_TYPE_OTHER, _('Other')),
    ]
    
    # Status Choices
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_APPROVED, _('Approved')),
        (STATUS_REJECTED, _('Rejected')),
        (STATUS_CANCELLED, _('Cancelled')),
    ]
    
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name=_('Employee')
    )
    leave_type = models.CharField(
        _('Leave Type'),
        max_length=20,
        choices=LEAVE_TYPE_CHOICES
    )
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    half_day = models.BooleanField(
        _('Half Day'),
        default=False,
        help_text=_('If checked, this leave request is for half a day')
    )
    reason = models.TextField(_('Reason'), blank=True)
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    reviewed_by = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leave_requests',
        verbose_name=_('Reviewed By')
    )
    reviewed_at = models.DateTimeField(_('Reviewed At'), null=True, blank=True)
    reviewer_comments = models.TextField(_('Reviewer Comments'), blank=True)
    attachment = models.FileField(
        _('Attachment'),
        upload_to='leave_requests/attachments/',
        blank=True,
        null=True,
        help_text=_('Supporting documents (e.g., medical certificate)')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Leave Request')
        verbose_name_plural = _('Leave Requests')
        ordering = ['-start_date', 'status']

    def __str__(self):
        return f"{self.employee} - {self.get_leave_type_display()} ({self.start_date.strftime('%Y-%m-%d')})"
    
    def clean(self):
        """
        Custom validation to ensure end_date is after or equal to start_date.
        """
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(_('End date must be after or equal to start date.'))
    
    @property
    def duration_days(self):
        """
        Calculate the duration of leave in days.
        """
        if self.start_date and self.end_date:
            days = (self.end_date - self.start_date).days + 1
            return days * 0.5 if self.half_day else days
        return 0
