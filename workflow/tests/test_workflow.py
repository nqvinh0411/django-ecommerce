from django.test import TestCase
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

from ..models import (
    Workflow, WorkflowStep, WorkflowTransition, WorkflowAction,
    WorkflowInstance, WorkflowStepLog, WorkflowActorConfig,
    WorkflowConditionContext
)
from ..services.engine import WorkflowEngine, start_workflow


class WorkflowModelTestCase(TestCase):
    """Test case for the Workflow model and related models."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass',
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass'
        )
        
        # Create test groups
        self.managers_group = Group.objects.create(name='Managers')
        self.staff_group = Group.objects.create(name='Staff')
        
        self.staff_user.groups.add(self.staff_group)
        
        # Create a test workflow for User model
        self.user_content_type = ContentType.objects.get_for_model(User)
        self.workflow = Workflow.objects.create(
            name='User Approval Workflow',
            description='Workflow for approving new users',
            is_active=True,
            content_type=self.user_content_type,
            created_by=self.admin_user,
            version=1
        )
        
        # Create workflow steps
        self.initial_review_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            name='Initial Review',
            description='Initial review of the user account',
            order=1,
            is_start=True,
            is_end=False
        )
        
        self.manager_approval_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            name='Manager Approval',
            description='Manager approval of the user account',
            order=2,
            is_start=False,
            is_end=False
        )
        
        self.final_approval_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            name='Final Approval',
            description='Final approval of the user account',
            order=3,
            is_start=False,
            is_end=True
        )
        
        self.rejection_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            name='Rejected',
            description='User account rejected',
            order=4,
            is_start=False,
            is_end=True
        )
        
        # Create workflow transitions
        self.transition1 = WorkflowTransition.objects.create(
            name='To Manager Approval',
            source_step=self.initial_review_step,
            target_step=self.manager_approval_step,
            condition_expression='',  # No condition
            priority=1
        )
        
        self.transition2 = WorkflowTransition.objects.create(
            name='Approve',
            source_step=self.manager_approval_step,
            target_step=self.final_approval_step,
            condition_expression='data.get("approved") == True',
            priority=1
        )
        
        self.transition3 = WorkflowTransition.objects.create(
            name='Reject',
            source_step=self.manager_approval_step,
            target_step=self.rejection_step,
            condition_expression='data.get("approved") == False',
            priority=1
        )
        
        # Create actor configurations
        self.actor_config1 = WorkflowActorConfig.objects.create(
            workflow_step=self.initial_review_step,
            actor_type='group',
            group=self.staff_group
        )
        
        self.actor_config2 = WorkflowActorConfig.objects.create(
            workflow_step=self.manager_approval_step,
            actor_type='group',
            group=self.managers_group
        )
        
        # Create a test action
        self.action = WorkflowAction.objects.create(
            workflow_step=self.final_approval_step,
            name='Send Approval Email',
            action_type='email',
            trigger_point='on_enter',
            configuration={
                'subject_template': 'User account approved: {{ object.username }}',
                'body_template': 'Dear {{ object.first_name }},\n\nYour account has been approved.',
                'recipient_type': 'field',
                'recipients': 'email'
            }
        )
    
    def test_workflow_creation(self):
        """Test that the workflow was created correctly."""
        self.assertEqual(self.workflow.name, 'User Approval Workflow')
        self.assertEqual(self.workflow.steps.count(), 4)
        self.assertEqual(self.workflow.get_start_step(), self.initial_review_step)
    
    def test_workflow_step_relationships(self):
        """Test the relationships between workflow steps and transitions."""
        self.assertEqual(self.initial_review_step.outgoing_transitions.count(), 1)
        self.assertEqual(self.manager_approval_step.incoming_transitions.count(), 1)
        self.assertEqual(self.manager_approval_step.outgoing_transitions.count(), 2)
    
    def test_actor_configuration(self):
        """Test actor configuration for workflow steps."""
        # Staff user should be able to act on initial review step (via group)
        self.assertTrue(
            self.actor_config1.can_user_act(self.staff_user)
        )
        
        # Regular user should not be able to act on any step
        self.assertFalse(
            self.actor_config1.can_user_act(self.regular_user)
        )
        
        # Admin should be able to act on any step (checked in permissions service)
        from ..services.permissions import can_user_process_step
        self.assertTrue(
            can_user_process_step(
                self.admin_user, 
                self.initial_review_step, 
                None  # No instance needed for this test
            )
        )


class WorkflowEngineTestCase(TestCase):
    """Test case for the Workflow engine and transitions."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass'
        )
        
        # Create a target user for the workflow
        self.target_user = User.objects.create_user(
            username='target',
            email='target@example.com',
            password='targetpass'
        )
        
        # Create a test workflow with branching and looping
        self.user_content_type = ContentType.objects.get_for_model(User)
        self.workflow = Workflow.objects.create(
            name='Complex Approval Workflow',
            description='Workflow with branching and looping',
            is_active=True,
            content_type=self.user_content_type,
            created_by=self.admin_user,
            version=1
        )
        
        # Create workflow steps
        self.start_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            name='Start',
            description='Start step',
            order=1,
            is_start=True,
            is_end=False
        )
        
        self.review_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            name='Review',
            description='Review step',
            order=2,
            is_start=False,
            is_end=False
        )
        
        self.additional_info_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            name='Request Additional Info',
            description='Request more information',
            order=3,
            is_start=False,
            is_end=False
        )
        
        self.approval_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            name='Approval',
            description='Final approval step',
            order=4,
            is_start=False,
            is_end=True
        )
        
        self.rejection_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            name='Rejection',
            description='Rejection step',
            order=5,
            is_start=False,
            is_end=True
        )
        
        # Create workflow transitions for branching
        self.transition1 = WorkflowTransition.objects.create(
            name='Start to Review',
            source_step=self.start_step,
            target_step=self.review_step,
            condition_expression='',  # No condition
            priority=1
        )
        
        self.transition2a = WorkflowTransition.objects.create(
            name='Review to Approval',
            source_step=self.review_step,
            target_step=self.approval_step,
            condition_expression='data.get("status") == "approve"',
            priority=1
        )
        
        self.transition2b = WorkflowTransition.objects.create(
            name='Review to Rejection',
            source_step=self.review_step,
            target_step=self.rejection_step,
            condition_expression='data.get("status") == "reject"',
            priority=1
        )
        
        self.transition2c = WorkflowTransition.objects.create(
            name='Review to Additional Info',
            source_step=self.review_step,
            target_step=self.additional_info_step,
            condition_expression='data.get("status") == "more_info"',
            priority=1
        )
        
        # Create a loop transition (back to review)
        self.transition3 = WorkflowTransition.objects.create(
            name='Additional Info to Review',
            source_step=self.additional_info_step,
            target_step=self.review_step,
            condition_expression='',  # No condition
            priority=1
        )
        
        # Create actor configurations - anyone can act for testing
        for step in [self.start_step, self.review_step, self.additional_info_step]:
            WorkflowActorConfig.objects.create(
                workflow_step=step,
                actor_type='user',
                user=self.admin_user
            )
    
    def test_start_workflow(self):
        """Test starting a workflow instance."""
        # Start the workflow
        instance = start_workflow(self.target_user, self.workflow.id, self.admin_user)
        
        # Check that the instance was created correctly
        self.assertEqual(instance.workflow, self.workflow)
        self.assertEqual(instance.content_object, self.target_user)
        self.assertEqual(instance.current_step, self.start_step)
        self.assertEqual(instance.status, 'active')
        
        # Check that a log entry was created
        self.assertEqual(instance.logs.count(), 1)
        log = instance.logs.first()
        self.assertEqual(log.action, 'start')
        self.assertEqual(log.workflow_step, self.start_step)
    
    def test_workflow_transition(self):
        """Test workflow transitions with conditions."""
        # Start the workflow
        instance = start_workflow(self.target_user, self.workflow.id, self.admin_user)
        
        # Process the start step
        instance.process_step('approve', self.admin_user)
        
        # Should have moved to review step
        instance.refresh_from_db()
        self.assertEqual(instance.current_step, self.review_step)
        
        # Process the review step with "approve" status
        instance.data['status'] = 'approve'
        instance.save()
        instance.process_step('approve', self.admin_user)
        
        # Should have moved to approval step
        instance.refresh_from_db()
        self.assertEqual(instance.current_step, self.approval_step)
        
        # Check logs
        self.assertEqual(instance.logs.count(), 3)  # start + 2 transitions
    
    def test_workflow_branching(self):
        """Test workflow branching based on conditions."""
        # Test branch 1: Approve
        instance1 = start_workflow(self.target_user, self.workflow.id, self.admin_user)
        instance1.process_step('approve', self.admin_user)  # Move to review
        
        instance1.data['status'] = 'approve'
        instance1.save()
        instance1.process_step('approve', self.admin_user)  # Choose approve branch
        
        instance1.refresh_from_db()
        self.assertEqual(instance1.current_step, self.approval_step)
        
        # Test branch 2: Reject
        instance2 = start_workflow(self.regular_user, self.workflow.id, self.admin_user)
        instance2.process_step('approve', self.admin_user)  # Move to review
        
        instance2.data['status'] = 'reject'
        instance2.save()
        instance2.process_step('approve', self.admin_user)  # Choose reject branch
        
        instance2.refresh_from_db()
        self.assertEqual(instance2.current_step, self.rejection_step)
    
    def test_workflow_looping(self):
        """Test workflow looping (returning to a previous step)."""
        instance = start_workflow(self.target_user, self.workflow.id, self.admin_user)
        instance.process_step('approve', self.admin_user)  # Move to review
        
        # Choose "more_info" branch to go to additional info step
        instance.data['status'] = 'more_info'
        instance.save()
        instance.process_step('approve', self.admin_user)
        
        instance.refresh_from_db()
        self.assertEqual(instance.current_step, self.additional_info_step)
        
        # Now process the additional info step to loop back to review
        instance.process_step('approve', self.admin_user)
        
        instance.refresh_from_db()
        self.assertEqual(instance.current_step, self.review_step)
        
        # Now approve to finish the workflow
        instance.data['status'] = 'approve'
        instance.save()
        instance.process_step('approve', self.admin_user)
        
        instance.refresh_from_db()
        self.assertEqual(instance.current_step, self.approval_step)
        self.assertEqual(instance.status, 'completed')  # Should be completed at end step


