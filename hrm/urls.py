from django.urls import path

from .views import (
    # Department views
    DepartmentListView, DepartmentCreateView, DepartmentRetrieveUpdateDestroyView,
    # Position views
    PositionListView, PositionCreateView, PositionRetrieveUpdateDestroyView,
    # Employee views
    EmployeeListView, EmployeeCreateView, EmployeeRetrieveUpdateDestroyView,
    # WorkSchedule views
    WorkScheduleListView, WorkScheduleCreateView, WorkScheduleRetrieveUpdateDestroyView,
    # Holiday views
    HolidayListView, HolidayCreateView, HolidayRetrieveUpdateDestroyView,
    # Timesheet views
    TimesheetListView, TimesheetCreateView, TimesheetRetrieveUpdateDestroyView,
    # LeaveRequest views
    LeaveRequestListView, LeaveRequestCreateView, LeaveRequestRetrieveUpdateDestroyView,
    # Salary views
    SalaryListView, SalaryCreateView, SalaryRetrieveUpdateDestroyView,
    # Payroll views
    PayrollListView, PayrollCreateView, PayrollRetrieveUpdateDestroyView
)

app_name = 'hrm'

urlpatterns = [
    # Department endpoints
    path('/departments', DepartmentListView.as_view(), name='department-list'),
    path('/departments/create', DepartmentCreateView.as_view(), name='department-create'),
    path('/departments/<int:pk>', DepartmentRetrieveUpdateDestroyView.as_view(), name='department-detail'),
    path('/departments/<int:pk>/update', DepartmentRetrieveUpdateDestroyView.as_view(), name='department-update'),
    path('/departments/<int:pk>/delete', DepartmentRetrieveUpdateDestroyView.as_view(), name='department-delete'),

    # Position endpoints
    path('/positions', PositionListView.as_view(), name='position-list'),
    path('/positions/create', PositionCreateView.as_view(), name='position-create'),
    path('/positions/<int:pk>', PositionRetrieveUpdateDestroyView.as_view(), name='position-detail'),
    path('/positions/<int:pk>/update', PositionRetrieveUpdateDestroyView.as_view(), name='position-update'),
    path('/positions/<int:pk>/delete', PositionRetrieveUpdateDestroyView.as_view(), name='position-delete'),

    # Employee endpoints
    path('/employees', EmployeeListView.as_view(), name='employee-list'),
    path('/employees/create', EmployeeCreateView.as_view(), name='employee-create'),
    path('/employees/<int:pk>', EmployeeRetrieveUpdateDestroyView.as_view(), name='employee-detail'),
    path('/employees/<int:pk>/update', EmployeeRetrieveUpdateDestroyView.as_view(), name='employee-update'),
    path('/employees/<int:pk>/delete', EmployeeRetrieveUpdateDestroyView.as_view(), name='employee-delete'),

    # WorkSchedule endpoints
    path('/work-schedules', WorkScheduleListView.as_view(), name='work-schedule-list'),
    path('/work-schedules/create', WorkScheduleCreateView.as_view(), name='work-schedule-create'),
    path('/work-schedules/<int:pk>', WorkScheduleRetrieveUpdateDestroyView.as_view(), name='work-schedule-detail'),
    path('/work-schedules/<int:pk>/update', WorkScheduleRetrieveUpdateDestroyView.as_view(), name='work-schedule-update'),
    path('/work-schedules/<int:pk>/delete', WorkScheduleRetrieveUpdateDestroyView.as_view(), name='work-schedule-delete'),

    # Holiday endpoints
    path('/holidays', HolidayListView.as_view(), name='holiday-list'),
    path('/holidays/create', HolidayCreateView.as_view(), name='holiday-create'),
    path('/holidays/<int:pk>', HolidayRetrieveUpdateDestroyView.as_view(), name='holiday-detail'),
    path('/holidays/<int:pk>/update', HolidayRetrieveUpdateDestroyView.as_view(), name='holiday-update'),
    path('/holidays/<int:pk>/delete', HolidayRetrieveUpdateDestroyView.as_view(), name='holiday-delete'),

    # Timesheet endpoints
    path('/timesheets', TimesheetListView.as_view(), name='timesheet-list'),
    path('/timesheets/create', TimesheetCreateView.as_view(), name='timesheet-create'),
    path('/timesheets/<int:pk>', TimesheetRetrieveUpdateDestroyView.as_view(), name='timesheet-detail'),
    path('/timesheets/<int:pk>/update', TimesheetRetrieveUpdateDestroyView.as_view(), name='timesheet-update'),
    path('/timesheets/<int:pk>/delete', TimesheetRetrieveUpdateDestroyView.as_view(), name='timesheet-delete'),

    # LeaveRequest endpoints
    path('/leave-requests', LeaveRequestListView.as_view(), name='leave-request-list'),
    path('/leave-requests/create', LeaveRequestCreateView.as_view(), name='leave-request-create'),
    path('/leave-requests/<int:pk>', LeaveRequestRetrieveUpdateDestroyView.as_view(), name='leave-request-detail'),
    path('/leave-requests/<int:pk>/update', LeaveRequestRetrieveUpdateDestroyView.as_view(), name='leave-request-update'),
    path('/leave-requests/<int:pk>/delete', LeaveRequestRetrieveUpdateDestroyView.as_view(), name='leave-request-delete'),

    # Salary endpoints
    path('/salaries', SalaryListView.as_view(), name='salary-list'),
    path('/salaries/create', SalaryCreateView.as_view(), name='salary-create'),
    path('/salaries/<int:pk>', SalaryRetrieveUpdateDestroyView.as_view(), name='salary-detail'),
    path('/salaries/<int:pk>/update', SalaryRetrieveUpdateDestroyView.as_view(), name='salary-update'),
    path('/salaries/<int:pk>/delete', SalaryRetrieveUpdateDestroyView.as_view(), name='salary-delete'),

    # Payroll endpoints
    path('/payrolls', PayrollListView.as_view(), name='payroll-list'),
    path('/payrolls/create', PayrollCreateView.as_view(), name='payroll-create'),
    path('/payrolls/<int:pk>', PayrollRetrieveUpdateDestroyView.as_view(), name='payroll-detail'),
    path('/payrolls/<int:pk>/update', PayrollRetrieveUpdateDestroyView.as_view(), name='payroll-update'),
    path('/payrolls/<int:pk>/delete', PayrollRetrieveUpdateDestroyView.as_view(), name='payroll-delete'),
]
