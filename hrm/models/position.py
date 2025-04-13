from django.db import models
from django.utils.translation import gettext_lazy as _


class Position(models.Model):
    """
    Model representing a job position within the organization.
    Positions define the roles and responsibilities of employees.
    """
    title = models.CharField(_('Title'), max_length=100)
    code = models.CharField(_('Position Code'), max_length=20, unique=True)
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name=_('Department')
    )
    description = models.TextField(_('Description'), blank=True)
    requirements = models.TextField(_('Requirements'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    min_salary = models.DecimalField(
        _('Minimum Salary'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    max_salary = models.DecimalField(
        _('Maximum Salary'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Position')
        verbose_name_plural = _('Positions')
        ordering = ['title']
        unique_together = [['title', 'department']]

    def __str__(self):
        return f"{self.title} ({self.department})"
