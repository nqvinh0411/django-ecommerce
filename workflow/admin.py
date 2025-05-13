from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import (
    Workflow, WorkflowStep, WorkflowTransition, WorkflowAction,
    WorkflowInstance, WorkflowStepLog, WorkflowActorConfig,
    WorkflowConditionContext
)


class WorkflowActorConfigInline(admin.TabularInline):
    """Inline admin for WorkflowActorConfig within WorkflowStep."""
    model = WorkflowActorConfig
    extra = 1
    fields = ['actor_type', 'user', 'group', 'role_name', 'dynamic_expression']
    
    def get_queryset(self, request):
        """Prefetch related objects for better performance."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'group')


class WorkflowActionInline(admin.TabularInline):
    """Inline admin for WorkflowAction within WorkflowStep."""
    model = WorkflowAction
    extra = 1
    fields = [
        'name', 'action_type', 'trigger_point', 'configuration', 
        'is_async', 'order', 'is_active'
    ]


class WorkflowStepInline(admin.TabularInline):
    """Inline admin for WorkflowStep within Workflow."""
    model = WorkflowStep
    extra = 1
    fields = [
        'name', 'order', 'is_start', 'is_end', 
        'wait_all', 'wait_any', 'auto_proceed'
    ]
    readonly_fields = ['transitions_count']
    
    def transitions_count(self, obj):
        """Count of transitions for this step."""
        if obj.pk:
            outgoing = obj.outgoing_transitions.count()
            incoming = obj.incoming_transitions.count()
            return f"{outgoing} out, {incoming} in"
        return "—"
    transitions_count.short_description = _("Transitions")


class WorkflowTransitionInline(admin.TabularInline):
    """Inline admin for WorkflowTransition within WorkflowStep (outgoing)."""
    model = WorkflowTransition
    fk_name = 'source_step'
    extra = 1
    fields = ['name', 'target_step', 'condition_expression', 'priority']


class WorkflowConditionContextInline(admin.TabularInline):
    """Inline admin for WorkflowConditionContext within Workflow."""
    model = WorkflowConditionContext
    extra = 1
    fields = ['name', 'description', 'variables']


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    """Admin interface for Workflow model."""
    list_display = [
        'name', 'content_type', 'version', 'is_active', 
        'steps_count', 'created_at', 'updated_at'
    ]
    list_filter = ['is_active', 'content_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    fieldsets = [
        (None, {
            'fields': ['name', 'description', 'content_type', 'is_active', 'version']
        }),
        (_('System Information'), {
            'fields': ['created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    inlines = [
        WorkflowStepInline,
        WorkflowConditionContextInline
    ]
    
    def steps_count(self, obj):
        """Count of steps in this workflow."""
        return obj.steps.count()
    steps_count.short_description = _("Steps")
    
    def save_model(self, request, obj, form, change):
        """Set created_by when creating a new workflow."""
        if not change:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    class Media:
        """Admin page custom CSS and JavaScript."""
        if hasattr(settings, 'STATIC_URL'):
            css = {
                'all': (f'{settings.STATIC_URL}workflow/css/admin.css',)
            }
            js = (f'{settings.STATIC_URL}workflow/js/admin.js',)


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowStep model."""
    list_display = [
        'name', 'workflow', 'order', 'is_start', 'is_end',
        'actors_count', 'actions_count', 'transitions_out_count'
    ]
    list_filter = ['workflow', 'is_start', 'is_end']
    search_fields = ['name', 'description', 'workflow__name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (None, {
            'fields': [
                'workflow', 'name', 'description', 'order',
                'is_start', 'is_end', 'auto_proceed'
            ]
        }),
        (_('Parallel Processing Options'), {
            'fields': ['wait_all', 'wait_any'],
            'classes': ['collapse']
        }),
        (_('System Information'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    inlines = [
        WorkflowActorConfigInline,
        WorkflowActionInline,
        WorkflowTransitionInline
    ]
    
    def actors_count(self, obj):
        """Count of actor configurations for this step."""
        return obj.actor_configs.count()
    actors_count.short_description = _("Actors")
    
    def actions_count(self, obj):
        """Count of actions for this step."""
        return obj.actions.count()
    actions_count.short_description = _("Actions")
    
    def transitions_out_count(self, obj):
        """Count of outgoing transitions for this step."""
        return obj.outgoing_transitions.count()
    transitions_out_count.short_description = _("Outgoing Transitions")


@admin.register(WorkflowTransition)
class WorkflowTransitionAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowTransition model."""
    list_display = [
        'name', 'source_step', 'target_step', 
        'has_condition', 'priority', 'created_at'
    ]
    list_filter = ['source_step__workflow', 'priority']
    search_fields = ['name', 'condition_expression', 'source_step__name', 'target_step__name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (None, {
            'fields': [
                'name', 'description', 'source_step', 'target_step',
                'condition_expression', 'priority'
            ]
        }),
        (_('System Information'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def has_condition(self, obj):
        """Whether this transition has a condition expression."""
        return bool(obj.condition_expression)
    has_condition.boolean = True
    has_condition.short_description = _("Has Condition")


@admin.register(WorkflowAction)
class WorkflowActionAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowAction model."""
    list_display = [
        'name', 'workflow_step', 'action_type', 'trigger_point',
        'is_async', 'order', 'is_active', 'created_at'
    ]
    list_filter = ['action_type', 'trigger_point', 'is_async', 'is_active']
    search_fields = ['name', 'description', 'workflow_step__name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (None, {
            'fields': [
                'workflow_step', 'name', 'description', 'action_type',
                'trigger_point', 'is_active'
            ]
        }),
        (_('Configuration'), {
            'fields': ['configuration', 'is_async', 'order']
        }),
        (_('System Information'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(WorkflowActorConfig)
class WorkflowActorConfigAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowActorConfig model."""
    list_display = [
        'workflow_step', 'actor_type', 'user', 'group',
        'role_name', 'has_dynamic_expression'
    ]
    list_filter = ['actor_type', 'workflow_step__workflow']
    search_fields = [
        'workflow_step__name', 'user__username', 
        'group__name', 'role_name', 'dynamic_expression'
    ]
    fields = [
        'workflow_step', 'actor_type', 'user', 'group',
        'role_name', 'dynamic_expression'
    ]
    
    def has_dynamic_expression(self, obj):
        """Whether this actor config has a dynamic expression."""
        return bool(obj.dynamic_expression)
    has_dynamic_expression.boolean = True
    has_dynamic_expression.short_description = _("Dynamic")


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowInstance model."""
    list_display = [
        'id', 'workflow', 'content_type', 'object_link',
        'current_step', 'status', 'current_user', 'created_at'
    ]
    list_filter = ['status', 'workflow', 'content_type', 'created_at']
    search_fields = ['id', 'workflow__name', 'current_step__name']
    readonly_fields = [
        'id', 'workflow', 'content_type', 'object_id', 'object_link',
        'current_step', 'current_user', 'created_by',
        'created_at', 'updated_at', 'data_formatted'
    ]
    fieldsets = [
        (_('Workflow Information'), {
            'fields': [
                'id', 'workflow', 'status', 'current_step',
                'current_user'
            ]
        }),
        (_('Target Object'), {
            'fields': ['content_type', 'object_id', 'object_link']
        }),
        (_('Data'), {
            'fields': ['data_formatted']
        }),
        (_('System Information'), {
            'fields': ['created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def object_link(self, obj):
        """Generate a link to the target object's admin page."""
        if not obj.content_type or not obj.object_id:
            return "-"
            
        try:
            target_obj = obj.content_object
            if not target_obj:
                return "-"
                
            app_label = obj.content_type.app_label
            model_name = obj.content_type.model
            
            url = reverse(
                f'admin:{app_label}_{model_name}_change',
                args=[obj.object_id]
            )
            
            return format_html(
                '<a href="{}">{}</a>',
                url,
                f"{obj.content_type.model} #{obj.object_id}"
            )
        except Exception:
            return f"{obj.content_type.model} #{obj.object_id}"
    object_link.short_description = _("Target Object")
    
    def data_formatted(self, obj):
        """Format the JSON data for display."""
        import json
        from django.utils.safestring import mark_safe
        
        if not obj.data:
            return "-"
            
        try:
            formatted = json.dumps(obj.data, indent=2)
            return mark_safe(f'<pre>{formatted}</pre>')
        except Exception:
            return str(obj.data)
    data_formatted.short_description = _("Data")
    
    def has_add_permission(self, request):
        """Prevent adding workflow instances directly in admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent changing workflow instances directly in admin."""
        return False
    
    class Media:
        """Admin page custom CSS and JavaScript."""
        if hasattr(settings, 'STATIC_URL'):
            css = {
                'all': (f'{settings.STATIC_URL}workflow/css/admin.css',)
            }


@admin.register(WorkflowStepLog)
class WorkflowStepLogAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowStepLog model."""
    list_display = [
        'id', 'workflow_instance_link', 'workflow_step', 
        'action', 'performed_by', 'performed_at', 'has_comment'
    ]
    list_filter = ['action', 'performed_at']
    search_fields = [
        'id', 'workflow_instance__id', 'workflow_step__name',
        'performed_by__username', 'action'
    ]
    readonly_fields = [
        'id', 'workflow_instance', 'workflow_instance_link',
        'workflow_step', 'action', 'performed_by',
        'performed_at', 'data_formatted', 'comment'
    ]
    fieldsets = [
        (_('Log Information'), {
            'fields': [
                'id', 'workflow_instance_link', 'workflow_step',
                'action', 'performed_by', 'performed_at'
            ]
        }),
        (_('Data'), {
            'fields': ['data_formatted', 'comment']
        })
    ]
    
    def workflow_instance_link(self, obj):
        """Generate a link to the workflow instance's admin page."""
        if not obj.workflow_instance:
            return "-"
            
        url = reverse(
            'admin:workflow_workflowinstance_change',
            args=[obj.workflow_instance.pk]
        )
        
        return format_html(
            '<a href="{}">{}</a>',
            url,
            str(obj.workflow_instance.pk)
        )
    workflow_instance_link.short_description = _("Workflow Instance")
    
    def has_comment(self, obj):
        """Whether this log entry has a comment."""
        return bool(obj.comment)
    has_comment.boolean = True
    has_comment.short_description = _("Has Comment")
    
    def data_formatted(self, obj):
        """Format the JSON data for display."""
        import json
        from django.utils.safestring import mark_safe
        
        if not obj.data:
            return "-"
            
        try:
            formatted = json.dumps(obj.data, indent=2)
            return mark_safe(f'<pre>{formatted}</pre>')
        except Exception:
            return str(obj.data)
    data_formatted.short_description = _("Data")
    
    def has_add_permission(self, request):
        """Prevent adding workflow logs directly in admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent changing workflow logs directly in admin."""
        return False


@admin.register(WorkflowConditionContext)
class WorkflowConditionContextAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowConditionContext model."""
    list_display = ['name', 'workflow', 'variable_count', 'created_at']
    list_filter = ['workflow', 'created_at']
    search_fields = ['name', 'description', 'workflow__name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (None, {
            'fields': ['workflow', 'name', 'description', 'variables']
        }),
        (_('System Information'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def variable_count(self, obj):
        """Count of variables in this context."""
        return len(obj.variables) if obj.variables else 0
    variable_count.short_description = _("Variables")
