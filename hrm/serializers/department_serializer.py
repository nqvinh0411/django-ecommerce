from rest_framework import serializers
from ..models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Department model.
    """
    child_departments_count = serializers.SerializerMethodField()
    employees_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'description', 'is_active', 
            'parent', 'manager', 'child_departments_count', 
            'employees_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_child_departments_count(self, obj):
        """Get the number of child departments."""
        return obj.child_departments.count()
    
    def get_employees_count(self, obj):
        """Get the number of employees in this department."""
        return obj.employees.count()
