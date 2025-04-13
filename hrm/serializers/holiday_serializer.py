from rest_framework import serializers
from ..models import Holiday


class HolidaySerializer(serializers.ModelSerializer):
    """
    Serializer for the Holiday model.
    """
    applicable_departments_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Holiday
        fields = [
            'id', 'name', 'date', 'holiday_type', 'description',
            'is_paid', 'recurring', 'applicable_departments',
            'applicable_departments_names', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'applicable_departments_names']
    
    def get_applicable_departments_names(self, obj):
        """Get the names of departments to which this holiday applies."""
        return [dept.name for dept in obj.applicable_departments.all()]
