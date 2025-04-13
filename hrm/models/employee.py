from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Employee(models.Model):
    """
    Model representing an employee in the organization.
    Contains personal, contact, and employment details.
    """
    # Employment Status Choices
    EMPLOYMENT_STATUS_FULL_TIME = 'full_time'
    EMPLOYMENT_STATUS_PART_TIME = 'part_time'
    EMPLOYMENT_STATUS_CONTRACT = 'contract'
    EMPLOYMENT_STATUS_INTERN = 'intern'
    EMPLOYMENT_STATUS_PROBATION = 'probation'
    EMPLOYMENT_STATUS_TERMINATED = 'terminated'
    
    EMPLOYMENT_STATUS_CHOICES = [
        (EMPLOYMENT_STATUS_FULL_TIME, _('Full Time')),
        (EMPLOYMENT_STATUS_PART_TIME, _('Part Time')),
        (EMPLOYMENT_STATUS_CONTRACT, _('Contract')),
        (EMPLOYMENT_STATUS_INTERN, _('Intern')),
        (EMPLOYMENT_STATUS_PROBATION, _('Probation')),
        (EMPLOYMENT_STATUS_TERMINATED, _('Terminated')),
    ]
    
    # Personal Information
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        verbose_name=_('User Account'),
        null=True,
        blank=True
    )
    employee_id = models.CharField(_('Employee ID'), max_length=20, unique=True)
    first_name = models.CharField(_('First Name'), max_length=50)
    last_name = models.CharField(_('Last Name'), max_length=50)
    date_of_birth = models.DateField(_('Date of Birth'), null=True, blank=True)
    gender = models.CharField(
        _('Gender'),
        max_length=10,
        choices=[('male', _('Male')), ('female', _('Female')), ('other', _('Other'))],
        blank=True
    )
    
    # Contact Information
    email = models.EmailField(_('Email'), max_length=255)
    phone = models.CharField(_('Phone Number'), max_length=20, blank=True)
    address = models.TextField(_('Address'), blank=True)
    emergency_contact_name = models.CharField(_('Emergency Contact Name'), max_length=100, blank=True)
    emergency_contact_phone = models.CharField(_('Emergency Contact Phone'), max_length=20, blank=True)
    
    # Employment Details
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees',
        verbose_name=_('Department')
    )
    position = models.ForeignKey(
        'Position',
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees',
        verbose_name=_('Position')
    )
    employment_status = models.CharField(
        _('Employment Status'),
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default=EMPLOYMENT_STATUS_FULL_TIME
    )
    hire_date = models.DateField(_('Hire Date'))
    termination_date = models.DateField(_('Termination Date'), null=True, blank=True)
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name=_('Supervisor')
    )
    
    # Additional Information
    profile_picture = models.ImageField(
        _('Profile Picture'),
        upload_to='employees/profile_pictures/',
        blank=True,
        null=True
    )
    notes = models.TextField(_('Notes'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
