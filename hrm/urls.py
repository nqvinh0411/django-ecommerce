from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    DepartmentViewSet,
    PositionViewSet,
    EmployeeViewSet,
    WorkScheduleViewSet,
    HolidayViewSet,
    TimesheetViewSet,
    LeaveRequestViewSet,
    SalaryViewSet,
    PayrollViewSet
)

app_name = 'hrm'

# Tạo router cho HRM API
router = DefaultRouter()
router.register('departments', DepartmentViewSet, basename='department')
router.register('positions', PositionViewSet, basename='position')
router.register('employees', EmployeeViewSet, basename='employee')
router.register('work-schedules', WorkScheduleViewSet, basename='work-schedule')
router.register('holidays', HolidayViewSet, basename='holiday')
router.register('timesheets', TimesheetViewSet, basename='timesheet')
router.register('leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register('salaries', SalaryViewSet, basename='salary')
router.register('payrolls', PayrollViewSet, basename='payroll')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
]
