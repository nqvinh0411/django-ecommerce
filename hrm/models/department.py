from django.db import models
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    """
    Model representing a department within the organization.
    Departments serve as organizational units that group employees.
    """
    name = models.CharField(_('Name'), max_length=100)
    code = models.CharField(_('Department Code'), max_length=20, unique=True)
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='child_departments',
        verbose_name=_('Parent Department')
    )
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_department',
        verbose_name=_('Department Manager')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        ordering = ['name']

    def __str__(self):
        return self.name
