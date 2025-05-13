"""
Workflow Permissions Service

This module contains functions for checking permissions related to workflow execution,
including who can process workflow steps based on actor configurations.
"""
import logging
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def can_user_process_step(user, workflow_step, workflow_instance):
    """
    Check if a user has permission to process a workflow step.
    
    Args:
        user: The Django User instance to check
        workflow_step: The WorkflowStep to check permission for
        workflow_instance: The WorkflowInstance being processed
        
    Returns:
        bool: True if user can process the step, False otherwise
    """
    if not user or not workflow_step:
        return False
        
    # Admin users can process any step
    if user.is_superuser:
        return True
        
    # Check all actor configurations for this step
    actor_configs = workflow_step.actor_configs.all()
    
    # If no configurations exist, no one can process except admins
    if not actor_configs.exists():
        return False
        
    # Build context for dynamic expressions
    context = _build_permission_context(user, workflow_step, workflow_instance)
    
    # Check each configuration
    for config in actor_configs:
        if config.can_user_act(user, context):
            return True
            
    return False


def get_eligible_users_for_step(workflow_step, workflow_instance):
    """
    Get all users who are eligible to process a workflow step.
    
    Args:
        workflow_step: The WorkflowStep to get eligible users for
        workflow_instance: The WorkflowInstance being processed
        
    Returns:
        QuerySet: Django User queryset of eligible users
    """
    # Start with empty queryset
    eligible_users = User.objects.none()
    
    # Get all actor configurations for this step
    actor_configs = workflow_step.actor_configs.all()
    
    # Process each configuration
    for config in actor_configs:
        if config.actor_type == 'user' and config.user:
            # Add specific user
            eligible_users = eligible_users.union(
                User.objects.filter(pk=config.user.pk)
            )
        elif config.actor_type == 'group' and config.group:
            # Add all users in the group
            group_users = User.objects.filter(groups__pk=config.group.pk)
            eligible_users = eligible_users.union(group_users)
        elif config.actor_type == 'role' and config.role_name:
            # This would need to be implemented based on your role system
            # For example, if you have a UserProfile model with roles:
            # role_users = User.objects.filter(profile__roles__name=config.role_name)
            # eligible_users = eligible_users.union(role_users)
            pass
        elif config.actor_type == 'dynamic' and config.dynamic_expression:
            # Dynamic expressions would need a more complex implementation
            # based on your evaluation system
            pass
            
    # Add superusers
    eligible_users = eligible_users.union(User.objects.filter(is_superuser=True))
    
    return eligible_users.distinct()


def can_user_start_workflow(user, workflow, target_object):
    """
    Check if a user has permission to start a workflow on a target object.
    
    Args:
        user: The Django User instance to check
        workflow: The Workflow to start
        target_object: The object to attach the workflow to
        
    Returns:
        bool: True if user can start the workflow, False otherwise
    """
    # Admin users can start any workflow
    if user.is_superuser:
        return True
        
    # Example permission checks based on object type
    # This would need to be customized based on your specific requirements
    
    # Check if user has permission to modify the target object
    # Example: for a Django model object with a user field
    if hasattr(target_object, 'user') and target_object.user == user:
        return True
        
    # Example: for objects that might have an owner or created_by field
    if hasattr(target_object, 'owner') and target_object.owner == user:
        return True
    if hasattr(target_object, 'created_by') and target_object.created_by == user:
        return True
        
    # Example: check model-specific permissions like 'can_start_workflow'
    if user.has_perm(f'{target_object._meta.app_label}.can_start_workflow'):
        return True
        
    return False


def can_user_terminate_workflow(user, workflow_instance):
    """
    Check if a user has permission to terminate a workflow instance.
    
    Args:
        user: The Django User instance to check
        workflow_instance: The WorkflowInstance to terminate
        
    Returns:
        bool: True if user can terminate the workflow, False otherwise
    """
    # Admin users can terminate any workflow
    if user.is_superuser:
        return True
        
    # Workflow creator can terminate their own workflows
    if workflow_instance.created_by == user:
        return True
        
    # Check if user has workflow termination permission
    if user.has_perm('workflow.can_terminate_workflow'):
        return True
        
    return False


def _build_permission_context(user, workflow_step, workflow_instance):
    """
    Build context for evaluating permission expressions.
    
    Args:
        user: The user to build context for
        workflow_step: The workflow step
        workflow_instance: The workflow instance
        
    Returns:
        dict: Context dictionary for permission evaluation
    """
    context = {
        'user': user,
        'workflow_step': workflow_step,
        'workflow_instance': workflow_instance,
        'target': workflow_instance.content_object if workflow_instance else None,
    }
    
    # Add user profile attributes if available
    if hasattr(user, 'profile'):
        context['profile'] = user.profile
        
        # Example: Add roles if they exist
        if hasattr(user.profile, 'roles'):
            context['roles'] = user.profile.roles.all()
            
    # Add target object attributes
    if workflow_instance and workflow_instance.content_object:
        target = workflow_instance.content_object
        context['target_attributes'] = {}
        
        # Add all fields from the target
        for field in target._meta.fields:
            context['target_attributes'][field.name] = getattr(target, field.name)
            
    return context
