# Promotions API

Tài liệu API cho module promotions.

## Coupon

ViewSet để quản lý Coupon resources.
    
    Cung cấp các operations CRUD cho mã giảm giá với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/promotions/coupons/ - Liệt kê tất cả mã giảm giá
    - POST /api/v1/promotions/coupons/ - Tạo mã giảm giá mới
    - GET /api/v1/promotions/coupons/{id}/ - Xem chi tiết mã giảm giá
    - PUT/PATCH /api/v1/promotions/coupons/{id}/ - Cập nhật mã giảm giá
    - DELETE /api/v1/promotions/coupons/{id}/ - Xóa mã giảm giá
    - POST /api/v1/promotions/coupons/apply/ - Áp dụng mã giảm giá

### List Coupons

**GET** `/api/v1/coupons`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Coupon Details

**GET** `/api/v1/coupons/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Coupon

**POST** `/api/v1/coupons`

**Request Body:**

```json
{
  "name": "New Coupon",
  "description": "This is a new Coupon"
}
```

### Update Coupon

**PUT** `/api/v1/coupons/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Coupon",
  "description": "This is an updated Coupon"
}
```

### Delete Coupon

**DELETE** `/api/v1/coupons/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## PromotionCampaign

ViewSet để quản lý PromotionCampaign resources.
    
    Cung cấp các operations CRUD cho chiến dịch khuyến mãi với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/promotions/campaigns/ - Liệt kê tất cả chiến dịch khuyến mãi
    - POST /api/v1/promotions/campaigns/ - Tạo chiến dịch khuyến mãi mới
    - GET /api/v1/promotions/campaigns/{id}/ - Xem chi tiết chiến dịch khuyến mãi
    - PUT/PATCH /api/v1/promotions/campaigns/{id}/ - Cập nhật chiến dịch khuyến mãi
    - DELETE /api/v1/promotions/campaigns/{id}/ - Xóa chiến dịch khuyến mãi
    - GET /api/v1/promotions/campaigns/active/ - Lấy các chiến dịch đang hoạt động

### List PromotionCampaigns

**GET** `/api/v1/promotioncampaigns`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get PromotionCampaign Details

**GET** `/api/v1/promotioncampaigns/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create PromotionCampaign

**POST** `/api/v1/promotioncampaigns`

**Request Body:**

```json
{
  "name": "New PromotionCampaign",
  "description": "This is a new PromotionCampaign"
}
```

### Update PromotionCampaign

**PUT** `/api/v1/promotioncampaigns/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated PromotionCampaign",
  "description": "This is an updated PromotionCampaign"
}
```

### Delete PromotionCampaign

**DELETE** `/api/v1/promotioncampaigns/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## UsageLog

ViewSet để quản lý UsageLog resources.
    
    Cung cấp các operations CRUD cho lịch sử sử dụng khuyến mãi với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/promotions/usage-logs/ - Liệt kê tất cả lịch sử sử dụng
    - GET /api/v1/promotions/usage-logs/{id}/ - Xem chi tiết lịch sử sử dụng

### List UsageLogs

**GET** `/api/v1/usagelogs`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get UsageLog Details

**GET** `/api/v1/usagelogs/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create UsageLog

**POST** `/api/v1/usagelogs`

**Request Body:**

```json
{
  "name": "New UsageLog",
  "description": "This is a new UsageLog"
}
```

### Update UsageLog

**PUT** `/api/v1/usagelogs/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated UsageLog",
  "description": "This is an updated UsageLog"
}
```

### Delete UsageLog

**DELETE** `/api/v1/usagelogs/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Voucher

ViewSet để quản lý Voucher resources.
    
    Cung cấp các operations CRUD cho phiếu giảm giá với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/promotions/vouchers/ - Liệt kê tất cả phiếu giảm giá
    - POST /api/v1/promotions/vouchers/ - Tạo phiếu giảm giá mới
    - GET /api/v1/promotions/vouchers/{id}/ - Xem chi tiết phiếu giảm giá
    - PUT/PATCH /api/v1/promotions/vouchers/{id}/ - Cập nhật phiếu giảm giá
    - DELETE /api/v1/promotions/vouchers/{id}/ - Xóa phiếu giảm giá
    - POST /api/v1/promotions/vouchers/apply/ - Áp dụng phiếu giảm giá
    - GET /api/v1/promotions/vouchers/my-vouchers/ - Lấy phiếu giảm giá của người dùng hiện tại

### List Vouchers

**GET** `/api/v1/vouchers`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Voucher Details

**GET** `/api/v1/vouchers/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Voucher

**POST** `/api/v1/vouchers`

**Request Body:**

```json
{
  "name": "New Voucher",
  "description": "This is a new Voucher"
}
```

### Update Voucher

**PUT** `/api/v1/vouchers/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Voucher",
  "description": "This is an updated Voucher"
}
```

### Delete Voucher

**DELETE** `/api/v1/vouchers/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


