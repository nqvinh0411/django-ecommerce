from rest_framework import serializers
from ..models import LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the LeaveRequest model.
    """
    employee_name = serializers.ReadOnlyField(source='employee.full_name')
    reviewed_by_name = serializers.ReadOnlyField(source='reviewed_by.full_name')
    leave_type_display = serializers.ReadOnlyField(source='get_leave_type_display')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    duration_days = serializers.ReadOnlyField()
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'leave_type', 'leave_type_display', 
            'start_date', 'end_date', 'half_day', 'reason', 'status', 
            'status_display', 'reviewed_by', 'reviewed_by_name', 'reviewed_at', 
            'reviewer_comments', 'attachment', 'duration_days', 
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'employee_name', 'reviewed_by_name',
            'leave_type_display', 'status_display', 'duration_days'
        ]
    
    def validate(self, data):
        """
        Validate leave request data.
        """
        # Validate start_date and end_date
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after or equal to start date.'
                })
        
        return data
