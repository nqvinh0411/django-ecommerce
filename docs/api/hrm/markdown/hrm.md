# Hrm API

Tài liệu API cho module hrm.

## Department

ViewSet để quản lý Department resources.
    
    Cung cấp các operations CRUD cho phòng ban với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/departments/ - Liệt kê tất cả phòng ban
    - POST /api/v1/hrm/departments/ - Tạo phòng ban mới
    - GET /api/v1/hrm/departments/{id}/ - Xem chi tiết phòng ban
    - PUT/PATCH /api/v1/hrm/departments/{id}/ - Cập nhật phòng ban
    - DELETE /api/v1/hrm/departments/{id}/ - Xóa phòng ban

### List Departments

**GET** `/api/v1/departments`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Department Details

**GET** `/api/v1/departments/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Department

**POST** `/api/v1/departments`

**Request Body:**

```json
{
  "name": "New Department",
  "description": "This is a new Department"
}
```

### Update Department

**PUT** `/api/v1/departments/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Department",
  "description": "This is an updated Department"
}
```

### Delete Department

**DELETE** `/api/v1/departments/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Employee

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

### List Employees

**GET** `/api/v1/employees`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Employee Details

**GET** `/api/v1/employees/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Employee

**POST** `/api/v1/employees`

**Request Body:**

```json
{
  "name": "New Employee",
  "description": "This is a new Employee"
}
```

### Update Employee

**PUT** `/api/v1/employees/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Employee",
  "description": "This is an updated Employee"
}
```

### Delete Employee

**DELETE** `/api/v1/employees/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Holiday

ViewSet để quản lý Holiday resources.
    
    Cung cấp các operations CRUD cho ngày lễ với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/holidays/ - Liệt kê tất cả ngày lễ
    - POST /api/v1/hrm/holidays/ - Tạo ngày lễ mới
    - GET /api/v1/hrm/holidays/{id}/ - Xem chi tiết ngày lễ
    - PUT/PATCH /api/v1/hrm/holidays/{id}/ - Cập nhật ngày lễ
    - DELETE /api/v1/hrm/holidays/{id}/ - Xóa ngày lễ

### List Holidays

**GET** `/api/v1/holidays`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Holiday Details

**GET** `/api/v1/holidays/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Holiday

**POST** `/api/v1/holidays`

**Request Body:**

```json
{
  "name": "New Holiday",
  "description": "This is a new Holiday"
}
```

### Update Holiday

**PUT** `/api/v1/holidays/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Holiday",
  "description": "This is an updated Holiday"
}
```

### Delete Holiday

**DELETE** `/api/v1/holidays/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## LeaveRequest

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

### List LeaveRequests

**GET** `/api/v1/leaverequests`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get LeaveRequest Details

**GET** `/api/v1/leaverequests/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create LeaveRequest

**POST** `/api/v1/leaverequests`

**Request Body:**

```json
{
  "name": "New LeaveRequest",
  "description": "This is a new LeaveRequest"
}
```

### Update LeaveRequest

**PUT** `/api/v1/leaverequests/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated LeaveRequest",
  "description": "This is an updated LeaveRequest"
}
```

### Delete LeaveRequest

**DELETE** `/api/v1/leaverequests/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Payroll

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

### List Payrolls

**GET** `/api/v1/payrolls`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Payroll Details

**GET** `/api/v1/payrolls/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Payroll

**POST** `/api/v1/payrolls`

**Request Body:**

```json
{
  "name": "New Payroll",
  "description": "This is a new Payroll"
}
```

### Update Payroll

**PUT** `/api/v1/payrolls/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Payroll",
  "description": "This is an updated Payroll"
}
```

### Delete Payroll

**DELETE** `/api/v1/payrolls/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Position

ViewSet để quản lý Position resources.
    
    Cung cấp các operations CRUD cho chức vụ với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/positions/ - Liệt kê tất cả chức vụ
    - POST /api/v1/hrm/positions/ - Tạo chức vụ mới
    - GET /api/v1/hrm/positions/{id}/ - Xem chi tiết chức vụ
    - PUT/PATCH /api/v1/hrm/positions/{id}/ - Cập nhật chức vụ
    - DELETE /api/v1/hrm/positions/{id}/ - Xóa chức vụ

