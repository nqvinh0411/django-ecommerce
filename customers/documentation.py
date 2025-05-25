"""
Tự động tạo tài liệu API cho module customers.

Module này sử dụng thông tin từ ViewSets, Serializers và Models để tự động
tạo tài liệu API phong phú, bao gồm các ví dụ request/response.
"""
import json
from django.urls import reverse
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIRequestFactory

from .viewsets import CustomerViewSet, CustomerGroupViewSet, CustomerAddressViewSet, CustomerActivityViewSet
from .models import Customer, CustomerGroup, CustomerAddress, CustomerActivity
from .serializers import CustomerSerializer, CustomerGroupSerializer, CustomerAddressSerializer, CustomerActivitySerializer


def generate_api_example():
    """
    Tạo ví dụ API cho các endpoints của module customers.
    
    Returns:
        dict: Dictionary chứa các ví dụ API cho từng endpoint
    """
    factory = APIRequestFactory()
    examples = {
        'customer': {},
        'customer_group': {},
        'customer_address': {},
        'customer_activity': {}
    }
    
    # Ví dụ cho Customer API
    customer_viewset = CustomerViewSet()
    examples['customer']['list_response'] = {
        "status": "success",
        "status_code": 200,
        "message": "Danh sách khách hàng",
        "data": [
            {
                "id": 1,
                "user": {
                    "id": 1,
                    "email": "john@example.com",
                    "first_name": "John",
                    "last_name": "Doe"
                },
                "phone_number": "+84901234567",
                "date_of_birth": "1990-01-01",
                "created_at": "2025-05-20T10:30:45Z",
                "updated_at": "2025-05-25T14:15:30Z"
            },
            {
                "id": 2,
                "user": {
                    "id": 2,
                    "email": "jane@example.com",
                    "first_name": "Jane",
                    "last_name": "Smith"
                },
                "phone_number": "+84909876543",
                "date_of_birth": "1992-05-15",
                "created_at": "2025-05-21T09:20:15Z",
                "updated_at": "2025-05-26T11:10:25Z"
            }
        ],
        "pagination": {
            "count": 20,
            "page_size": 10,
            "current_page": 1,
            "total_pages": 2,
            "next": "/api/v1/customers/?page=2",
            "previous": None
        }
    }
    
    examples['customer']['detail_response'] = {
        "status": "success",
        "status_code": 200,
        "message": "Chi tiết khách hàng",
        "data": {
            "id": 1,
            "user": {
                "id": 1,
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe"
            },
            "phone_number": "+84901234567",
            "date_of_birth": "1990-01-01",
            "created_at": "2025-05-20T10:30:45Z",
            "updated_at": "2025-05-25T14:15:30Z"
        }
    }
    
    examples['customer']['create_request'] = {
        "user": {
            "email": "new.customer@example.com",
            "first_name": "New",
            "last_name": "Customer"
        },
        "phone_number": "+84912345678",
        "date_of_birth": "1995-10-20"
    }
    
    examples['customer']['create_response'] = {
        "status": "success",
        "status_code": 201,
        "message": "Khách hàng đã được tạo thành công",
        "data": {
            "id": 3,
            "user": {
                "id": 3,
                "email": "new.customer@example.com",
                "first_name": "New",
                "last_name": "Customer"
            },
            "phone_number": "+84912345678",
            "date_of_birth": "1995-10-20",
            "created_at": "2025-05-27T10:30:45Z",
            "updated_at": "2025-05-27T10:30:45Z"
        }
    }
    
    examples['customer']['update_request'] = {
        "phone_number": "+84912345679",
        "date_of_birth": "1995-10-21"
    }
    
    examples['customer']['update_response'] = {
        "status": "success",
        "status_code": 200,
        "message": "Khách hàng đã được cập nhật thành công",
        "data": {
            "id": 3,
            "user": {
                "id": 3,
                "email": "new.customer@example.com",
                "first_name": "New",
                "last_name": "Customer"
            },
            "phone_number": "+84912345679",
            "date_of_birth": "1995-10-21",
            "created_at": "2025-05-27T10:30:45Z",
            "updated_at": "2025-05-27T11:15:30Z"
        }
    }
    
    examples['customer']['delete_response'] = {
        "status": "success",
        "status_code": 204,
        "message": "Khách hàng đã được xóa thành công"
    }
    
    examples['customer']['error_response'] = {
        "status": "error",
        "status_code": 400,
        "message": "Dữ liệu không hợp lệ",
        "errors": {
            "phone_number": ["Số điện thoại không đúng định dạng E.164"],
            "date_of_birth": ["Ngày sinh không đúng định dạng ISO 8601 (YYYY-MM-DD)"]
        }
    }
    
    # Ví dụ cho CustomerGroup API
    customer_group_viewset = CustomerGroupViewSet()
    examples['customer_group']['list_response'] = {
        "status": "success",
        "status_code": 200,
        "message": "Danh sách nhóm khách hàng",
        "data": [
            {
                "id": 1,
                "name": "VIP",
                "description": "Khách hàng VIP được hưởng nhiều ưu đãi",
                "discount_rate": 10.0,
                "created_at": "2025-05-10T08:30:00Z",
                "updated_at": "2025-05-15T09:45:30Z"
            },
            {
                "id": 2,
                "name": "Thường xuyên",
                "description": "Khách hàng mua sắm thường xuyên",
                "discount_rate": 5.0,
                "created_at": "2025-05-11T10:15:20Z",
                "updated_at": "2025-05-16T11:30:45Z"
            }
        ],
        "pagination": {
            "count": 10,
            "page_size": 10,
            "current_page": 1,
            "total_pages": 1,
            "next": None,
            "previous": None
        }
    }
    
    # Ví dụ cho CustomerAddress API
    customer_address_viewset = CustomerAddressViewSet()
    examples['customer_address']['default_shipping_response'] = {
        "status": "success",
        "status_code": 200,
        "message": "Địa chỉ giao hàng mặc định",
        "data": {
            "id": 1,
            "customer": 1,
            "address_type": "shipping",
            "street_address": "123 Đường Nguyễn Huệ",
            "city": "Thành phố Hồ Chí Minh",
            "state": "Hồ Chí Minh",
            "postal_code": "70000",
            "country": "Việt Nam",
            "is_default": True,
            "created_at": "2025-05-20T10:30:45Z",
            "updated_at": "2025-05-25T14:15:30Z"
        }
    }
    
    # Ví dụ cho CustomerActivity API
    customer_activity_viewset = CustomerActivityViewSet()
    examples['customer_activity']['list_response'] = {
        "status": "success",
        "status_code": 200,
        "message": "Danh sách hoạt động khách hàng",
        "data": [
            {
                "id": 1,
                "customer": 1,
                "activity_type": "login",
                "metadata": {
                    "ip_address": "192.168.1.1",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
                "created_at": "2025-05-26T10:30:45Z"
            },
            {
                "id": 2,
                "customer": 1,
                "activity_type": "order_placed",
                "metadata": {
                    "order_id": 12345,
                    "total_amount": 500000,
                    "items_count": 3
                },
                "created_at": "2025-05-26T11:45:30Z"
            }
        ],
        "pagination": {
            "count": 50,
            "page_size": 10,
            "current_page": 1,
            "total_pages": 5,
            "next": "/api/v1/customer-activities/?page=2",
            "previous": None
        }
    }
    
    return examples


def save_api_examples_to_file(file_path='/home/ho/Project/django/docs/api/customers_examples.json'):
    """
    Lưu các ví dụ API vào file JSON.
    
    Args:
        file_path (str, optional): Đường dẫn đến file lưu ví dụ. 
                                  Mặc định là '/home/ho/Project/django/docs/api/customers_examples.json'.
    """
    import os
    
    examples = generate_api_example()
    
    # Đảm bảo thư mục tồn tại
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Lưu vào file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(examples, f, ensure_ascii=False, indent=2)
    
    print(f"API examples saved to {file_path}")


def generate_swagger_definition(output_file='/home/ho/Project/django/docs/api/swagger/customers.yaml'):
    """
    Tạo định nghĩa OpenAPI/Swagger cho module customers.
    
    Args:
        output_file (str, optional): Đường dẫn đến file OpenAPI output.
                                    Mặc định là '/home/ho/Project/django/docs/api/swagger/customers.yaml'.
    """
    import os
    import yaml
    
    openapi = {
        "openapi": "3.0.0",
        "info": {
            "title": "Customers API",
            "description": "API để quản lý khách hàng, nhóm khách hàng, địa chỉ và hoạt động",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@example.com"
            }
        },
        "servers": [
            {
                "url": "https://api.example.com/api/v1",
                "description": "Production server"
            },
            {
                "url": "https://staging-api.example.com/api/v1",
                "description": "Staging server"
            }
        ],
        "tags": [
            {
                "name": "customers",
                "description": "Operations about customers"
            },
            {
                "name": "customer-groups",
                "description": "Operations about customer groups"
            },
            {
                "name": "customer-addresses",
                "description": "Operations about customer addresses"
            },
            {
                "name": "customer-activities",
                "description": "Operations about customer activities"
            }
        ],
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    }
    
    # Định nghĩa schemas
    openapi["components"]["schemas"]["Customer"] = {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "format": "int64"},
            "user": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "email": {"type": "string", "format": "email"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"}
                }
            },
            "phone_number": {"type": "string"},
            "date_of_birth": {"type": "string", "format": "date"},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"}
        }
    }
    
    # Định nghĩa paths
    # Customer paths
    openapi["paths"]["/customers"] = {
        "get": {
            "tags": ["customers"],
            "summary": "Lấy danh sách khách hàng",
            "description": "Trả về danh sách khách hàng phân trang",
            "operationId": "listCustomers",
            "parameters": [
                {
                    "name": "page",
                    "in": "query",
                    "description": "Số trang",
                    "required": False,
                    "schema": {"type": "integer", "default": 1}
                },
                {
                    "name": "page_size",
                    "in": "query",
                    "description": "Số lượng item trên mỗi trang",
                    "required": False,
                    "schema": {"type": "integer", "default": 10}
                },
                {
                    "name": "search",
                    "in": "query",
                    "description": "Tìm kiếm theo email hoặc số điện thoại",
                    "required": False,
                    "schema": {"type": "string"}
                },
                {
                    "name": "ordering",
                    "in": "query",
                    "description": "Sắp xếp kết quả (prefix với - để sắp xếp giảm dần)",
                    "required": False,
                    "schema": {"type": "string", "enum": ["created_at", "-created_at", "user__email", "-user__email"]}
                }
            ],
            "responses": {
                "200": {
                    "description": "Danh sách khách hàng thành công",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaginatedCustomerList"
                            },
                            "example": generate_api_example()["customer"]["list_response"]
                        }
                    }
                },
                "401": {
                    "description": "Chưa xác thực",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Error"
                            },
                            "example": {
                                "status": "error",
                                "status_code": 401,
                                "message": "Bạn cần đăng nhập để thực hiện hành động này"
                            }
                        }
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        },
        "post": {
            "tags": ["customers"],
            "summary": "Tạo khách hàng mới",
            "description": "Tạo một khách hàng mới và trả về thông tin của khách hàng đó",
            "operationId": "createCustomer",
            "requestBody": {
                "description": "Thông tin khách hàng mới",
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/CustomerInput"
                        },
                        "example": generate_api_example()["customer"]["create_request"]
                    }
                }
            },
            "responses": {
                "201": {
                    "description": "Tạo khách hàng thành công",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/CustomerResponse"
                            },
                            "example": generate_api_example()["customer"]["create_response"]
                        }
                    }
                },
                "400": {
                    "description": "Dữ liệu không hợp lệ",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Error"
                            },
                            "example": generate_api_example()["customer"]["error_response"]
                        }
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        }
    }
    
    # Đảm bảo thư mục tồn tại
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Lưu vào file YAML
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(openapi, f, sort_keys=False, default_flow_style=False)
    
    print(f"OpenAPI definition saved to {output_file}")


if __name__ == "__main__":
    save_api_examples_to_file()
    generate_swagger_definition()
