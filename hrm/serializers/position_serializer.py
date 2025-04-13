from rest_framework import serializers
from ..models import Position


class PositionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Position model.
    """
    department_name = serializers.ReadOnlyField(source='department.name')
    employees_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Position
        fields = [
            'id', 'title', 'code', 'department', 'department_name',
            'description', 'requirements', 'is_active', 'min_salary',
            'max_salary', 'employees_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'department_name']
    
    def get_employees_count(self, obj):
        """Get the number of employees in this position."""
        return obj.employees.count()
