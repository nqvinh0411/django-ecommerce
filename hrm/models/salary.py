from django.db import models
from django.utils.translation import gettext_lazy as _


class Salary(models.Model):
    """
    Model representing employee salary structure.
    Contains base salary and other compensation components.
    """
    # Salary Type Choices
    SALARY_TYPE_MONTHLY = 'monthly'
    SALARY_TYPE_HOURLY = 'hourly'
    SALARY_TYPE_COMMISSION = 'commission'
    
    SALARY_TYPE_CHOICES = [
        (SALARY_TYPE_MONTHLY, _('Monthly')),
        (SALARY_TYPE_HOURLY, _('Hourly')),
        (SALARY_TYPE_COMMISSION, _('Commission')),
    ]
    
    # Currency Choices
    CURRENCY_VND = 'VND'
    CURRENCY_USD = 'USD'
    CURRENCY_EUR = 'EUR'
    
    CURRENCY_CHOICES = [
        (CURRENCY_VND, _('Vietnamese Dong')),
        (CURRENCY_USD, _('US Dollar')),
        (CURRENCY_EUR, _('Euro')),
    ]
    
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='salaries',
        verbose_name=_('Employee')
    )
    salary_type = models.CharField(
        _('Salary Type'),
        max_length=20,
        choices=SALARY_TYPE_CHOICES,
        default=SALARY_TYPE_MONTHLY
    )
    base_salary = models.DecimalField(
        _('Base Salary'),
        max_digits=12,
        decimal_places=2
    )
    currency = models.CharField(
        _('Currency'),
        max_length=3,
        choices=CURRENCY_CHOICES,
        default=CURRENCY_VND
    )
    allowances = models.JSONField(
        _('Allowances'),
        default=dict,
        help_text=_('Additional allowances as key-value pairs (e.g., {"transportation": 500000})')
    )
    deductions = models.JSONField(
        _('Deductions'),
        default=dict,
        help_text=_('Standard deductions as key-value pairs (e.g., {"tax": 150000})')
    )
    effective_date = models.DateField(_('Effective Date'))
    end_date = models.DateField(_('End Date'), null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Salary')
        verbose_name_plural = _('Salaries')
        ordering = ['-effective_date']
        unique_together = [['employee', 'effective_date']]

    def __str__(self):
        return f"{self.employee} - {self.base_salary} {self.currency} ({self.get_salary_type_display()})"
    
    @property
    def total_allowances(self):
        """Calculate the total of all allowances."""
        return sum(self.allowances.values())
    
    @property
    def total_deductions(self):
        """Calculate the total of all deductions."""
        return sum(self.deductions.values())
    
    @property
    def net_salary(self):
        """Calculate the net salary (base + allowances - deductions)."""
        return self.base_salary + self.total_allowances - self.total_deductions
