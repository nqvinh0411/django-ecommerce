from .department_view import DepartmentListView, DepartmentCreateView, DepartmentRetrieveUpdateDestroyView
from .position_view import PositionListView, PositionCreateView, PositionRetrieveUpdateDestroyView
from .employee_view import EmployeeListView, EmployeeCreateView, EmployeeRetrieveUpdateDestroyView
from .work_schedule_view import WorkScheduleListView, WorkScheduleCreateView, WorkScheduleRetrieveUpdateDestroyView
from .holiday_view import HolidayListView, HolidayCreateView, HolidayRetrieveUpdateDestroyView
from .timesheet_view import TimesheetListView, TimesheetCreateView, TimesheetRetrieveUpdateDestroyView
from .leave_request_view import LeaveRequestListView, LeaveRequestCreateView, LeaveRequestRetrieveUpdateDestroyView
from .salary_view import SalaryListView, SalaryCreateView, SalaryRetrieveUpdateDestroyView
from .payroll_view import PayrollListView, PayrollCreateView, PayrollRetrieveUpdateDestroyView

__all__ = [
    # Department views
    'DepartmentListView', 'DepartmentCreateView', 'DepartmentRetrieveUpdateDestroyView',
    # Position views
    'PositionListView', 'PositionCreateView', 'PositionRetrieveUpdateDestroyView',
    # Employee views
    'EmployeeListView', 'EmployeeCreateView', 'EmployeeRetrieveUpdateDestroyView',
    # WorkSchedule views
    'WorkScheduleListView', 'WorkScheduleCreateView', 'WorkScheduleRetrieveUpdateDestroyView',
    # Holiday views
    'HolidayListView', 'HolidayCreateView', 'HolidayRetrieveUpdateDestroyView',
    # Timesheet views
    'TimesheetListView', 'TimesheetCreateView', 'TimesheetRetrieveUpdateDestroyView',
    # LeaveRequest views
    'LeaveRequestListView', 'LeaveRequestCreateView', 'LeaveRequestRetrieveUpdateDestroyView',
    # Salary views
    'SalaryListView', 'SalaryCreateView', 'SalaryRetrieveUpdateDestroyView',
    # Payroll views
    'PayrollListView', 'PayrollCreateView', 'PayrollRetrieveUpdateDestroyView'
]
