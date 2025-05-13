"""
Workflow Actions Service

This module contains implementations for different types of workflow actions,
such as sending emails, making API calls, updating records, etc.
"""
import logging
import json
import requests
from django.core.mail import send_mail
from django.template import Template, Context
from django.db import transaction
from django.apps import apps
from django.conf import settings

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Base class for executing workflow actions."""
    
    def execute(self, action, workflow_instance, context):
        """
        Execute the workflow action.
        
        Args:
            action: The WorkflowAction to execute
            workflow_instance: The WorkflowInstance context
            context: Additional context for action execution
            
        Returns:
            dict: The result of the action execution
        """
        action_type = action.action_type
        
        # Dispatch to appropriate handler
        if action_type == 'email':
            return self._execute_email_action(action, workflow_instance, context)
        elif action_type == 'api':
            return self._execute_api_action(action, workflow_instance, context)
        elif action_type == 'update':
            return self._execute_update_action(action, workflow_instance, context)
        elif action_type == 'function':
            return self._execute_function_action(action, workflow_instance, context)
        elif action_type == 'notification':
            return self._execute_notification_action(action, workflow_instance, context)
        else:
            error_msg = f"Unsupported action type: {action_type}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _execute_email_action(self, action, workflow_instance, context):
        """
        Send an email based on action configuration.
        
        Configuration format:
        {
            "subject_template": "Email subject with {{ variables }}",
            "body_template": "Email body with {{ variables }}",
            "from_email": "sender@example.com",
            "recipient_type": "static|field|expression",
            "recipients": ["email1@example.com"] or "field_name" or "expression"
            "cc": ["cc1@example.com"],
            "bcc": ["bcc1@example.com"],
            "html_email": true|false
        }
        """
        try:
            config = action.configuration
            
            # Get subject and body from templates
            subject_template = Template(config.get('subject_template', ''))
            body_template = Template(config.get('body_template', ''))
            
            # Create template context
            template_context = Context(self._prepare_template_context(workflow_instance, context))
            
            # Render templates
            subject = subject_template.render(template_context)
            body = body_template.render(template_context)
            
            # Get recipients
            recipients = self._get_email_recipients(config, workflow_instance, context)
            
            if not recipients:
                return {
                    "status": "error",
                    "message": "No recipients specified for email action"
                }
                
            # Get sender
            from_email = config.get('from_email', settings.DEFAULT_FROM_EMAIL)
            
            # Get CC and BCC
            cc = config.get('cc', [])
            bcc = config.get('bcc', [])
            
            # Send email
            is_html = config.get('html_email', False)
            html_message = body if is_html else None
            
            send_mail(
                subject=subject,
                message=body if not is_html else '',
                from_email=from_email,
                recipient_list=recipients,
                html_message=html_message,
                fail_silently=False,
                cc=cc,
                bcc=bcc
            )
            
            return {
                "status": "success",
                "message": f"Email sent to {', '.join(recipients)}",
                "details": {
                    "subject": subject,
                    "recipients": recipients
                }
            }
            
        except Exception as e:
            error_msg = f"Error executing email action: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _get_email_recipients(self, config, workflow_instance, context):
        """
        Get email recipients based on configuration.
        
        Args:
            config: The action configuration
            workflow_instance: The workflow instance
            context: The action context
            
        Returns:
            list: List of email addresses
        """
        recipient_type = config.get('recipient_type', 'static')
        recipients_config = config.get('recipients', [])
        
        if recipient_type == 'static':
            # Static list of recipients
            return recipients_config
            
        elif recipient_type == 'field':
            # Get recipient from a field on the target object
            target = workflow_instance.content_object
            field_name = recipients_config
            
            if not target or not hasattr(target, field_name):
                return []
                
            field_value = getattr(target, field_name)
            
            # Handle different field types
            if isinstance(field_value, str):
                # Single email address
                return [field_value]
            elif hasattr(field_value, '__iter__'):
                # List of email addresses
                return list(field_value)
            else:
                # Try to get email from user/profile object
                if hasattr(field_value, 'email'):
                    return [field_value.email]
                return []
                
        elif recipient_type == 'expression':
            # Evaluate expression to get recipients
            # This would need a secure evaluation mechanism
            return []
            
        return []
    
    def _execute_api_action(self, action, workflow_instance, context):
        """
        Make an API call based on action configuration.
        
        Configuration format:
        {
            "method": "GET|POST|PUT|DELETE",
            "url_template": "https://example.com/api/{{ variables }}",
            "headers": {"Content-Type": "application/json", ...},
            "body_template": "{\"key\": \"{{ value }}\"}",
            "auth_type": "none|basic|token|oauth",
            "auth_credentials": {...},
            "timeout": 30,
            "success_codes": [200, 201]
        }
        """
        try:
            config = action.configuration
            
            # Get method
            method = config.get('method', 'GET').upper()
            
            # Get URL from template
            url_template = Template(config.get('url_template', ''))
            template_context = Context(self._prepare_template_context(workflow_instance, context))
            url = url_template.render(template_context)
            
            # Get headers
            headers = config.get('headers', {})
            
            # Get body from template if present
            body = None
            if 'body_template' in config:
                body_template = Template(config.get('body_template', ''))
                body = body_template.render(template_context)
                
                # Parse JSON body if applicable
                if 'Content-Type' in headers and 'application/json' in headers['Content-Type']:
                    body = json.loads(body)
                    
            # Get timeout
            timeout = config.get('timeout', 30)
            
            # Get authentication
            auth = None
            auth_type = config.get('auth_type', 'none')
            
            if auth_type == 'basic':
                auth = (
                    config.get('auth_credentials', {}).get('username', ''),
                    config.get('auth_credentials', {}).get('password', '')
                )
            
            # Make the request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=body if isinstance(body, dict) else None,
                data=body if isinstance(body, str) else None,
                auth=auth,
                timeout=timeout
            )
            
            # Check if response is successful
            success_codes = config.get('success_codes', [200, 201, 202, 204])
            is_success = response.status_code in success_codes
            
            result = {
                "status": "success" if is_success else "error",
                "status_code": response.status_code,
                "message": f"API call {method} {url} returned {response.status_code}",
                "details": {
                    "method": method,
                    "url": url,
                    "response_headers": dict(response.headers),
                }
            }
            
            # Add response content if present
            try:
                result["response"] = response.json()
            except ValueError:
                result["response"] = response.text[:1000]  # Limit text size
                
            return result
            
        except Exception as e:
            error_msg = f"Error executing API action: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _execute_update_action(self, action, workflow_instance, context):
        """
        Update a database record based on action configuration.
        
        Configuration format:
        {
            "target_type": "self|related|model",
            "related_object_path": "field.subfield",  # For related objects
            "model_app_label": "app_label",  # For model target type
            "model_name": "ModelName",       # For model target type
            "object_id_field": "id",         # For model target type
            "fields": {
                "field1": "value1",
                "field2": "{{ variable }}",
                "field3": {
                    "type": "expression",
                    "value": "{{ obj.field1 + obj.field2 }}"
                }
            }
        }
        """
        try:
            config = action.configuration
            
            # Get target type
            target_type = config.get('target_type', 'self')
            
            # Determine target object
            target = None
            
            if target_type == 'self':
                # Update the workflow instance's target object
                target = workflow_instance.content_object
                
            elif target_type == 'related':
                # Update a related object
                target = workflow_instance.content_object
                path = config.get('related_object_path', '').split('.')
                
                for part in path:
                    if target and hasattr(target, part):
                        target = getattr(target, part)
                    else:
                        return {
                            "status": "error",
                            "message": f"Could not resolve related object path: {config.get('related_object_path')}"
                        }
                        
            elif target_type == 'model':
                # Update a model instance by ID
                app_label = config.get('model_app_label')
                model_name = config.get('model_name')
                object_id_field = config.get('object_id_field', 'id')
                object_id = config.get('object_id')
                
                if not (app_label and model_name and object_id):
                    return {
                        "status": "error",
                        "message": "Missing required fields for model target type"
                    }
                    
                try:
                    model_class = apps.get_model(app_label, model_name)
                    lookup = {object_id_field: object_id}
                    target = model_class.objects.get(**lookup)
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Could not find model instance: {str(e)}"
                    }
            
            if not target:
                return {
                    "status": "error",
                    "message": "No target object found to update"
                }
                
            # Get fields to update
            fields = config.get('fields', {})
            
            if not fields:
                return {
                    "status": "warning",
                    "message": "No fields specified for update action"
                }
                
            # Prepare template context
            template_context = self._prepare_template_context(workflow_instance, context)
            
            # Update fields
            changes = {}
            with transaction.atomic():
                for field_name, field_config in fields.items():
                    if not hasattr(target, field_name):
                        logger.warning(f"Field {field_name} does not exist on target")
                        continue
                        
                    # Get current value for change tracking
                    old_value = getattr(target, field_name)
                    
                    # Determine new value
                    if isinstance(field_config, str):
                        # String value - may contain template variables
                        template = Template(field_config)
                        new_value = template.render(Context(template_context))
                    elif isinstance(field_config, dict) and field_config.get('type') == 'expression':
                        # Expression value - would need a secure evaluation mechanism
                        # For demonstration, just use a simple template rendering
                        template = Template(field_config.get('value', ''))
                        new_value = template.render(Context(template_context))
                    else:
                        # Direct value
                        new_value = field_config
                        
                    # Update the field
                    setattr(target, field_name, new_value)
                    
                    # Track changes
                    changes[field_name] = {
                        'old': old_value,
                        'new': new_value
                    }
                    
                # Save the object
                target.save()
                
            return {
                "status": "success",
                "message": f"Updated {len(changes)} fields on {target._meta.model.__name__} #{target.pk}",
                "details": {
                    "changes": changes
                }
            }
            
        except Exception as e:
            error_msg = f"Error executing update action: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _execute_function_action(self, action, workflow_instance, context):
        """
        Call a registered function based on action configuration.
        
        Configuration format:
        {
            "function_path": "module.submodule.function_name",
            "args": ["arg1", "{{ variable }}"],
            "kwargs": {
                "key1": "value1",
                "key2": "{{ variable }}"
            }
        }
        """
        try:
            config = action.configuration
            
            # Get function path
            function_path = config.get('function_path')
            
            if not function_path:
                return {
                    "status": "error",
                    "message": "No function path specified"
                }
                
            # Get function arguments
            args = config.get('args', [])
            kwargs = config.get('kwargs', {})
            
            # Prepare template context
            template_context = self._prepare_template_context(workflow_instance, context)
            
            # Process template variables in args and kwargs
            processed_args = []
            for arg in args:
                if isinstance(arg, str):
                    template = Template(arg)
                    processed_args.append(template.render(Context(template_context)))
                else:
                    processed_args.append(arg)
                    
            processed_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    template = Template(value)
                    processed_kwargs[key] = template.render(Context(template_context))
                else:
                    processed_kwargs[key] = value
                    
            # Import and call the function
            module_path, function_name = function_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[function_name])
            function = getattr(module, function_name)
            
            result = function(*processed_args, **processed_kwargs)
            
            return {
                "status": "success",
                "message": f"Called function {function_path}",
                "result": result
            }
            
        except Exception as e:
            error_msg = f"Error executing function action: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _execute_notification_action(self, action, workflow_instance, context):
        """
        Send a notification based on action configuration.
        
        Configuration format:
        {
            "notification_type": "in_app|push|sms",
            "title_template": "Notification title with {{ variables }}",
            "message_template": "Notification message with {{ variables }}",
            "recipient_type": "user|role|expression",
            "recipients": [1, 2] or "role_name" or "expression",
            "priority": "low|medium|high",
            "data": {
                "key1": "value1",
                "key2": "{{ variable }}"
            }
        }
        """
        try:
            config = action.configuration
            
            # Get notification type
            notification_type = config.get('notification_type', 'in_app')
            
            # Get title and message from templates
            title_template = Template(config.get('title_template', ''))
            message_template = Template(config.get('message_template', ''))
            
            # Create template context
            template_context = Context(self._prepare_template_context(workflow_instance, context))
            
            # Render templates
            title = title_template.render(template_context)
            message = message_template.render(template_context)
            
            # Get recipients
            recipients = self._get_notification_recipients(config, workflow_instance, context)
            
            if not recipients:
                return {
                    "status": "error",
                    "message": "No recipients specified for notification action"
                }
                
            # Get priority
            priority = config.get('priority', 'medium')
            
            # Get additional data
            data = config.get('data', {})
            
            # Process template variables in data
            processed_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    template = Template(value)
                    processed_data[key] = template.render(template_context)
                else:
                    processed_data[key] = value
                    
            # This would integrate with your notification system
            # For demonstration, we'll just log the notification
            logger.info(
                f"Notification ({notification_type}, {priority}): {title} - "
                f"To: {recipients}, Message: {message}, Data: {processed_data}"
            )
            
            # In a real implementation, you would call your notification service
            # Example:
            # from notifications.services import send_notification
            # for recipient in recipients:
            #     send_notification(
            #         recipient=recipient,
            #         notification_type=notification_type,
            #         title=title,
            #         message=message,
            #         priority=priority,
            #         data=processed_data
            #     )
            
            return {
                "status": "success",
                "message": f"Notification sent to {len(recipients)} recipients",
                "details": {
                    "type": notification_type,
                    "title": title,
                    "recipients": recipients
                }
            }
            
        except Exception as e:
            error_msg = f"Error executing notification action: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _get_notification_recipients(self, config, workflow_instance, context):
        """
        Get notification recipients based on configuration.
        
        Args:
            config: The action configuration
            workflow_instance: The workflow instance
            context: The action context
            
        Returns:
            list: List of recipient IDs or objects
        """
        recipient_type = config.get('recipient_type', 'user')
        recipients_config = config.get('recipients', [])
        
        if recipient_type == 'user':
            # List of user IDs
            return recipients_config
            
        elif recipient_type == 'role':
            # Get users with a specific role
            role_name = recipients_config
            
            # This would need to be implemented based on your role system
            # Example:
            # return list(User.objects.filter(profile__roles__name=role_name).values_list('id', flat=True))
            return []
            
        elif recipient_type == 'expression':
            # Evaluate expression to get recipients
            # This would need a secure evaluation mechanism
            return []
            
        return []
    
    def _prepare_template_context(self, workflow_instance, context):
        """
        Prepare context for template rendering.
        
        Args:
            workflow_instance: The workflow instance
            context: The action context
            
        Returns:
            dict: Context dictionary for template rendering
        """
        template_context = {
            'workflow': {
                'id': workflow_instance.workflow.id,
                'name': workflow_instance.workflow.name,
                'description': workflow_instance.workflow.description
            },
            'instance': {
                'id': workflow_instance.id,
                'status': workflow_instance.status,
                'created_at': workflow_instance.created_at,
                'updated_at': workflow_instance.updated_at,
                'data': workflow_instance.data
            },
            'step': {
                'id': workflow_instance.current_step.id if workflow_instance.current_step else None,
                'name': workflow_instance.current_step.name if workflow_instance.current_step else None,
                'description': workflow_instance.current_step.description if workflow_instance.current_step else None
            },
            'user': None,
            'object': {}
        }
        
        # Add user information
        if workflow_instance.current_user:
            user = workflow_instance.current_user
            template_context['user'] = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined
            }
            
        # Add target object attributes
        if workflow_instance.content_object:
            obj = workflow_instance.content_object
            
            # Basic object info
            template_context['object'] = {
                'id': obj.pk,
                'model': obj._meta.model_name,
                'app': obj._meta.app_label
            }
            
            # Add all fields
            for field in obj._meta.fields:
                field_name = field.name
                if hasattr(obj, field_name):
                    template_context['object'][field_name] = getattr(obj, field_name)
                    
        # Add additional context
        if context:
            template_context.update(context)
            
        return template_context


# Singleton instance
action_executor = ActionExecutor()


def execute_action(action, workflow_instance, context=None):
    """
    Convenience function to execute a workflow action.
    
    Args:
        action: The WorkflowAction to execute
        workflow_instance: The WorkflowInstance context
        context: Additional context for action execution
        
    Returns:
        dict: The result of the action execution
    """
    return action_executor.execute(action, workflow_instance, context)
