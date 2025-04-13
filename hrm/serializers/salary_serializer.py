from rest_framework import serializers
from ..models import Salary


class SalarySerializer(serializers.ModelSerializer):
    """
    Serializer for the Salary model.
    """
    employee_name = serializers.ReadOnlyField(source='employee.full_name')
    salary_type_display = serializers.ReadOnlyField(source='get_salary_type_display')
    total_allowances = serializers.ReadOnlyField()
    total_deductions = serializers.ReadOnlyField()
    net_salary = serializers.ReadOnlyField()
    
    class Meta:
        model = Salary
        fields = [
            'id', 'employee', 'employee_name', 'salary_type', 'salary_type_display',
            'base_salary', 'currency', 'allowances', 'deductions',
            'total_allowances', 'total_deductions', 'net_salary',
            'effective_date', 'end_date', 'is_active', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'employee_name', 'salary_type_display',
            'total_allowances', 'total_deductions', 'net_salary'
        ]
    
    def validate(self, data):
        """
        Validate salary data.
        """
        # Validate effective_date and end_date
        if 'effective_date' in data and 'end_date' in data and data['end_date']:
            if data['effective_date'] >= data['end_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after effective date.'
                })
        
        # Validate that min_salary is less than max_salary
        if 'min_salary' in data and 'max_salary' in data and data['min_salary'] and data['max_salary']:
            if data['min_salary'] >= data['max_salary']:
                raise serializers.ValidationError({
                    'max_salary': 'Maximum salary must be greater than minimum salary.'
                })
        
        return data
