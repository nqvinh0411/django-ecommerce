from rest_framework import serializers
from ..models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Employee model.
    """
    department_name = serializers.ReadOnlyField(source='department.name')
    position_title = serializers.ReadOnlyField(source='position.title')
    supervisor_name = serializers.ReadOnlyField(source='supervisor.full_name')
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'employee_id', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'gender', 'email', 'phone', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
            'department', 'department_name', 'position', 'position_title',
            'employment_status', 'hire_date', 'termination_date',
            'supervisor', 'supervisor_name', 'profile_picture',
            'notes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'full_name',
            'department_name', 'position_title', 'supervisor_name'
        ]
        extra_kwargs = {
            'profile_picture': {'allow_null': True}
        }
