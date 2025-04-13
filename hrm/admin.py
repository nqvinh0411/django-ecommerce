from django.contrib import admin
from .models import (
    Department,
    Position,
    Employee,
    WorkSchedule,
    Holiday,
    Timesheet,
    LeaveRequest,
    Salary,
    Payroll
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'parent', 'manager', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'department', 'is_active', 'min_salary', 'max_salary')
    list_filter = ('department', 'is_active', 'created_at')
    search_fields = ('title', 'code', 'description', 'requirements')
    ordering = ('title',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'department', 'position', 'employment_status', 'hire_date', 'is_active')
    list_filter = ('department', 'position', 'employment_status', 'is_active', 'hire_date')
    search_fields = ('first_name', 'last_name', 'employee_id', 'email', 'phone')
    ordering = ('last_name', 'first_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'employee_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'profile_picture')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Employment Details', {
            'fields': ('department', 'position', 'employment_status', 'hire_date', 'termination_date', 'supervisor')
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'schedule_type', 'start_time', 'end_time', 'effective_date', 'is_active')
    list_filter = ('department', 'schedule_type', 'is_active', 'effective_date')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'holiday_type', 'is_paid', 'recurring')
    list_filter = ('holiday_type', 'is_paid', 'recurring', 'date')
    search_fields = ('name', 'description')
    ordering = ('date',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('applicable_departments',)


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status', 'work_duration')
    list_filter = ('status', 'date')
    search_fields = ('employee__first_name', 'employee__last_name', 'notes')
    ordering = ('-date', '-check_in')
    readonly_fields = ('work_duration', 'created_at', 'updated_at')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'duration_days')
    list_filter = ('leave_type', 'status', 'start_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'reason', 'reviewer_comments')
    ordering = ('-start_date',)
    readonly_fields = ('duration_days', 'created_at', 'updated_at')


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'salary_type', 'base_salary', 'currency', 'effective_date', 'is_active')
    list_filter = ('salary_type', 'currency', 'is_active', 'effective_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'notes')
    ordering = ('-effective_date',)
    readonly_fields = ('total_allowances', 'total_deductions', 'net_salary', 'created_at', 'updated_at')


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'payroll_period', 'gross_amount', 'net_amount', 'payment_date', 'status')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'payroll_period', 'payment_reference')
    ordering = ('-payroll_period', 'employee__last_name')
    readonly_fields = ('total_allowances', 'total_deductions', 'created_at', 'updated_at')
