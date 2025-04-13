from rest_framework import serializers
from ..models import Payroll


class PayrollSerializer(serializers.ModelSerializer):
    """
    Serializer for the Payroll model.
    """
    employee_name = serializers.ReadOnlyField(source='employee.full_name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    payment_method_display = serializers.ReadOnlyField(source='get_payment_method_display')
    approved_by_name = serializers.ReadOnlyField(source='approved_by.full_name')
    total_deductions = serializers.ReadOnlyField()
    total_allowances = serializers.ReadOnlyField()
    
    class Meta:
        model = Payroll
        fields = [
            'id', 'payroll_period', 'start_date', 'end_date', 'employee',
            'employee_name', 'salary', 'gross_amount', 'deductions',
            'allowances', 'net_amount', 'overtime_hours', 'overtime_rate',
            'payment_date', 'payment_method', 'payment_method_display',
            'payment_reference', 'status', 'status_display', 'approved_by',
            'approved_by_name', 'approved_at', 'notes', 'total_deductions',
            'total_allowances', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'employee_name', 'status_display',
            'payment_method_display', 'approved_by_name', 'total_deductions',
            'total_allowances'
        ]
    
    def validate(self, data):
        """
        Validate payroll data.
        """
        # Validate start_date and end_date
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })
        
        # Validate net_amount calculation
        if 'gross_amount' in data and 'deductions' in data and 'allowances' in data:
            total_deductions = sum(data['deductions'].values()) if data['deductions'] else 0
            total_allowances = sum(data['allowances'].values()) if data['allowances'] else 0
            calculated_net = data['gross_amount'] - total_deductions + total_allowances
            
            if 'net_amount' in data and abs(data['net_amount'] - calculated_net) > 0.01:
                raise serializers.ValidationError({
                    'net_amount': 'Net amount does not match the calculation of gross amount minus deductions plus allowances.'
                })
        
        return data
