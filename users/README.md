# Users App - Complete User Management System

## Tổng quan

Users app đã được khôi phục đầy đủ các tính năng quản lý user cho hệ thống e-commerce. App này bao gồm:

- **User Management**: Quản lý users (admin)
- **Self Management**: User tự quản lý profile
- **Role Management**: Quản lý roles (seller, customer, staff)
- **Analytics**: Thống kê user metrics
- **Security**: Avatar upload, change password, activity tracking

## Architecture

### Models
- `User`: Extended AbstractUser với role management và profile fields
- Hỗ trợ multi-role: seller, customer, staff
- Profile fields: phone, address, date_of_birth, avatar
- Tracking: last_login_ip, created_at, updated_at

### ViewSets Structure

#### 1. UserAdminViewSet (`/api/v1/users/admin/`)
**Quản lý users cho admin**

```python
# CRUD Operations
GET    /api/v1/users/admin/                 # List tất cả users
POST   /api/v1/users/admin/                 # Tạo user mới  
GET    /api/v1/users/admin/{id}/            # Chi tiết user
PUT    /api/v1/users/admin/{id}/            # Cập nhật user
PATCH  /api/v1/users/admin/{id}/            # Partial update
DELETE /api/v1/users/admin/{id}/            # Deactivate user

# Special Actions  
GET    /api/v1/users/admin/analytics/       # User analytics overview
POST   /api/v1/users/admin/{id}/activate/   # Activate user
POST   /api/v1/users/admin/{id}/deactivate/ # Deactivate user
```

**Features:**
- Filtering: `is_seller`, `is_customer`, `is_staff`, `is_active`, `is_verified`
- Search: `username`, `email`, `first_name`, `last_name`, `phone_number`
- Ordering: `date_joined`, `last_login`, `username`, `email`
- Query parameter `?role=sellers/customers/staff` để filter theo role

#### 2. UserSelfViewSet (`/api/v1/users/profile/`)
**User tự quản lý profile**

```python
# Profile Management
GET    /api/v1/users/profile/               # Get profile hiện tại
PUT    /api/v1/users/profile/               # Update profile  
PATCH  /api/v1/users/profile/               # Partial update

# Special Actions
POST   /api/v1/users/profile/upload-avatar/     # Upload avatar
POST   /api/v1/users/profile/change-password/   # Đổi mật khẩu
GET    /api/v1/users/profile/activity/          # Lịch sử hoạt động
```

**Features:**
- Chỉ user có thể edit profile của mình
- Avatar upload với validation
- Change password với current password verification
- Activity tracking

#### 3. UserRoleViewSet (`/api/v1/users/roles/`)
**Quản lý roles (admin only)**

```python
# Role Management
GET    /api/v1/users/roles/{user_id}/       # Get roles của user
PUT    /api/v1/users/roles/{user_id}/       # Update roles
PATCH  /api/v1/users/roles/{user_id}/       # Partial update roles

# Role Listing
GET    /api/v1/users/roles/sellers/         # List sellers
GET    /api/v1/users/roles/customers/       # List customers  
GET    /api/v1/users/roles/staff/           # List staff
```

**Features:**
- Chỉ admin có thể manage roles
- Validation: user phải có ít nhất 1 role
- Bulk role assignment

### Legacy Endpoints (Backward Compatibility)

```python
# Giữ lại để backward compatibility
GET    /api/v1/users/me/                    # Get user info (legacy)
PATCH  /api/v1/users/me/update/             # Update profile (legacy)
```

## User Analytics 

### Analytics Overview (`GET /api/v1/users/admin/analytics/`)

```json
{
  "success": true,
  "data": {
    "total_users": 1250,
    "active_users": 1180,
    "verified_users": 1100,
    "seller_users": 45,
    "customer_users": 1200,
    "recent_registrations": 125,    // Last 30 days
    "recently_active": 890,         // Last 7 days
    "verification_rate": 88.0,      // %
    "activity_rate": 71.2,          // %
    "registration_trend": [         // Last 12 months
      {"month": "2024-01", "count": 45},
      {"month": "2024-02", "count": 67},
      // ...
    ]
  }
}
```

