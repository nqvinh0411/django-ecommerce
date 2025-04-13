from rest_framework import serializers
from ..models import WorkSchedule


class WorkScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for the WorkSchedule model.
    """
    department_name = serializers.ReadOnlyField(source='department.name')
    
    class Meta:
        model = WorkSchedule
        fields = [
            'id', 'name', 'department', 'department_name', 
            'schedule_type', 'start_time', 'end_time', 
            'working_days', 'break_duration', 'is_active',
            'effective_date', 'expiration_date', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'department_name']
    
    def validate(self, data):
        """
        Validate the schedule data.
        """
        # Validate working_days to ensure they are valid day numbers
        if 'working_days' in data:
            for day in data['working_days']:
                if not (1 <= day <= 7):
                    raise serializers.ValidationError({
                        'working_days': f'Invalid day number: {day}. Must be between 1 and 7.'
                    })
                    
        # Validate that start_time is before end_time
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError({
                    'end_time': 'End time must be after start time.'
                })
                
        # Validate effective and expiration dates if both provided
        if 'effective_date' in data and 'expiration_date' in data and data['expiration_date']:
            if data['effective_date'] > data['expiration_date']:
                raise serializers.ValidationError({
                    'expiration_date': 'Expiration date must be after effective date.'
                })
                
        return data
