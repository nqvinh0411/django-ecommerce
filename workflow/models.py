from django.db import models
from django.contrib.auth.models import Group
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
import json


class Workflow(models.Model):
    """
    Defines a workflow template that can be applied to any model instance.
    """
    name = models.CharField(_("Workflow Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        verbose_name=_("Target Model"),
        help_text=_("The model this workflow can be applied to")
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="created_workflows",
        verbose_name=_("Created By")
    )
    version = models.PositiveIntegerField(_("Version"), default=1)
    
    class Meta:
        verbose_name = _("Workflow")
        verbose_name_plural = _("Workflows")
        ordering = ["-updated_at"]
        unique_together = [["name", "version"]]
    
    def __str__(self):
        return f"{self.name} v{self.version}"
    
    def get_start_step(self):
        """Returns the starting step of this workflow."""
        return self.steps.filter(is_start=True).first()
    
    def export_configuration(self):
        """
        Export the workflow configuration as a JSON object for backup/restoration.
        """
        # This would serialize the workflow and all related objects
        # Implementation would include steps, transitions, actions, etc.
        pass


class WorkflowActorConfig(models.Model):
    """
    Configures who can act on a workflow step (users, groups, or roles).
    """
    ACTOR_TYPE_CHOICES = (
        ('user', _('Specific User')),
        ('group', _('User Group')),
        ('role', _('User Role')),
        ('dynamic', _('Dynamic Expression')),
    )
    
    workflow_step = models.ForeignKey(
        'WorkflowStep', 
        on_delete=models.CASCADE,
        related_name="actor_configs",
        verbose_name=_("Workflow Step")
    )
    actor_type = models.CharField(_("Actor Type"), max_length=20, choices=ACTOR_TYPE_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name=_("User")
    )
    group = models.ForeignKey(
        Group, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name=_("Group")
    )
    role_name = models.CharField(_("Role Name"), max_length=100, blank=True)
    dynamic_expression = models.TextField(
        _("Dynamic Expression"), 
        blank=True,
        help_text=_("Python expression to dynamically determine the actor")
    )
    
    class Meta:
        verbose_name = _("Workflow Actor Configuration")
        verbose_name_plural = _("Workflow Actor Configurations")
    
    def __str__(self):
        if self.actor_type == 'user' and self.user:
            return f"User: {self.user.username}"
        elif self.actor_type == 'group' and self.group:
            return f"Group: {self.group.name}"
        elif self.actor_type == 'role':
            return f"Role: {self.role_name}"
        else:
            return f"Dynamic: {self.dynamic_expression[:30]}..."
    
    def can_user_act(self, user, context=None):
        """
        Check if the given user can act on the associated step.
        
        Args:
            user: The Django User instance to check
            context: Optional context dict for dynamic expressions
            
        Returns:
            bool: True if user can act, False otherwise
        """
        if self.actor_type == 'user':
            return self.user == user
        elif self.actor_type == 'group':
            return user.groups.filter(pk=self.group.pk).exists()
        elif self.actor_type == 'role':
            # This would need to be implemented based on your role system
            # Example implementation:
            # return user.roles.filter(name=self.role_name).exists()
            return False
        elif self.actor_type == 'dynamic' and context:
            # Evaluate dynamic expression - should be implemented safely
            # with proper sanitization and execution control
            return False
        return False


class WorkflowStep(models.Model):
    """
    Represents a single step in a workflow process.
    """
    workflow = models.ForeignKey(
        Workflow, 
        on_delete=models.CASCADE,
        related_name="steps",
        verbose_name=_("Workflow")
    )
    name = models.CharField(_("Step Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    order = models.PositiveIntegerField(_("Order"), default=1)
    is_start = models.BooleanField(_("Is Start Step"), default=False)
    is_end = models.BooleanField(_("Is End Step"), default=False)
    wait_all = models.BooleanField(
        _("Wait for All Parallel Steps"), 
        default=False,
        help_text=_("If True, all parallel steps must complete before proceeding")
    )
    wait_any = models.BooleanField(
        _("Wait for Any Parallel Step"), 
        default=False,
        help_text=_("If True, only one parallel step needs to complete before proceeding")
    )
    auto_proceed = models.BooleanField(
        _("Auto Proceed"), 
        default=False,
        help_text=_("If True, step will automatically proceed to next step after actions complete")
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    class Meta:
        verbose_name = _("Workflow Step")
        verbose_name_plural = _("Workflow Steps")
        ordering = ["workflow", "order"]
        unique_together = [["workflow", "order"]]
    
    def __str__(self):
        return f"{self.workflow.name} - {self.name}"
    
    def get_available_transitions(self, instance=None, context=None):
        """
        Get all transitions available from this step that match their conditions.
        
        Args:
            instance: The workflow instance
            context: Additional context for evaluating conditions
            
        Returns:
            QuerySet of valid transitions from this step
        """
        transitions = self.outgoing_transitions.all()
        if instance and context:
            # Filter by conditions - this would need to be implemented
            # based on your condition evaluation logic
            valid_transitions = []
            for transition in transitions:
                if transition.evaluate_condition(instance, context):
                    valid_transitions.append(transition.pk)
            return self.outgoing_transitions.filter(pk__in=valid_transitions)
        return transitions


class WorkflowTransition(models.Model):
    """
    Defines a possible transition between workflow steps with optional conditions.
    """
    name = models.CharField(_("Transition Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    source_step = models.ForeignKey(
        WorkflowStep, 
        on_delete=models.CASCADE,
        related_name="outgoing_transitions",
        verbose_name=_("Source Step")
    )
    target_step = models.ForeignKey(
        WorkflowStep, 
        on_delete=models.CASCADE,
        related_name="incoming_transitions",
        verbose_name=_("Target Step")
    )
    condition_expression = models.TextField(
        _("Condition Expression"),
        blank=True,
        help_text=_("Python-safe expression that must evaluate to True for this transition to be valid")
    )
    priority = models.PositiveIntegerField(
        _("Priority"), 
        default=1,
        help_text=_("When multiple transitions are valid, higher priority transitions are chosen first")
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    class Meta:
        verbose_name = _("Workflow Transition")
        verbose_name_plural = _("Workflow Transitions")
        ordering = ["-priority"]
    
    def __str__(self):
        return f"{self.source_step.name} → {self.target_step.name}"
    
    def evaluate_condition(self, instance, context=None):
        """
        Evaluate the condition expression for this transition.
        
        Args:
            instance: The workflow instance
            context: Additional context dict for condition evaluation
            
        Returns:
            bool: True if condition is met or empty, False otherwise
        """
        if not self.condition_expression:
            return True
            
        try:
            # This is a simplified implementation
            # A real implementation would use a secure evaluation mechanism
            # like a DSL parser or a restricted Python evaluation
            
            # In a real implementation, you'd want to:
            # 1. Prevent dangerous operations (exec, eval, etc.)
            # 2. Limit available functions and modules
            # 3. Set a timeout for evaluation
            # 4. Handle exceptions properly
            
            # Example of restricted evaluation:
            # return safe_eval(self.condition_expression, instance, context)
            return True
        except Exception as e:
            # Log the error
            return False


class WorkflowAction(models.Model):
    """
    Actions that are automatically executed when a step is activated or completed.
    """
    ACTION_TYPE_CHOICES = (
        ('email', _('Send Email')),
        ('api', _('Call API')),
        ('update', _('Update Record')),
        ('function', _('Call Function')),
        ('notification', _('Send Notification')),
    )
    
    TRIGGER_POINT_CHOICES = (
        ('on_enter', _('On Step Enter')),
        ('on_exit', _('On Step Exit')),
        ('on_complete', _('On Step Complete')),
        ('on_reject', _('On Step Reject')),
    )
    
    workflow_step = models.ForeignKey(
        WorkflowStep, 
        on_delete=models.CASCADE,
        related_name="actions",
        verbose_name=_("Workflow Step")
    )
    name = models.CharField(_("Action Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    action_type = models.CharField(_("Action Type"), max_length=20, choices=ACTION_TYPE_CHOICES)
    trigger_point = models.CharField(
        _("Trigger Point"), 
        max_length=20, 
        choices=TRIGGER_POINT_CHOICES
    )
    configuration = models.JSONField(
        _("Configuration"),
        default=dict,
        help_text=_("JSON configuration specific to the action type")
    )
    is_async = models.BooleanField(
        _("Asynchronous"),
        default=False,
        help_text=_("If True, action will be executed asynchronously")
    )
    order = models.PositiveIntegerField(_("Execution Order"), default=1)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    class Meta:
        verbose_name = _("Workflow Action")
        verbose_name_plural = _("Workflow Actions")
        ordering = ["workflow_step", "trigger_point", "order"]
    
    def __str__(self):
        return f"{self.workflow_step.name} - {self.get_trigger_point_display()} - {self.name}"
    
    def execute(self, workflow_instance, context=None):
        """
        Execute this action within the given workflow instance context.
        
        Args:
            workflow_instance: The workflow instance this action is being executed for
            context: Additional context for action execution
            
        Returns:
            dict: Result of the action execution
        """
        # This would delegate to appropriate handler based on action_type
        # Example implementation:
        if self.action_type == 'email':
            return self._execute_email_action(workflow_instance, context)
        elif self.action_type == 'api':
            return self._execute_api_action(workflow_instance, context)
        elif self.action_type == 'update':
            return self._execute_update_action(workflow_instance, context)
        elif self.action_type == 'function':
            return self._execute_function_action(workflow_instance, context)
        elif self.action_type == 'notification':
            return self._execute_notification_action(workflow_instance, context)
        return {"status": "error", "message": "Unknown action type"}
    
    def _execute_email_action(self, workflow_instance, context):
        """Send email based on configuration."""
        # Implementation would use Django's email functionality
        return {"status": "success", "message": "Email sent"}
    
    def _execute_api_action(self, workflow_instance, context):
        """Call external API based on configuration."""
        # Implementation would use requests or similar library
        return {"status": "success", "message": "API called"}
    
    def _execute_update_action(self, workflow_instance, context):
        """Update the target record based on configuration."""
        # Implementation would update model fields
        return {"status": "success", "message": "Record updated"}
    
    def _execute_function_action(self, workflow_instance, context):
        """Call a predefined function based on configuration."""
        # Implementation would call registered functions
        return {"status": "success", "message": "Function called"}
    
    def _execute_notification_action(self, workflow_instance, context):
        """Send a notification based on configuration."""
        # Implementation would use your notification system
        return {"status": "success", "message": "Notification sent"}


class WorkflowConditionContext(models.Model):
    """
    Provides variables and context for evaluating workflow conditions.
    """
    workflow = models.ForeignKey(
        Workflow, 
        on_delete=models.CASCADE,
        related_name="condition_contexts",
        verbose_name=_("Workflow")
    )
    name = models.CharField(_("Context Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    variables = models.JSONField(
        _("Variables"),
        default=dict,
        help_text=_("JSON mapping of variable names to source paths or expressions")
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    class Meta:
        verbose_name = _("Workflow Condition Context")
        verbose_name_plural = _("Workflow Condition Contexts")
    
    def __str__(self):
        return f"{self.workflow.name} - {self.name}"
    
    def build_context(self, workflow_instance):
        """
        Build a context dictionary for condition evaluation.
        
        Args:
            workflow_instance: The workflow instance to build context for
            
        Returns:
            dict: Context dictionary with variables
        """
        context = {
            'instance': workflow_instance,
            'target': workflow_instance.content_object,
            'user': workflow_instance.current_user,
        }
        
        # Add custom variables from configuration
        for var_name, var_config in self.variables.items():
            # Implementation would extract values based on var_config
            # Either from target object attributes, user properties, etc.
            pass
            
        return context


class WorkflowInstance(models.Model):
    """
    Represents an actual running instance of a workflow applied to a specific model instance.
    """
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('terminated', _('Terminated')),
        ('error', _('Error')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        Workflow, 
        on_delete=models.CASCADE,
        related_name="instances",
        verbose_name=_("Workflow")
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    current_step = models.ForeignKey(
        WorkflowStep, 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name="current_instances",
        verbose_name=_("Current Step")
    )
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    current_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name="assigned_workflow_instances",
        verbose_name=_("Current User")
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name="initiated_workflow_instances",
        verbose_name=_("Created By")
    )
    data = models.JSONField(
        _("Instance Data"),
        default=dict,
        help_text=_("Additional data stored during workflow execution")
    )
    
    class Meta:
        verbose_name = _("Workflow Instance")
        verbose_name_plural = _("Workflow Instances")
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name} - {self.content_object}"
    
    def start(self, user=None):
        """
        Start the workflow instance.
        
        Args:
            user: The user initiating the workflow
            
        Returns:
            WorkflowStepLog: The log entry for the started step
        """
        if self.status != 'pending':
            raise ValueError("Workflow instance has already been started")
            
        start_step = self.workflow.get_start_step()
        if not start_step:
            raise ValueError("Workflow has no start step defined")
            
        self.current_step = start_step
        self.status = 'active'
        self.current_user = user
        self.save()
        
        # Create a log entry for starting the workflow
        log = WorkflowStepLog.objects.create(
            workflow_instance=self,
            workflow_step=start_step,
            action='start',
            performed_by=user,
            data={'initial_start': True}
        )
        
        # Execute any "on_enter" actions for the start step
        self._execute_step_actions('on_enter')
        
        return log
    
    def process_step(self, action, user, comment=None, data=None):
        """
        Process the current step with the given action.
        
        Args:
            action: The action to take ('approve', 'reject', etc.)
            user: The user performing the action
            comment: Optional comment for the action
            data: Optional data for the action
            
        Returns:
            WorkflowStepLog: The log entry for the processed step
        """
        if not self.current_step:
            raise ValueError("No current step to process")
            
        if self.status != 'active':
            raise ValueError(f"Cannot process step when workflow is in {self.status} status")
            
        # Create the step log
        log_data = data or {}
        if comment:
            log_data['comment'] = comment
            
        log = WorkflowStepLog.objects.create(
            workflow_instance=self,
            workflow_step=self.current_step,
            action=action,
            performed_by=user,
            data=log_data
        )
        
        # Execute appropriate actions based on the action
        if action == 'approve':
            self._execute_step_actions('on_exit')
            self._execute_step_actions('on_complete')
            self._proceed_to_next_step(user)
        elif action == 'reject':
            self._execute_step_actions('on_reject')
            # Implement rejection logic - might go to previous step or terminate
            
        return log
    
    def _execute_step_actions(self, trigger_point):
        """
        Execute all actions for the current step with the given trigger point.
        
        Args:
            trigger_point: The action trigger point ('on_enter', 'on_exit', etc.)
        """
        if not self.current_step:
            return
            
        actions = self.current_step.actions.filter(
            trigger_point=trigger_point,
            is_active=True
        ).order_by('order')
        
        for action in actions:
            try:
                # Build context for action execution
                context = self._build_action_context()
                
                if action.is_async:
                    # In a real implementation, this would use Celery or similar
                    # Example: execute_action_async.delay(action.id, self.id, context)
                    pass
                else:
                    action.execute(self, context)
            except Exception as e:
                # Log the error
                pass
    
    def _build_action_context(self):
        """
        Build context for action execution.
        
        Returns:
            dict: Context dictionary for action execution
        """
        context = {
            'instance': self,
            'target': self.content_object,
            'current_user': self.current_user,
            'workflow': self.workflow,
            'current_step': self.current_step,
            'data': self.data,
        }
        
        # Add any condition contexts if available
        for ctx in self.workflow.condition_contexts.all():
            additional_context = ctx.build_context(self)
            context.update(additional_context)
            
        return context
    
    def _proceed_to_next_step(self, user):
        """
        Determine and move to the next step based on transitions and conditions.
        
        Args:
            user: The user triggering the transition
        """
        if not self.current_step:
            return
            
        # Get valid transitions
        context = self._build_action_context()
        valid_transitions = self.current_step.get_available_transitions(self, context)
        
        if not valid_transitions.exists():
            if self.current_step.is_end:
                self.status = 'completed'
                self.save()
                return
            else:
                # No valid transitions but not an end step
                # This might be an error state or just waiting for conditions to change
                return
                
        # Get the highest priority valid transition
        next_transition = valid_transitions.first()  # Ordered by -priority
        
        # Update current step
        self.current_step = next_transition.target_step
        self.save()
        
        # Create a log entry for the transition
        WorkflowStepLog.objects.create(
            workflow_instance=self,
            workflow_step=self.current_step,
            action='transition',
            performed_by=user,
            data={
                'from_step': next_transition.source_step.name,
                'to_step': next_transition.target_step.name,
                'transition': next_transition.name
            }
        )
        
        # Execute on_enter actions for the new step
        self._execute_step_actions('on_enter')
        
        # If this is an end step, mark the workflow as completed
        if self.current_step.is_end:
            self.status = 'completed'
            self.save()
        
        # If auto_proceed is enabled, automatically process this step
        if self.current_step.auto_proceed:
            self.process_step('approve', user, "Auto-approved", {})


class WorkflowStepLog(models.Model):
    """
    Records the history of each step in a workflow instance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_instance = models.ForeignKey(
        WorkflowInstance, 
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name=_("Workflow Instance")
    )
    workflow_step = models.ForeignKey(
        WorkflowStep, 
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name=_("Workflow Step")
    )
    action = models.CharField(_("Action"), max_length=50)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name="workflow_actions",
        verbose_name=_("Performed By")
    )
    performed_at = models.DateTimeField(_("Performed At"), default=timezone.now)
    data = models.JSONField(_("Action Data"), default=dict)
    
    class Meta:
        verbose_name = _("Workflow Step Log")
        verbose_name_plural = _("Workflow Step Logs")
        ordering = ["-performed_at"]
        indexes = [
            models.Index(fields=['workflow_instance', 'performed_at']),
            models.Index(fields=['performed_by']),
        ]
    
    def __str__(self):
        return f"{self.workflow_step.name} - {self.action} - {self.performed_at}"
    
    @property
    def comment(self):
        """Extract comment from data if present."""
        return self.data.get('comment', '')