class WorkflowAPITestCase(APITestCase):
    """Test case for the Workflow API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass'
        )
        
        # Create a test workflow
        self.user_content_type = ContentType.objects.get_for_model(User)
        self.workflow = Workflow.objects.create(
            name='API Test Workflow',
            description='Workflow for API testing',
            is_active=True,
            content_type=self.user_content_type,
            created_by=self.admin_user,
            version=1
        )
        
        # Create workflow steps
        self.start_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            name='Start',
            description='Start step',
            order=1,
            is_start=True,
            is_end=False
        )
        
        self.end_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            name='End',
            description='End step',
            order=2,
            is_start=False,
            is_end=True
        )
        
        # Create workflow transition
        self.transition = WorkflowTransition.objects.create(
            name='Start to End',
            source_step=self.start_step,
            target_step=self.end_step,
            condition_expression='',  # No condition
            priority=1
        )
        
        # Create actor configuration
        self.actor_config = WorkflowActorConfig.objects.create(
            workflow_step=self.start_step,
            actor_type='user',
            user=self.admin_user
        )
    
    def test_list_workflows(self):
        """Test listing workflows."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('workflow-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'API Test Workflow')
    
    def test_start_workflow_api(self):
        """Test starting a workflow via API."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('workflow-start', args=[self.workflow.id])
        data = {
            'content_type_id': self.user_content_type.id,
            'object_id': self.regular_user.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that instance was created
        instance_id = response.data['id']
        instance = WorkflowInstance.objects.get(pk=instance_id)
        self.assertEqual(instance.workflow, self.workflow)
        self.assertEqual(instance.content_object, self.regular_user)
        self.assertEqual(instance.current_step, self.start_step)
    
    def test_process_workflow_step_api(self):
        """Test processing a workflow step via API."""
        # Start a workflow instance
        instance = start_workflow(
            self.regular_user, self.workflow.id, self.admin_user
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('workflowinstance-process', args=[instance.id])
        data = {
            'action': 'approve',
            'comment': 'Test approval'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that instance was updated
        instance.refresh_from_db()
        self.assertEqual(instance.current_step, self.end_step)
        self.assertEqual(instance.status, 'completed')
        
        # Check logs
        logs = instance.logs.all()
        self.assertEqual(logs.count(), 2)  # start + approve
        self.assertEqual(logs.last().action, 'approve')
        self.assertEqual(logs.last().data.get('comment'), 'Test approval')
