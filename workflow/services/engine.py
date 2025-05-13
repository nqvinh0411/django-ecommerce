"""
Workflow Engine Service

This module contains the core engine for executing workflow transitions, 
evaluating conditions, and handling workflow state management.
"""
import logging
from django.db import transaction
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from ..models import (
    Workflow, WorkflowStep, WorkflowTransition, WorkflowAction,
    WorkflowInstance, WorkflowStepLog, WorkflowActorConfig
)

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Core engine for workflow execution, providing methods to:
    - Start workflow instances
    - Process workflow steps
    - Evaluate transition conditions
    - Execute workflow actions
    - Handle branching and parallel execution
    """
    
    def start_workflow(self, target_object, workflow_id, user=None, initial_data=None):
        """
        Start a new workflow instance for a target object.
        
        Args:
            target_object: The object to attach the workflow to
            workflow_id: The ID of the workflow to start
            user: The user starting the workflow
            initial_data: Optional initial data for the workflow instance
            
        Returns:
            WorkflowInstance: The created workflow instance
        """
        try:
            workflow = Workflow.objects.get(pk=workflow_id, is_active=True)
        except Workflow.DoesNotExist:
            raise ValueError(f"Active workflow with ID {workflow_id} not found")
            
        # Verify the target object type matches the workflow's expected type
        content_type = ContentType.objects.get_for_model(target_object)
        if content_type.id != workflow.content_type.id:
            raise ValueError(
                f"Workflow {workflow.name} cannot be applied to {content_type.model} objects"
            )
            
        # Check if there's already an active workflow of this type for this object
        existing_active = WorkflowInstance.objects.filter(
            workflow=workflow,
            content_type=content_type,
            object_id=target_object.pk,
            status__in=['pending', 'active']
        ).first()
        
        if existing_active:
            raise ValueError(
                f"There is already an active {workflow.name} workflow for this {content_type.model}"
            )
            
        with transaction.atomic():
            # Create the workflow instance
            instance = WorkflowInstance.objects.create(
                workflow=workflow,
                content_type=content_type,
                object_id=target_object.pk,
                status='pending',
                created_by=user,
                data=initial_data or {}
            )
            
            # Start the workflow
            instance.start(user)
            
            logger.info(
                f"Started workflow {workflow.name} for {content_type.model} #{target_object.pk}"
            )
            
            return instance
    
    def process_step(self, instance_id, action, user, comment=None, data=None):
        """
        Process a step in a workflow instance.
        
        Args:
            instance_id: The ID of the workflow instance
            action: The action to perform (e.g., 'approve', 'reject')
            user: The user performing the action
            comment: Optional comment for the action
            data: Optional data for the action
            
        Returns:
            WorkflowInstance: The updated workflow instance
        """
        try:
            instance = WorkflowInstance.objects.get(pk=instance_id)
        except WorkflowInstance.DoesNotExist:
            raise ValueError(f"Workflow instance with ID {instance_id} not found")
            
        if instance.status != 'active':
            raise ValueError(
                f"Cannot process step when workflow is in {instance.status} status"
            )
            
        if not instance.current_step:
            raise ValueError("No current step to process")
            
        # Process the step
        log = instance.process_step(action, user, comment, data)
        
        logger.info(
            f"Processed step {instance.current_step.name} with action {action} "
            f"by user {user.username if user else 'System'}"
        )
        
        return instance
    
    def evaluate_condition(self, condition_expression, context):
        """
        Safely evaluate a condition expression.
        
        Args:
            condition_expression: The expression to evaluate
            context: The context data for evaluation
            
        Returns:
            bool: The result of the evaluation
        """
        if not condition_expression:
            return True
            
        try:
            # This is a simplified implementation
            # A real implementation would use a secure evaluation mechanism
            # Either a custom DSL parser or a restricted Python evaluation
            
            # For demonstration, we'll just evaluate some simple expressions
            # In a real implementation, you'd want to use a secure evaluation library
            
            # Example implementation for simple expressions:
            expression = condition_expression.lower()
            
            # Handle some common condition types
            if "==" in expression:
                left, right = expression.split("==", 1)
                left = left.strip()
                right = right.strip()
                
                # Remove quotes if present
                if right.startswith('"') and right.endswith('"'):
                    right = right[1:-1]
                if right.startswith("'") and right.endswith("'"):
                    right = right[1:-1]
                    
                # Get the value from context
                if '.' in left:
                    obj_name, attr = left.split('.', 1)
                    if obj_name in context and hasattr(context[obj_name], attr):
                        left_value = getattr(context[obj_name], attr)
                    else:
                        return False
                else:
                    if left in context:
                        left_value = context[left]
                    else:
                        return False
                        
                return left_value == right
                
            elif ">" in expression:
                left, right = expression.split(">", 1)
                left = left.strip()
                right = right.strip()
                
                # Try to convert right to number
                try:
                    right = float(right)
                except ValueError:
                    return False
                    
                # Get the value from context
                if '.' in left:
                    obj_name, attr = left.split('.', 1)
                    if obj_name in context and hasattr(context[obj_name], attr):
                        left_value = getattr(context[obj_name], attr)
                    else:
                        return False
                else:
                    if left in context:
                        left_value = context[left]
                    else:
                        return False
                        
                try:
                    left_value = float(left_value)
                    return left_value > right
                except (ValueError, TypeError):
                    return False
                    
            elif "<" in expression:
                # Similar implementation for < operator
                pass
                
            # Add more operators as needed
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition_expression}': {e}")
            return False
    
    def execute_action(self, action_id, instance_id, context=None):
        """
        Execute a workflow action.
        
        Args:
            action_id: The ID of the action to execute
            instance_id: The ID of the workflow instance
            context: Additional context for action execution
            
        Returns:
            dict: The result of the action execution
        """
        try:
            action = WorkflowAction.objects.get(pk=action_id, is_active=True)
        except WorkflowAction.DoesNotExist:
            raise ValueError(f"Active action with ID {action_id} not found")
            
        try:
            instance = WorkflowInstance.objects.get(pk=instance_id)
        except WorkflowInstance.DoesNotExist:
            raise ValueError(f"Workflow instance with ID {instance_id} not found")
            
        # Execute the action
        result = action.execute(instance, context)
        
        logger.info(
            f"Executed action {action.name} for workflow instance {instance_id}"
        )
        
        return result
    
    def get_next_steps(self, instance_id):
        """
        Get the possible next steps for a workflow instance.
        
        Args:
            instance_id: The ID of the workflow instance
            
        Returns:
            list: List of possible next steps with their transitions
        """
        try:
            instance = WorkflowInstance.objects.get(pk=instance_id)
        except WorkflowInstance.DoesNotExist:
            raise ValueError(f"Workflow instance with ID {instance_id} not found")
            
        if not instance.current_step:
            return []
            
        # Build context for condition evaluation
        context = self._build_condition_context(instance)
        
        # Get available transitions
        transitions = instance.current_step.get_available_transitions(instance, context)
        
        # Prepare result
        next_steps = []
        for transition in transitions:
            next_steps.append({
                'transition_id': transition.id,
                'transition_name': transition.name,
                'target_step_id': transition.target_step.id,
                'target_step_name': transition.target_step.name,
                'condition': transition.condition_expression,
                'condition_valid': self.evaluate_condition(
                    transition.condition_expression, context
                )
            })
            
        return next_steps
    
    def _build_condition_context(self, instance):
        """
        Build a context dictionary for condition evaluation.
        
        Args:
            instance: The workflow instance
            
        Returns:
            dict: Context dictionary for condition evaluation
        """
        # Basic context
        context = {
            'instance': instance,
            'target': instance.content_object,
            'user': instance.current_user,
            'data': instance.data,
        }
        
        # Add attributes from the target object
        target = instance.content_object
        if target:
            context['target_attributes'] = {}
            for field in target._meta.fields:
                context['target_attributes'][field.name] = getattr(target, field.name)
                
        # Add condition contexts if available
        for ctx in instance.workflow.condition_contexts.all():
            additional_context = ctx.build_context(instance)
            context.update(additional_context)
            
        return context
    
    def simulate_workflow(self, workflow, test_data, simulation_steps=None):
        """
        Simulate a workflow execution with test data.
        
        Args:
            workflow: The workflow to simulate
            test_data: Test data for the simulation
            simulation_steps: Optional list of step actions to perform
            
        Returns:
            dict: Simulation results
        """
        # Create a mock instance for simulation
        mock_instance = {
            'id': 'simulation',
            'workflow': workflow,
            'status': 'active',
            'data': test_data,
            'current_step': workflow.get_start_step(),
            'logs': []
        }
        
        result = {
            'workflow': workflow.name,
            'start_step': workflow.get_start_step().name if workflow.get_start_step() else None,
            'simulation_paths': []
        }
        
        # If specific simulation steps are provided, follow that path
        if simulation_steps:
            path = self._simulate_specific_path(mock_instance, simulation_steps)
            result['simulation_paths'].append(path)
        else:
            # Otherwise, explore all possible paths (up to a reasonable depth)
            paths = self._simulate_all_paths(mock_instance, max_depth=10)
            result['simulation_paths'] = paths
            
        return result
    
    def _simulate_specific_path(self, mock_instance, simulation_steps):
        """Simulate a specific path in the workflow."""
        path = {
            'steps': [],
            'success': True,
            'end_step': None
        }
        
        current_step = mock_instance['current_step']
        
        for step_action in simulation_steps:
            path['steps'].append({
                'step': current_step.name,
                'action': step_action
            })
            
            # Get available transitions
            context = self._build_condition_context(mock_instance)
            transitions = current_step.get_available_transitions(mock_instance, context)
            
            # Find a valid transition based on the action
            valid_transition = None
            for transition in transitions:
                # In a real implementation, you'd have a mapping from actions to transitions
                # or a way to determine which transition matches an action
                if self.evaluate_condition(transition.condition_expression, context):
                    valid_transition = transition
                    break
                    
            if not valid_transition:
                path['success'] = False
                path['error'] = f"No valid transition found for step {current_step.name} with action {step_action}"
                break
                
            # Move to next step
            current_step = valid_transition.target_step
            mock_instance['current_step'] = current_step
            
            # Check if we've reached an end step
            if current_step.is_end:
                path['end_step'] = current_step.name
                break
                
        if path['success'] and not path['end_step']:
            path['end_step'] = current_step.name
            
        return path
    
    def _simulate_all_paths(self, mock_instance, max_depth=10, current_depth=0, path=None):
        """Recursively explore all possible paths in the workflow."""
        if path is None:
            path = []
            
        if current_depth >= max_depth:
            return [{
                'steps': path.copy(),
                'truncated': True,
                'end_step': mock_instance['current_step'].name
            }]
            
        current_step = mock_instance['current_step']
        
        # Check if we've reached an end step
        if current_step.is_end:
            return [{
                'steps': path.copy(),
                'success': True,
                'end_step': current_step.name
            }]
            
        # Get available transitions
        context = self._build_condition_context(mock_instance)
        transitions = current_step.get_available_transitions(mock_instance, context)
        
        # Filter to valid transitions
        valid_transitions = []
        for transition in transitions:
            if self.evaluate_condition(transition.condition_expression, context):
                valid_transitions.append(transition)
                
        if not valid_transitions:
            return [{
                'steps': path.copy(),
                'success': False,
                'error': f"No valid transitions from step {current_step.name}",
                'end_step': current_step.name
            }]
            
        # Explore each possible transition
        all_paths = []
        for transition in valid_transitions:
            next_step = transition.target_step
            
            # Update path
            path.append({
                'step': current_step.name,
                'transition': transition.name,
                'next_step': next_step.name
            })
            
            # Create a copy of the instance for this branch
            branch_instance = mock_instance.copy()
            branch_instance['current_step'] = next_step
            
            # Recursively explore this branch
            branch_paths = self._simulate_all_paths(
                branch_instance, max_depth, current_depth + 1, path.copy()
            )
            
            all_paths.extend(branch_paths)
            
            # Remove the current step from the path for the next iteration
            path.pop()
            
        return all_paths


def start_workflow(instance, workflow_id, user=None, initial_data=None):
    """
    Convenience function to start a workflow for a model instance.
    
    Args:
        instance: The model instance to attach the workflow to
        workflow_id: The ID of the workflow to start
        user: The user starting the workflow
        initial_data: Optional initial data for the workflow instance
        
    Returns:
        WorkflowInstance: The created workflow instance
    """
    engine = WorkflowEngine()
    return engine.start_workflow(instance, workflow_id, user, initial_data)
