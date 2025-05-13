from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from .models import (
    Workflow, WorkflowStep, WorkflowTransition, WorkflowAction,
    WorkflowInstance, WorkflowStepLog, WorkflowActorConfig,
    WorkflowConditionContext
)


class ContentTypeSerializer(serializers.ModelSerializer):
    """Serializer for ContentType model to use in Workflow configuration."""
    app_label = serializers.CharField(read_only=True)
    model = serializers.CharField(read_only=True)
    name = serializers.CharField(source='model_class.__name__', read_only=True)
    
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model', 'name']


class UserSerializer(serializers.ModelSerializer):
    """Minimal User serializer for workflow assignments."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class GroupSerializer(serializers.ModelSerializer):
    """Minimal Group serializer for workflow assignments."""
    class Meta:
        model = Group
        fields = ['id', 'name']


class WorkflowActorConfigSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowActorConfig model."""
    user_details = UserSerializer(source='user', read_only=True)
    group_details = GroupSerializer(source='group', read_only=True)
    
    class Meta:
        model = WorkflowActorConfig
        fields = [
            'id', 'actor_type', 'user', 'user_details', 'group', 'group_details',
            'role_name', 'dynamic_expression'
        ]


class WorkflowActionSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowAction model."""
    class Meta:
        model = WorkflowAction
        fields = [
            'id', 'workflow_step', 'name', 'description', 'action_type',
            'trigger_point', 'configuration', 'is_async', 'order', 'is_active'
        ]


class WorkflowTransitionSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowTransition model."""
    source_step_name = serializers.CharField(source='source_step.name', read_only=True)
    target_step_name = serializers.CharField(source='target_step.name', read_only=True)
    
    class Meta:
        model = WorkflowTransition
        fields = [
            'id', 'name', 'description', 'source_step', 'source_step_name',
            'target_step', 'target_step_name', 'condition_expression', 'priority'
        ]


class WorkflowStepSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowStep model."""
    actions = WorkflowActionSerializer(many=True, read_only=True)
    actor_configs = WorkflowActorConfigSerializer(many=True, read_only=True)
    outgoing_transitions = WorkflowTransitionSerializer(many=True, read_only=True)
    incoming_transitions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = WorkflowStep
        fields = [
            'id', 'workflow', 'name', 'description', 'order', 'is_start', 'is_end',
            'wait_all', 'wait_any', 'auto_proceed', 'actions', 'actor_configs',
            'outgoing_transitions', 'incoming_transitions', 'created_at', 'updated_at'
        ]


class WorkflowConditionContextSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowConditionContext model."""
    class Meta:
        model = WorkflowConditionContext
        fields = ['id', 'workflow', 'name', 'description', 'variables']


class WorkflowSerializer(serializers.ModelSerializer):
    """Serializer for Workflow model with nested data."""
    content_type_details = ContentTypeSerializer(source='content_type', read_only=True)
    steps = WorkflowStepSerializer(many=True, read_only=True)
    condition_contexts = WorkflowConditionContextSerializer(many=True, read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'description', 'is_active', 'content_type', 'content_type_details',
            'created_at', 'updated_at', 'created_by', 'created_by_details', 'version',
            'steps', 'condition_contexts'
        ]


class WorkflowStepLogSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowStepLog model."""
    workflow_step_name = serializers.CharField(source='workflow_step.name', read_only=True)
    performed_by_details = UserSerializer(source='performed_by', read_only=True)
    
    class Meta:
        model = WorkflowStepLog
        fields = [
            'id', 'workflow_instance', 'workflow_step', 'workflow_step_name',
            'action', 'performed_by', 'performed_by_details', 
            'performed_at', 'data', 'comment'
        ]


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowInstance model."""
    workflow_details = WorkflowSerializer(source='workflow', read_only=True)
    current_step_details = WorkflowStepSerializer(source='current_step', read_only=True)
    current_user_details = UserSerializer(source='current_user', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    content_type_details = ContentTypeSerializer(source='content_type', read_only=True)
    logs = WorkflowStepLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'workflow', 'workflow_details', 'content_type', 'content_type_details',
            'object_id', 'current_step', 'current_step_details', 'status',
            'current_user', 'current_user_details', 'created_at', 'updated_at',
            'created_by', 'created_by_details', 'data', 'logs'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Specialized serializers for API operations

class WorkflowImportExportSerializer(serializers.Serializer):
    """Serializer for importing/exporting workflow configurations."""
    workflow_json = serializers.JSONField()


class WorkflowStartSerializer(serializers.Serializer):
    """Serializer for starting a workflow instance."""
    content_type_id = serializers.IntegerField()
    object_id = serializers.IntegerField()
    workflow_id = serializers.IntegerField()
    initial_data = serializers.JSONField(required=False)


class WorkflowProcessStepSerializer(serializers.Serializer):
    """Serializer for processing a workflow step."""
    action = serializers.CharField()
    comment = serializers.CharField(required=False, allow_blank=True)
    data = serializers.JSONField(required=False)


class WorkflowSimulateSerializer(serializers.Serializer):
    """Serializer for simulating a workflow execution."""
    workflow_id = serializers.IntegerField()
    test_data = serializers.JSONField()
    simulation_steps = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class WorkflowStepPositionSerializer(serializers.Serializer):
    """Serializer for updating workflow step positions in the UI."""
    step_id = serializers.IntegerField()
    x_position = serializers.FloatField()
    y_position = serializers.FloatField()
