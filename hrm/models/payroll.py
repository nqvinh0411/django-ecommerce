from django.db import models
from django.utils.translation import gettext_lazy as _


class Payroll(models.Model):
    """
    Model representing payroll processing.
    Records salary payments to employees for specific pay periods.
    """
    # Payment Status Choices
    STATUS_DRAFT = 'draft'
    STATUS_PENDING = 'pending'
    STATUS_PROCESSED = 'processed'
    STATUS_PAID = 'paid'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, _('Draft')),
        (STATUS_PENDING, _('Pending')),
        (STATUS_PROCESSED, _('Processed')),
        (STATUS_PAID, _('Paid')),
        (STATUS_CANCELLED, _('Cancelled')),
    ]
    
    # Payment Method Choices
    PAYMENT_METHOD_BANK_TRANSFER = 'bank_transfer'
    PAYMENT_METHOD_CASH = 'cash'
    PAYMENT_METHOD_CHECK = 'check'
    
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_BANK_TRANSFER, _('Bank Transfer')),
        (PAYMENT_METHOD_CASH, _('Cash')),
        (PAYMENT_METHOD_CHECK, _('Check')),
    ]
    
    payroll_period = models.CharField(_('Payroll Period'), max_length=50)
    start_date = models.DateField(_('Period Start Date'))
    end_date = models.DateField(_('Period End Date'))
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='payrolls',
        verbose_name=_('Employee')
    )
    salary = models.ForeignKey(
        'Salary',
        on_delete=models.SET_NULL,
        null=True,
        related_name='payrolls',
        verbose_name=_('Salary Structure')
    )
    gross_amount = models.DecimalField(
        _('Gross Amount'),
        max_digits=12,
        decimal_places=2
    )
    deductions = models.JSONField(
        _('Deductions'),
        default=dict,
        help_text=_('All deductions as key-value pairs (e.g., {"tax": 150000, "insurance": 100000})')
    )
    allowances = models.JSONField(
        _('Allowances'),
        default=dict,
        help_text=_('All allowances as key-value pairs (e.g., {"overtime": 200000, "bonus": 500000})')
    )
    net_amount = models.DecimalField(
        _('Net Amount'),
        max_digits=12,
        decimal_places=2
    )
    overtime_hours = models.DecimalField(
        _('Overtime Hours'),
        max_digits=6,
        decimal_places=2,
        default=0
    )
    overtime_rate = models.DecimalField(
        _('Overtime Rate'),
        max_digits=5,
        decimal_places=2,
        default=1.5
    )
    payment_date = models.DateField(_('Payment Date'), null=True, blank=True)
    payment_method = models.CharField(
        _('Payment Method'),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_METHOD_BANK_TRANSFER
    )
    payment_reference = models.CharField(_('Payment Reference'), max_length=100, blank=True)
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )
    approved_by = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_payrolls',
        verbose_name=_('Approved By')
    )
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Payroll')
        verbose_name_plural = _('Payrolls')
        ordering = ['-payroll_period', 'employee']
        unique_together = [['employee', 'payroll_period']]

    def __str__(self):
        return f"{self.employee} - {self.payroll_period} ({self.net_amount})"
    
    @property
    def total_deductions(self):
        """Calculate the total of all deductions."""
        return sum(self.deductions.values())
    
    @property
    def total_allowances(self):
        """Calculate the total of all allowances."""
        return sum(self.allowances.values())
    
    def calculate_net_amount(self):
        """Calculate the net amount based on gross amount, deductions, and allowances."""
        net = self.gross_amount - self.total_deductions + self.total_allowances
        return max(0, net)
