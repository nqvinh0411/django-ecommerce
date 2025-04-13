from django.db import models
from django.utils.translation import gettext_lazy as _


class Holiday(models.Model):
    """
    Model representing holidays and days off.
    Used for payroll calculations and timesheet validation.
    """
    # Holiday Type Choices
    HOLIDAY_TYPE_PUBLIC = 'public'
    HOLIDAY_TYPE_COMPANY = 'company'
    
    HOLIDAY_TYPE_CHOICES = [
        (HOLIDAY_TYPE_PUBLIC, _('Public Holiday')),
        (HOLIDAY_TYPE_COMPANY, _('Company Holiday')),
    ]
    
    name = models.CharField(_('Holiday Name'), max_length=100)
    date = models.DateField(_('Date'))
    holiday_type = models.CharField(
        _('Holiday Type'),
        max_length=20,
        choices=HOLIDAY_TYPE_CHOICES,
        default=HOLIDAY_TYPE_PUBLIC
    )
    description = models.TextField(_('Description'), blank=True)
    is_paid = models.BooleanField(_('Paid Holiday'), default=True)
    recurring = models.BooleanField(
        _('Recurring Yearly'),
        default=False,
        help_text=_('If checked, this holiday repeats every year on the same date')
    )
    applicable_departments = models.ManyToManyField(
        'Department',
        related_name='holidays',
        verbose_name=_('Applicable Departments'),
        blank=True,
        help_text=_('Leave empty if applies to all departments')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Holiday')
        verbose_name_plural = _('Holidays')
        ordering = ['date']
        unique_together = [['name', 'date']]

    def __str__(self):
        return f"{self.name} ({self.date.strftime('%Y-%m-%d')})"