### List Positions

**GET** `/api/v1/positions`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Position Details

**GET** `/api/v1/positions/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Position

**POST** `/api/v1/positions`

**Request Body:**

```json
{
  "name": "New Position",
  "description": "This is a new Position"
}
```

### Update Position

**PUT** `/api/v1/positions/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Position",
  "description": "This is an updated Position"
}
```

### Delete Position

**DELETE** `/api/v1/positions/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Salary

ViewSet để quản lý Salary resources.
    
    Cung cấp các operations CRUD cho lương cơ bản với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/salaries/ - Liệt kê tất cả lương cơ bản
    - POST /api/v1/hrm/salaries/ - Tạo lương cơ bản mới
    - GET /api/v1/hrm/salaries/{id}/ - Xem chi tiết lương cơ bản
    - PUT/PATCH /api/v1/hrm/salaries/{id}/ - Cập nhật lương cơ bản
    - DELETE /api/v1/hrm/salaries/{id}/ - Xóa lương cơ bản

### List Salarys

**GET** `/api/v1/salarys`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Salary Details

**GET** `/api/v1/salarys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Salary

**POST** `/api/v1/salarys`

**Request Body:**

```json
{
  "name": "New Salary",
  "description": "This is a new Salary"
}
```

### Update Salary

**PUT** `/api/v1/salarys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Salary",
  "description": "This is an updated Salary"
}
```

### Delete Salary

**DELETE** `/api/v1/salarys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Timesheet

ViewSet để quản lý Timesheet resources.
    
    Cung cấp các operations CRUD cho bảng chấm công với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/timesheets/ - Liệt kê tất cả bảng chấm công
    - POST /api/v1/hrm/timesheets/ - Tạo bảng chấm công mới
    - GET /api/v1/hrm/timesheets/{id}/ - Xem chi tiết bảng chấm công
    - PUT/PATCH /api/v1/hrm/timesheets/{id}/ - Cập nhật bảng chấm công
    - DELETE /api/v1/hrm/timesheets/{id}/ - Xóa bảng chấm công

### List Timesheets

**GET** `/api/v1/timesheets`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Timesheet Details

**GET** `/api/v1/timesheets/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Timesheet

**POST** `/api/v1/timesheets`

**Request Body:**

```json
{
  "name": "New Timesheet",
  "description": "This is a new Timesheet"
}
```

### Update Timesheet

**PUT** `/api/v1/timesheets/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Timesheet",
  "description": "This is an updated Timesheet"
}
```

### Delete Timesheet

**DELETE** `/api/v1/timesheets/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## WorkSchedule

ViewSet để quản lý WorkSchedule resources.
    
    Cung cấp các operations CRUD cho lịch làm việc với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/hrm/work-schedules/ - Liệt kê tất cả lịch làm việc
    - POST /api/v1/hrm/work-schedules/ - Tạo lịch làm việc mới
    - GET /api/v1/hrm/work-schedules/{id}/ - Xem chi tiết lịch làm việc
    - PUT/PATCH /api/v1/hrm/work-schedules/{id}/ - Cập nhật lịch làm việc
    - DELETE /api/v1/hrm/work-schedules/{id}/ - Xóa lịch làm việc

### List WorkSchedules

**GET** `/api/v1/workschedules`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get WorkSchedule Details

**GET** `/api/v1/workschedules/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create WorkSchedule

**POST** `/api/v1/workschedules`

**Request Body:**

```json
{
  "name": "New WorkSchedule",
  "description": "This is a new WorkSchedule"
}
```

### Update WorkSchedule

**PUT** `/api/v1/workschedules/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated WorkSchedule",
  "description": "This is an updated WorkSchedule"
}
```

### Delete WorkSchedule

**DELETE** `/api/v1/workschedules/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


