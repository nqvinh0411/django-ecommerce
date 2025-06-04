from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkflowViewSet, WorkflowStepViewSet, WorkflowTransitionViewSet,
    WorkflowActionViewSet, WorkflowInstanceViewSet, WorkflowStepLogViewSet,
    WorkflowActorConfigViewSet, WorkflowConditionContextViewSet,
    ContentTypeViewSet
)

# Create a router and register our viewsets
router = DefaultRouter(trailing_slash=False)
router.register(r'workflows', WorkflowViewSet)
router.register(r'workflow-steps', WorkflowStepViewSet)
router.register(r'workflow-transitions', WorkflowTransitionViewSet)
router.register(r'workflow-actions', WorkflowActionViewSet)
router.register(r'workflow-instances', WorkflowInstanceViewSet)
router.register(r'workflow-step-logs', WorkflowStepLogViewSet)
router.register(r'workflow-actor-configs', WorkflowActorConfigViewSet)
router.register(r'workflow-condition-contexts', WorkflowConditionContextViewSet)
router.register(r'content-types', ContentTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
