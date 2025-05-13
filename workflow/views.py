from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import (
    Workflow, WorkflowStep, WorkflowTransition, WorkflowAction,
    WorkflowInstance, WorkflowStepLog, WorkflowActorConfig,
    WorkflowConditionContext
)
from .serializers import (
    WorkflowSerializer, WorkflowStepSerializer, WorkflowTransitionSerializer,
    WorkflowActionSerializer, WorkflowInstanceSerializer, WorkflowStepLogSerializer,
    WorkflowActorConfigSerializer, WorkflowConditionContextSerializer,
    ContentTypeSerializer, WorkflowImportExportSerializer,
    WorkflowStartSerializer, WorkflowProcessStepSerializer,
    WorkflowSimulateSerializer, WorkflowStepPositionSerializer
)
from .services.engine import WorkflowEngine
from .services.permissions import can_user_process_step


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    Others can only read.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff


class ContentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ContentType model to list available models for workflow targets.
    """
    queryset = ContentType.objects.all().order_by('app_label', 'model')
    serializer_class = ContentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class WorkflowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Workflow configurations.
    """
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Export workflow configuration as JSON."""
        workflow = self.get_object()
        
        # This would call a service method to export the workflow
        # Example: export_data = workflow_export_service.export_workflow(workflow)
        export_data = {"workflow": workflow.name, "steps": []}  # Placeholder
        
        serializer = WorkflowImportExportSerializer(data={"workflow_json": export_data})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def import_workflow(self, request):
        """Import workflow configuration from JSON."""
        serializer = WorkflowImportExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # This would call a service method to import the workflow
        # Example: workflow = workflow_import_service.import_workflow(
        #    serializer.validated_data['workflow_json'], request.user)
        
        # Placeholder response
        return Response(
            {"status": "success", "message": "Workflow imported successfully"},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a new workflow instance for a specific object."""
        workflow = self.get_object()
        
        serializer = WorkflowStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            content_type = ContentType.objects.get(
                pk=serializer.validated_data['content_type_id']
            )
            target_object = content_type.get_object_for_this_type(
                pk=serializer.validated_data['object_id']
            )
            
            with transaction.atomic():
                # Create workflow instance
                instance = WorkflowInstance.objects.create(
                    workflow=workflow,
                    content_type=content_type,
                    object_id=serializer.validated_data['object_id'],
                    created_by=request.user,
                    data=serializer.validated_data.get('initial_data', {})
                )
                
                # Start the workflow
                instance.start(request.user)
                
                # Return the created instance
                return Response(
                    WorkflowInstanceSerializer(instance).data,
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def simulate(self, request, pk=None):
        """Simulate a workflow execution with test data."""
        workflow = self.get_object()
        
        serializer = WorkflowSimulateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Instantiate the workflow engine
        engine = WorkflowEngine()
        
        # Run simulation
        simulation_result = engine.simulate_workflow(
            workflow,
            serializer.validated_data['test_data'],
            serializer.validated_data.get('simulation_steps', [])
        )
        
        return Response(simulation_result)


class WorkflowStepViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing WorkflowStep configurations.
    """
    queryset = WorkflowStep.objects.all()
    serializer_class = WorkflowStepSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_queryset(self):
        queryset = WorkflowStep.objects.all()
        workflow_id = self.request.query_params.get('workflow', None)
        if workflow_id:
            queryset = queryset.filter(workflow_id=workflow_id)
        return queryset
    
    @action(detail=False, methods=['post'])
    def update_positions(self, request):
        """Update positions of multiple steps (for drag-and-drop UI)."""
        serializer = WorkflowStepPositionSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            for item in serializer.validated_data:
                step = get_object_or_404(WorkflowStep, pk=item['step_id'])
                
                # In a real implementation, you would have x_position and y_position fields
                # For now, we just update the step's data field
                if not hasattr(step, 'data'):
                    step.data = {}
                    
                step.data.update({
                    'x_position': item['x_position'],
                    'y_position': item['y_position']
                })
                step.save()
                
        return Response({"status": "success"})


class WorkflowTransitionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing WorkflowTransition configurations.
    """
    queryset = WorkflowTransition.objects.all()
    serializer_class = WorkflowTransitionSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_queryset(self):
        queryset = WorkflowTransition.objects.all()
        source_step = self.request.query_params.get('source_step', None)
        target_step = self.request.query_params.get('target_step', None)
        
        if source_step:
            queryset = queryset.filter(source_step_id=source_step)
        if target_step:
            queryset = queryset.filter(target_step_id=target_step)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def test_condition(self, request, pk=None):
        """Test a transition condition with sample data."""
        transition = self.get_object()
        test_data = request.data.get('test_data', {})
        
        # This would use a service to safely evaluate the condition
        # Example: result = condition_evaluator.evaluate(
        #     transition.condition_expression, test_data)
        
        # Placeholder implementation
        result = True
        explanation = "Condition would evaluate based on the provided test data"
        
        return Response({
            "result": result,
            "explanation": explanation
        })


class WorkflowActionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing WorkflowAction configurations.
    """
    queryset = WorkflowAction.objects.all()
    serializer_class = WorkflowActionSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_queryset(self):
        queryset = WorkflowAction.objects.all()
        workflow_step = self.request.query_params.get('workflow_step', None)
        if workflow_step:
            queryset = queryset.filter(workflow_step_id=workflow_step)
        return queryset
    
    @action(detail=True, methods=['post'])
    def test_action(self, request, pk=None):
        """Test an action with sample data without actually executing it."""
        action = self.get_object()
        test_data = request.data.get('test_data', {})
        
        # This would call a service to simulate the action
        # Example: result = action_simulator.simulate(action, test_data)
        
        # Placeholder implementation
        action_type = action.action_type
        configuration = action.configuration
        
        result = {
            "action_type": action_type,
            "configuration": configuration,
            "simulation_result": f"Would execute {action_type} action with provided test data"
        }
        
        return Response(result)


class WorkflowActorConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing WorkflowActorConfig configurations.
    """
    queryset = WorkflowActorConfig.objects.all()
    serializer_class = WorkflowActorConfigSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_queryset(self):
        queryset = WorkflowActorConfig.objects.all()
        workflow_step = self.request.query_params.get('workflow_step', None)
        if workflow_step:
            queryset = queryset.filter(workflow_step_id=workflow_step)
        return queryset


class WorkflowConditionContextViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing WorkflowConditionContext configurations.
    """
    queryset = WorkflowConditionContext.objects.all()
    serializer_class = WorkflowConditionContextSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_queryset(self):
        queryset = WorkflowConditionContext.objects.all()
        workflow = self.request.query_params.get('workflow', None)
        if workflow:
            queryset = queryset.filter(workflow_id=workflow)
        return queryset


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing WorkflowInstance runtime instances.
    """
    queryset = WorkflowInstance.objects.all()
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = WorkflowInstance.objects.all()
        
        # Filter by content type and object id
        content_type_id = self.request.query_params.get('content_type_id', None)
        object_id = self.request.query_params.get('object_id', None)
        if content_type_id and object_id:
            queryset = queryset.filter(
                content_type_id=content_type_id,
                object_id=object_id
            )
            
        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # Filter by workflow
        workflow_id = self.request.query_params.get('workflow_id', None)
        if workflow_id:
            queryset = queryset.filter(workflow_id=workflow_id)
            
        # Filter by current step
        current_step_id = self.request.query_params.get('current_step_id', None)
        if current_step_id:
            queryset = queryset.filter(current_step_id=current_step_id)
            
        # Filter by current user
        current_user_id = self.request.query_params.get('current_user_id', None)
        if current_user_id:
            queryset = queryset.filter(current_user_id=current_user_id)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a workflow instance step."""
        instance = self.get_object()
        
        serializer = WorkflowProcessStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if user has permission to process this step
        if not can_user_process_step(request.user, instance.current_step, instance):
            return Response(
                {"error": "You don't have permission to process this step"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            with transaction.atomic():
                # Process the step
                log = instance.process_step(
                    serializer.validated_data['action'],
                    request.user,
                    serializer.validated_data.get('comment', ''),
                    serializer.validated_data.get('data', {})
                )
                
                # Return the updated instance
                return Response(
                    WorkflowInstanceSerializer(instance).data
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate a workflow instance."""
        instance = self.get_object()
        
        # Check if user has permission (only admins or the creator)
        if not (request.user.is_staff or request.user == instance.created_by):
            return Response(
                {"error": "You don't have permission to terminate this workflow"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            with transaction.atomic():
                # Update status
                instance.status = 'terminated'
                instance.save()
                
                # Create log entry
                WorkflowStepLog.objects.create(
                    workflow_instance=instance,
                    workflow_step=instance.current_step,
                    action='terminate',
                    performed_by=request.user,
                    data={
                        'reason': request.data.get('reason', 'Terminated by user')
                    }
                )
                
                # Return the updated instance
                return Response(
                    WorkflowInstanceSerializer(instance).data
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class WorkflowStepLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing WorkflowStepLog entries (read-only).
    """
    queryset = WorkflowStepLog.objects.all()
    serializer_class = WorkflowStepLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = WorkflowStepLog.objects.all()
        
        # Filter by workflow instance
        instance_id = self.request.query_params.get('workflow_instance', None)
        if instance_id:
            queryset = queryset.filter(workflow_instance_id=instance_id)
            
        # Filter by workflow step
        step_id = self.request.query_params.get('workflow_step', None)
        if step_id:
            queryset = queryset.filter(workflow_step_id=step_id)
            
        # Filter by actor
        performed_by_id = self.request.query_params.get('performed_by', None)
        if performed_by_id:
            queryset = queryset.filter(performed_by_id=performed_by_id)
            
        # Filter by action
        action = self.request.query_params.get('action', None)
        if action:
            queryset = queryset.filter(action=action)
            
        return queryset
