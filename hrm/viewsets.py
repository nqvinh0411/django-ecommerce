"""
HRM API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho HRM API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet
from core.permissions.base import IsAdminOrReadOnly
from core.optimization.decorators import log_slow_queries
from core.optimization.mixins import QueryOptimizationMixin
from drf_spectacular.utils import extend_schema

from .models.department import Department
from .models.position import Position
from .models.employee import Employee
from .models.work_schedule import WorkSchedule
from .models.holiday import Holiday
from .models.timesheet import Timesheet
from .models.leave_request import LeaveRequest
from .models.salary import Salary
from .models.payroll import Payroll

from .serializers.department_serializer import DepartmentSerializer
from .serializers.position_serializer import PositionSerializer
from .serializers.employee_serializer import EmployeeSerializer
from .serializers.work_schedule_serializer import WorkScheduleSerializer
from .serializers.holiday_serializer import HolidaySerializer
from .serializers.timesheet_serializer import TimesheetSerializer
from .serializers.leave_request_serializer import LeaveRequestSerializer
from .serializers.salary_serializer import SalarySerializer
from .serializers.payroll_serializer import PayrollSerializer


@extend_schema(tags=['HRM'])
class DepartmentViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Department resources.
    
    Cung cấp các operations CRUD cho phòng ban với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/departments/ - Liệt kê tất cả phòng ban
    - POST /api/v1/hrm/departments/ - Tạo phòng ban mới
    - GET /api/v1/hrm/departments/{id}/ - Xem chi tiết phòng ban
    - PUT/PATCH /api/v1/hrm/departments/{id}/ - Cập nhật phòng ban
    - DELETE /api/v1/hrm/departments/{id}/ - Xóa phòng ban
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def employees(self, request, pk=None):
        """
        Lấy danh sách nhân viên thuộc phòng ban.
        """
        department = self.get_object()
        employees = department.employees.all()
        page = self.paginate_queryset(employees)
        
        if page is not None:
            serializer = EmployeeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EmployeeSerializer(employees, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách nhân viên thuộc phòng ban {department.name}",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['HRM'])
class PositionViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Position resources.
    
    Cung cấp các operations CRUD cho chức vụ với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/positions/ - Liệt kê tất cả chức vụ
    - POST /api/v1/hrm/positions/ - Tạo chức vụ mới
    - GET /api/v1/hrm/positions/{id}/ - Xem chi tiết chức vụ
    - PUT/PATCH /api/v1/hrm/positions/{id}/ - Cập nhật chức vụ
    - DELETE /api/v1/hrm/positions/{id}/ - Xóa chức vụ
    """
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at']
    ordering = ['title']

    @action(detail=True, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def employees(self, request, pk=None):
        """
        Lấy danh sách nhân viên giữ chức vụ này.
        """
        position = self.get_object()
        employees = position.employees.all()
        page = self.paginate_queryset(employees)
        
        if page is not None:
            serializer = EmployeeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EmployeeSerializer(employees, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách nhân viên giữ chức vụ {position.title}",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['HRM'])
class EmployeeViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Employee resources.
    
    Cung cấp các operations CRUD cho nhân viên với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/employees/ - Liệt kê tất cả nhân viên
    - POST /api/v1/hrm/employees/ - Tạo nhân viên mới
    - GET /api/v1/hrm/employees/{id}/ - Xem chi tiết nhân viên
    - PUT/PATCH /api/v1/hrm/employees/{id}/ - Cập nhật nhân viên
    - DELETE /api/v1/hrm/employees/{id}/ - Xóa nhân viên
    - GET /api/v1/hrm/employees/{id}/subordinates/ - Xem danh sách cấp dưới
    - GET /api/v1/hrm/employees/{id}/timesheets/ - Xem bảng chấm công
    - GET /api/v1/hrm/employees/{id}/leave-requests/ - Xem yêu cầu nghỉ phép
    - GET /api/v1/hrm/employees/{id}/payrolls/ - Xem bảng lương
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'position', 'employment_status', 'is_active']
    search_fields = ['first_name', 'last_name', 'employee_id', 'email']
    ordering_fields = ['last_name', 'first_name', 'hire_date', 'department__name']
    ordering = ['last_name', 'first_name']
    
    select_related_fields = ['department', 'position', 'supervisor']
    
    @action(detail=True, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def subordinates(self, request, pk=None):
        """
        Lấy danh sách nhân viên cấp dưới của nhân viên này.
        """
        employee = self.get_object()
        subordinates = employee.subordinates.all()
        page = self.paginate_queryset(subordinates)
        
        if page is not None:
            serializer = EmployeeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EmployeeSerializer(subordinates, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách nhân viên cấp dưới của {employee.full_name}",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def timesheets(self, request, pk=None):
        """
        Lấy bảng chấm công của nhân viên này.
        """
        employee = self.get_object()
        timesheets = Timesheet.objects.filter(employee=employee)
        
        # Lọc theo khoảng thời gian nếu có
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            timesheets = timesheets.filter(date__gte=start_date)
        if end_date:
            timesheets = timesheets.filter(date__lte=end_date)
            
        page = self.paginate_queryset(timesheets)
        
        if page is not None:
            serializer = TimesheetSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TimesheetSerializer(timesheets, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Bảng chấm công của {employee.full_name}",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def leave_requests(self, request, pk=None):
        """
        Lấy danh sách yêu cầu nghỉ phép của nhân viên này.
        """
        employee = self.get_object()
        leave_requests = LeaveRequest.objects.filter(employee=employee)
        
        # Lọc theo trạng thái nếu có
        status_filter = request.query_params.get('status')
        if status_filter:
            leave_requests = leave_requests.filter(status=status_filter)
            
        page = self.paginate_queryset(leave_requests)
        
        if page is not None:
            serializer = LeaveRequestSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = LeaveRequestSerializer(leave_requests, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách yêu cầu nghỉ phép của {employee.full_name}",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def payrolls(self, request, pk=None):
        """
        Lấy bảng lương của nhân viên này.
        """
        employee = self.get_object()
        payrolls = Payroll.objects.filter(employee=employee)
        
        # Lọc theo khoảng thời gian nếu có
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if year:
            payrolls = payrolls.filter(year=year)
        if month:
            payrolls = payrolls.filter(month=month)
            
        page = self.paginate_queryset(payrolls)
        
        if page is not None:
            serializer = PayrollSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PayrollSerializer(payrolls, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Bảng lương của {employee.full_name}",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['HRM'])
class WorkScheduleViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý WorkSchedule resources.
    
    Cung cấp các operations CRUD cho lịch làm việc với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/work-schedules/ - Liệt kê tất cả lịch làm việc
    - POST /api/v1/hrm/work-schedules/ - Tạo lịch làm việc mới
    - GET /api/v1/hrm/work-schedules/{id}/ - Xem chi tiết lịch làm việc
    - PUT/PATCH /api/v1/hrm/work-schedules/{id}/ - Cập nhật lịch làm việc
    - DELETE /api/v1/hrm/work-schedules/{id}/ - Xóa lịch làm việc
    """
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'schedule_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_time', 'effective_date']
    ordering = ['name', 'start_time']
    
    select_related_fields = ['department']


@extend_schema(tags=['HRM'])
class HolidayViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Holiday resources.
    
    Cung cấp các operations CRUD cho ngày lễ với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/holidays/ - Liệt kê tất cả ngày lễ
    - POST /api/v1/hrm/holidays/ - Tạo ngày lễ mới
    - GET /api/v1/hrm/holidays/{id}/ - Xem chi tiết ngày lễ
    - PUT/PATCH /api/v1/hrm/holidays/{id}/ - Cập nhật ngày lễ
    - DELETE /api/v1/hrm/holidays/{id}/ - Xóa ngày lễ
    """
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['date', 'name']
    ordering = ['date']


@extend_schema(tags=['HRM'])
class TimesheetViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Timesheet resources.
    
    Cung cấp các operations CRUD cho bảng chấm công với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/timesheets/ - Liệt kê tất cả bảng chấm công
    - POST /api/v1/hrm/timesheets/ - Tạo bảng chấm công mới
    - GET /api/v1/hrm/timesheets/{id}/ - Xem chi tiết bảng chấm công
    - PUT/PATCH /api/v1/hrm/timesheets/{id}/ - Cập nhật bảng chấm công
    - DELETE /api/v1/hrm/timesheets/{id}/ - Xóa bảng chấm công
    """
    queryset = Timesheet.objects.all()
    serializer_class = TimesheetSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'date', 'status']
    ordering_fields = ['employee__last_name', 'date']
    ordering = ['-date', 'employee__last_name']
    
    select_related_fields = ['employee']


@extend_schema(tags=['HRM'])
class LeaveRequestViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý LeaveRequest resources.
    
    Cung cấp các operations CRUD cho yêu cầu nghỉ phép với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/leave-requests/ - Liệt kê tất cả yêu cầu nghỉ phép
    - POST /api/v1/hrm/leave-requests/ - Tạo yêu cầu nghỉ phép mới
    - GET /api/v1/hrm/leave-requests/{id}/ - Xem chi tiết yêu cầu nghỉ phép
    - PUT/PATCH /api/v1/hrm/leave-requests/{id}/ - Cập nhật yêu cầu nghỉ phép
    - DELETE /api/v1/hrm/leave-requests/{id}/ - Xóa yêu cầu nghỉ phép
    - POST /api/v1/hrm/leave-requests/{id}/approve/ - Phê duyệt yêu cầu nghỉ phép
    - POST /api/v1/hrm/leave-requests/{id}/reject/ - Từ chối yêu cầu nghỉ phép
    """
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'status', 'leave_type']
    ordering_fields = ['employee__last_name', 'start_date', 'status']
    ordering = ['-start_date']
    
    select_related_fields = ['employee', 'approved_by']
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """
        Phê duyệt yêu cầu nghỉ phép.
        """
        leave_request = self.get_object()
        
        if leave_request.status != LeaveRequest.STATUS_PENDING:
            return self.error_response(
                message="Chỉ có thể phê duyệt yêu cầu đang chờ xử lý",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        leave_request.status = LeaveRequest.STATUS_APPROVED
        leave_request.approved_by = request.user
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return self.success_response(
            data=serializer.data,
            message="Yêu cầu nghỉ phép đã được phê duyệt",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """
        Từ chối yêu cầu nghỉ phép.
        """
        leave_request = self.get_object()
        
        if leave_request.status != LeaveRequest.STATUS_PENDING:
            return self.error_response(
                message="Chỉ có thể từ chối yêu cầu đang chờ xử lý",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        leave_request.status = LeaveRequest.STATUS_REJECTED
        leave_request.approved_by = request.user
        leave_request.rejection_reason = request.data.get('rejection_reason', '')
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return self.success_response(
            data=serializer.data,
            message="Yêu cầu nghỉ phép đã bị từ chối",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['HRM'])
class SalaryViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Salary resources.
    
    Cung cấp các operations CRUD cho lương cơ bản với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/salaries/ - Liệt kê tất cả lương cơ bản
    - POST /api/v1/hrm/salaries/ - Tạo lương cơ bản mới
    - GET /api/v1/hrm/salaries/{id}/ - Xem chi tiết lương cơ bản
    - PUT/PATCH /api/v1/hrm/salaries/{id}/ - Cập nhật lương cơ bản
    - DELETE /api/v1/hrm/salaries/{id}/ - Xóa lương cơ bản
    """
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'is_active']
    ordering_fields = ['employee__last_name', 'effective_date', 'amount']
    ordering = ['-effective_date']
    
    select_related_fields = ['employee']


@extend_schema(tags=['HRM'])
class PayrollViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Payroll resources.
    
    Cung cấp các operations CRUD cho bảng lương với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/payrolls/ - Liệt kê tất cả bảng lương
    - POST /api/v1/hrm/payrolls/ - Tạo bảng lương mới
    - GET /api/v1/hrm/payrolls/{id}/ - Xem chi tiết bảng lương
    - PUT/PATCH /api/v1/hrm/payrolls/{id}/ - Cập nhật bảng lương
    - DELETE /api/v1/hrm/payrolls/{id}/ - Xóa bảng lương
    - GET /api/v1/hrm/payrolls/generate-monthly/ - Tạo bảng lương hàng tháng
    """
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'payroll_period', 'status']
    ordering_fields = ['employee__last_name', 'payroll_period', 'start_date']
    ordering = ['-payroll_period', 'employee__last_name']
    
    select_related_fields = ['employee']
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def generate_monthly(self, request):
        """
        Tạo bảng lương hàng tháng cho tất cả nhân viên.
        """
        year = request.data.get('year')
        month = request.data.get('month')
        
        if not year or not month:
            return self.error_response(
                message="Năm và tháng là bắt buộc",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return self.error_response(
                message="Năm và tháng phải là số nguyên",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Tạo payroll_period từ year và month
        payroll_period = f"{year}-{month:02d}"
        
        # Kiểm tra nếu đã tồn tại bảng lương cho tháng này
        existing_payrolls = Payroll.objects.filter(payroll_period=payroll_period).count()
        if existing_payrolls > 0:
            return self.error_response(
                message=f"Đã tồn tại bảng lương cho tháng {month}/{year}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Tạo start_date và end_date cho tháng
        from datetime import date, timedelta
        import calendar
        
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        
        # Tạo bảng lương cho tất cả nhân viên đang hoạt động
        employees = Employee.objects.filter(is_active=True)
        payrolls_created = 0
        
        for employee in employees:
            # Tìm mức lương hiện tại của nhân viên
            current_salary = Salary.objects.filter(
                employee=employee,
                is_active=True,
                effective_date__lte=start_date
            ).order_by('-effective_date').first()
            
            if not current_salary:
                continue
            
            # Tạo bảng lương mới
            Payroll.objects.create(
                employee=employee,
                payroll_period=payroll_period,
                start_date=start_date,
                end_date=end_date,
                salary=current_salary,
                gross_amount=current_salary.amount,
                net_amount=current_salary.amount,  # Sẽ được tính toán lại sau
                status=Payroll.STATUS_DRAFT
            )
            payrolls_created += 1
        
        return self.success_response(
            data={"payrolls_created": payrolls_created},
            message=f"Đã tạo {payrolls_created} bảng lương cho tháng {month}/{year}",
            status_code=status.HTTP_201_CREATED
        )