## Permissions

### Admin Endpoints
- `UserAdminViewSet`: `IsAdminUser`
- `UserRoleViewSet`: `IsAdminUser`

### User Endpoints  
- `UserSelfViewSet`: `IsAuthenticated`
- Legacy views: `IsAuthenticated`

## Serializers

### UserSerializer
Thông tin cơ bản của user (list view)

### UserDetailSerializer  
Chi tiết đầy đủ (admin CRUD)

### UserProfileSerializer
Profile management (self management)

### UserRoleUpdateSerializer
Role management (admin only)

### UserAnalyticsSerializer
Analytics data structure

## Security Features

### Avatar Upload
- Validation file type và size
- Automatic image processing
- Secure file storage

### Password Management
- Current password verification
- Django password validation
- Secure password hashing

### Activity Tracking
- Last login IP tracking
- Login history (extensible)
- Profile update tracking (extensible)

## Usage Examples

### Admin tạo user mới
```bash
POST /api/v1/users/admin/
{
  "username": "newuser",
  "email": "user@example.com", 
  "first_name": "John",
  "last_name": "Doe",
  "is_seller": true,
  "is_customer": true
}
```

### User update profile
```bash
PATCH /api/v1/users/profile/
{
  "first_name": "Jane",
  "phone_number": "+84123456789",
  "address": "123 Main St, HCMC"
}
```

### Admin assign seller role
```bash
PATCH /api/v1/users/roles/123/
{
  "is_seller": true,
  "is_customer": true,
  "is_staff": false
}
```

### Upload avatar
```bash
POST /api/v1/users/profile/upload-avatar/
Content-Type: multipart/form-data

avatar: [file]
```

### Change password
```bash
POST /api/v1/users/profile/change-password/
{
  "current_password": "old_password",
  "new_password": "new_secure_password"
}
```

## Frontend Integration

### Admin Dashboard
- User management table với filtering/search
- User analytics dashboard
- Role management interface
- Bulk operations

### User Profile
- Profile edit form
- Avatar upload component  
- Password change form
- Activity history

### Seller Dashboard
- Seller-specific features
- Product management access
- Sales analytics

## Extensibility

### Planned Features
- User activity logging system
- Advanced analytics với charts
- User settings management
- Social login integration
- Two-factor authentication
- User groups và permissions
- Audit logs
- User preferences

### Integration Points
- Customer app: Customer profile extended từ User
- Orders app: Order tracking theo user
- Products app: Seller product management
- Reviews app: User reviews và ratings
- Notifications app: User notifications preferences

## Migration Notes

Để migrate từ legacy system:

1. **Legacy endpoints vẫn hoạt động** - không breaking changes
2. **Frontend có thể dần migrate** sang endpoints mới  
3. **Admin dashboard** nên sử dụng ViewSets mới ngay
4. **Mobile apps** có thể sử dụng profile endpoints mới

## Testing

```bash
# Run user tests
python manage.py test users

# Test specific ViewSet
python manage.py test users.tests.test_viewsets

# Test permissions
python manage.py test users.tests.test_permissions
```

## API Documentation

- **Swagger UI**: `/api/swagger/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`

Tất cả endpoints đều có đầy đủ Swagger documentation với examples và schema.

---

## Vấn đề đã được giải quyết

✅ **User Management APIs đã được khôi phục hoàn toàn**
✅ **Admin có thể quản lý users qua REST API**  
✅ **Users có thể self-manage profiles**
✅ **Role management system hoạt động**
✅ **Analytics và reporting có sẵn**
✅ **Security features đầy đủ**
✅ **Backward compatibility được đảm bảo**
✅ **Extensible architecture cho future features**

Bây giờ Users app đã có đầy đủ chức năng của một hệ thống e-commerce portal professional!
