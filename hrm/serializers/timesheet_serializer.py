from rest_framework import serializers
from ..models import Timesheet


class TimesheetSerializer(serializers.ModelSerializer):
    """
    Serializer for the Timesheet model.
    """
    employee_name = serializers.ReadOnlyField(source='employee.full_name')
    approved_by_name = serializers.ReadOnlyField(source='approved_by.full_name')
    work_duration = serializers.ReadOnlyField()
    
    class Meta:
        model = Timesheet
        fields = [
            'id', 'employee', 'employee_name', 'date', 'check_in', 'check_out',
            'break_duration', 'status', 'approved_by', 'approved_by_name',
            'approved_at', 'notes', 'work_duration', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'employee_name', 
            'approved_by_name', 'work_duration'
        ]
    
    def validate(self, data):
        """
        Validate timesheet data.
        """
        # Validate check_in and check_out times
        if 'check_in' in data and 'check_out' in data and data['check_out']:
            if data['check_in'] >= data['check_out']:
                raise serializers.ValidationError({
                    'check_out': 'Check-out time must be after check-in time.'
                })
        
        return data
