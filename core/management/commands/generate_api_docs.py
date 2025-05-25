"""
Management command để tự động sinh tài liệu API.

Command này sẽ quét tất cả các ViewSets trong hệ thống và tạo tài liệu API
theo chuẩn OpenAPI, kèm theo các ví dụ request/response.
"""
import os
import json
import yaml
import importlib
import inspect
from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps
from rest_framework.viewsets import ViewSet

from core.viewsets.base import StandardizedModelViewSet, ReadOnlyStandardizedModelViewSet


class Command(BaseCommand):
    help = 'Tự động sinh tài liệu API cho tất cả modules trong hệ thống'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='all',
            help='Định dạng tài liệu (openapi, examples, markdown, all)'
        )
        parser.add_argument(
            '--module',
            type=str,
            default='all',
            help='Module cụ thể để sinh tài liệu (all để sinh cho tất cả)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default=os.path.join(str(settings.BASE_DIR), 'docs', 'api'),
            help='Thư mục đầu ra cho tài liệu'
        )

    def handle(self, *args, **options):
        format_option = options['format']
        module_option = options['module']
        output_dir = options['output_dir']
        
        # Đảm bảo thư mục đầu ra tồn tại
        os.makedirs(output_dir, exist_ok=True)
        
        # Danh sách modules để sinh tài liệu
        modules = []
        if module_option == 'all':
            # Lấy tất cả app từ INSTALLED_APPS
            for app_config in apps.get_app_configs():
                # Chỉ lấy các app trong project, không phải third-party
                if str(app_config.path).startswith(str(settings.BASE_DIR)):
                    modules.append(app_config.name)
        else:
            modules = [module_option]
        
        self.stdout.write(self.style.SUCCESS(f"Bắt đầu sinh tài liệu API cho modules: {', '.join(modules)}"))
        
        # Sinh tài liệu cho từng module
        for module_name in modules:
            try:
                self._generate_docs_for_module(module_name, format_option, output_dir)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Lỗi khi sinh tài liệu cho module {module_name}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS("Đã hoàn thành sinh tài liệu API!"))
    
    def _generate_docs_for_module(self, module_name, format_option, output_dir):
        """Sinh tài liệu cho một module cụ thể."""
        self.stdout.write(f"Đang sinh tài liệu cho module {module_name}...")
        
        # Kiểm tra xem module có tồn tại viewsets.py không
        try:
            viewsets_module = importlib.import_module(f"{module_name}.viewsets")
        except ImportError:
            self.stdout.write(f"Module {module_name} không có file viewsets.py, bỏ qua.")
            return
        
        # Lấy tất cả các ViewSet classes trong module
        viewsets = []
        for name, obj in inspect.getmembers(viewsets_module):
            if (inspect.isclass(obj) and issubclass(obj, ViewSet) and 
                obj not in [StandardizedModelViewSet, ReadOnlyStandardizedModelViewSet] and
                obj.__module__ == viewsets_module.__name__):
                viewsets.append(obj)
        
        if not viewsets:
            self.stdout.write(f"Không tìm thấy ViewSet nào trong module {module_name}, bỏ qua.")
            return
        
        self.stdout.write(f"Tìm thấy {len(viewsets)} ViewSets trong module {module_name}")
        
        # Tạo thư mục đầu ra cho module
        module_output_dir = os.path.join(output_dir, module_name.split('.')[-1])
        os.makedirs(module_output_dir, exist_ok=True)
        
        # Sinh tài liệu theo định dạng yêu cầu
        if format_option in ['openapi', 'all']:
            self._generate_openapi(viewsets, module_name, module_output_dir)
        
        if format_option in ['examples', 'all']:
            self._generate_examples(viewsets, module_name, module_output_dir)
        
        if format_option in ['markdown', 'all']:
            self._generate_markdown(viewsets, module_name, module_output_dir)
    
    def _generate_openapi(self, viewsets, module_name, output_dir):
        """Sinh tài liệu OpenAPI cho các ViewSets."""
        openapi_dir = os.path.join(output_dir, 'openapi')
        os.makedirs(openapi_dir, exist_ok=True)
        
        # Tạo template OpenAPI cơ bản
        openapi = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{module_name.split('.')[-1].title()} API",
                "description": f"API cho module {module_name}",
                "version": "1.0.0",
                "contact": {
                    "name": "API Support",
                    "email": "api@example.com"
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
            "tags": [],
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
        
        # Thêm tag cho module
        module_tag = {
            "name": module_name.split('.')[-1],
            "description": f"Operations related to {module_name.split('.')[-1]}"
        }
        openapi["tags"].append(module_tag)
        
        # Thêm thông tin chi tiết cho từng ViewSet
        for viewset in viewsets:
            self._add_viewset_to_openapi(viewset, openapi)
        
        # Lưu file OpenAPI
        output_file = os.path.join(openapi_dir, f"{module_name.split('.')[-1]}.yaml")
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(openapi, f, sort_keys=False, default_flow_style=False)
        
        self.stdout.write(self.style.SUCCESS(f"Đã sinh tài liệu OpenAPI cho module {module_name} tại {output_file}"))
    
    def _add_viewset_to_openapi(self, viewset, openapi):
        """Thêm thông tin chi tiết của một ViewSet vào tài liệu OpenAPI."""
        # Lấy tên resource từ ViewSet
        viewset_name = viewset.__name__
        resource_name = viewset_name.replace('ViewSet', '').lower()
        
        # Thêm paths cho từng action của ViewSet
        if hasattr(viewset, 'get_queryset') or hasattr(viewset, 'queryset'):
            # List action
            path = f"/{resource_name}s"
            if path not in openapi["paths"]:
                openapi["paths"][path] = {}
            
            # GET - list
            openapi["paths"][path]["get"] = {
                "tags": [resource_name + "s"],
                "summary": f"List all {resource_name}s",
                "description": f"Returns a list of {resource_name}s",
                "operationId": f"list{resource_name.title()}s",
                "parameters": [
                    {
                        "name": "page",
                        "in": "query",
                        "description": "Page number",
                        "required": False,
                        "schema": {"type": "integer", "default": 1}
                    },
                    {
                        "name": "page_size",
                        "in": "query",
                        "description": "Number of items per page",
                        "required": False,
                        "schema": {"type": "integer", "default": 10}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "success"},
                                        "status_code": {"type": "integer", "example": 200},
                                        "message": {"type": "string", "example": f"List of {resource_name}s"},
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "type": "object"
                                            }
                                        },
                                        "pagination": {
                                            "type": "object",
                                            "properties": {
                                                "count": {"type": "integer"},
                                                "page_size": {"type": "integer"},
                                                "current_page": {"type": "integer"},
                                                "total_pages": {"type": "integer"},
                                                "next": {"type": "string", "nullable": True},
                                                "previous": {"type": "string", "nullable": True}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "error"},
                                        "status_code": {"type": "integer", "example": 401},
                                        "message": {"type": "string", "example": "Authentication credentials were not provided."}
                                    }
                                }
                            }
                        }
                    }
                },
                "security": [{"BearerAuth": []}]
            }
            
            # Chỉ thêm POST nếu ViewSet không phải ReadOnly
            if not issubclass(viewset, ReadOnlyStandardizedModelViewSet):
                # POST - create
                openapi["paths"][path]["post"] = {
                    "tags": [resource_name + "s"],
                    "summary": f"Create a new {resource_name}",
                    "description": f"Creates a new {resource_name} and returns its details",
                    "operationId": f"create{resource_name.title()}",
                    "requestBody": {
                        "description": f"{resource_name.title()} object that needs to be created",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        },
                        "required": True
                    },
                    "responses": {
                        "201": {
                            "description": "Created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "status_code": {"type": "integer", "example": 201},
                                            "message": {"type": "string", "example": f"{resource_name.title()} created successfully"},
                                            "data": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid input",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "error"},
                                            "status_code": {"type": "integer", "example": 400},
                                            "message": {"type": "string", "example": "Invalid input"},
                                            "errors": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "security": [{"BearerAuth": []}]
                }
            
            # Detail actions
            detail_path = f"/{resource_name}s/{{id}}"
            if detail_path not in openapi["paths"]:
                openapi["paths"][detail_path] = {}
            
            # GET - retrieve
            openapi["paths"][detail_path]["get"] = {
                "tags": [resource_name + "s"],
                "summary": f"Get {resource_name} by ID",
                "description": f"Returns a single {resource_name}",
                "operationId": f"get{resource_name.title()}",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "description": f"ID of {resource_name} to return",
                        "required": True,
                        "schema": {"type": "integer", "format": "int64"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "success"},
                                        "status_code": {"type": "integer", "example": 200},
                                        "message": {"type": "string", "example": f"{resource_name.title()} details"},
                                        "data": {"type": "object"}
                                    }
                                }
                            }
                        }
                    },
                    "404": {
                        "description": "Not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "error"},
                                        "status_code": {"type": "integer", "example": 404},
                                        "message": {"type": "string", "example": f"{resource_name.title()} not found"}
                                    }
                                }
                            }
                        }
                    }
                },
                "security": [{"BearerAuth": []}]
            }
            
            # Chỉ thêm PUT/DELETE nếu ViewSet không phải ReadOnly
            if not issubclass(viewset, ReadOnlyStandardizedModelViewSet):
                # PUT - update
                openapi["paths"][detail_path]["put"] = {
                    "tags": [resource_name + "s"],
                    "summary": f"Update {resource_name}",
                    "description": f"Updates an existing {resource_name}",
                    "operationId": f"update{resource_name.title()}",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "description": f"ID of {resource_name} to update",
                            "required": True,
                            "schema": {"type": "integer", "format": "int64"}
                        }
                    ],
                    "requestBody": {
                        "description": f"{resource_name.title()} object that needs to be updated",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        },
                        "required": True
                    },
                    "responses": {
                        "200": {
                            "description": "Updated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "status_code": {"type": "integer", "example": 200},
                                            "message": {"type": "string", "example": f"{resource_name.title()} updated successfully"},
                                            "data": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "security": [{"BearerAuth": []}]
                }
                
                # DELETE - delete
                openapi["paths"][detail_path]["delete"] = {
                    "tags": [resource_name + "s"],
                    "summary": f"Delete {resource_name}",
                    "description": f"Deletes a {resource_name}",
                    "operationId": f"delete{resource_name.title()}",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "description": f"ID of {resource_name} to delete",
                            "required": True,
                            "schema": {"type": "integer", "format": "int64"}
                        }
                    ],
                    "responses": {
                        "204": {
                            "description": "Deleted successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "status_code": {"type": "integer", "example": 204},
                                            "message": {"type": "string", "example": f"{resource_name.title()} deleted successfully"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "security": [{"BearerAuth": []}]
                }
    
    def _generate_examples(self, viewsets, module_name, output_dir):
        """Sinh các ví dụ API cho các ViewSets."""
        examples_dir = os.path.join(output_dir, 'examples')
        os.makedirs(examples_dir, exist_ok=True)
        
        examples = {}
        
        # Tạo ví dụ cho từng ViewSet
        for viewset in viewsets:
            viewset_name = viewset.__name__
            resource_name = viewset_name.replace('ViewSet', '').lower()
            
            examples[resource_name] = self._generate_viewset_examples(viewset)
        
        # Lưu ví dụ vào file JSON
        output_file = os.path.join(examples_dir, f"{module_name.split('.')[-1]}_examples.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(examples, f, indent=2)
        
        self.stdout.write(self.style.SUCCESS(f"Đã sinh ví dụ API cho module {module_name} tại {output_file}"))
    
    def _generate_viewset_examples(self, viewset):
        """Sinh ví dụ cho một ViewSet cụ thể."""
        viewset_name = viewset.__name__
        resource_name = viewset_name.replace('ViewSet', '')
        
        examples = {}
        
        # Ví dụ cho list endpoint
        examples['list_response'] = {
            "status": "success",
            "status_code": 200,
            "message": f"List of {resource_name}s",
            "data": [
                {
                    "id": 1,
                    "name": f"Example {resource_name} 1",
                    "created_at": "2025-05-20T10:30:45Z"
                },
                {
                    "id": 2,
                    "name": f"Example {resource_name} 2",
                    "created_at": "2025-05-21T11:30:45Z"
                }
            ],
            "pagination": {
                "count": 20,
                "page_size": 10,
                "current_page": 1,
                "total_pages": 2,
                "next": f"/api/v1/{resource_name.lower()}s?page=2",
                "previous": None
            }
        }
        
        # Ví dụ cho retrieve endpoint
        examples['detail_response'] = {
            "status": "success",
            "status_code": 200,
            "message": f"{resource_name} details",
            "data": {
                "id": 1,
                "name": f"Example {resource_name}",
                "description": f"This is an example {resource_name}",
                "created_at": "2025-05-20T10:30:45Z",
                "updated_at": "2025-05-25T14:15:30Z"
            }
        }
        
        # Chỉ tạo ví dụ create/update/delete nếu ViewSet không phải ReadOnly
        if not issubclass(viewset, ReadOnlyStandardizedModelViewSet):
            # Ví dụ cho create endpoint
            examples['create_request'] = {
                "name": f"New {resource_name}",
                "description": f"This is a new {resource_name}"
            }
            
            examples['create_response'] = {
                "status": "success",
                "status_code": 201,
                "message": f"{resource_name} created successfully",
                "data": {
                    "id": 3,
                    "name": f"New {resource_name}",
                    "description": f"This is a new {resource_name}",
                    "created_at": "2025-05-27T10:30:45Z",
                    "updated_at": "2025-05-27T10:30:45Z"
                }
            }
            
            # Ví dụ cho update endpoint
            examples['update_request'] = {
                "name": f"Updated {resource_name}",
                "description": f"This is an updated {resource_name}"
            }
            
            examples['update_response'] = {
                "status": "success",
                "status_code": 200,
                "message": f"{resource_name} updated successfully",
                "data": {
                    "id": 1,
                    "name": f"Updated {resource_name}",
                    "description": f"This is an updated {resource_name}",
                    "created_at": "2025-05-20T10:30:45Z",
                    "updated_at": "2025-05-27T11:15:30Z"
                }
            }
            
            # Ví dụ cho delete endpoint
            examples['delete_response'] = {
                "status": "success",
                "status_code": 204,
                "message": f"{resource_name} deleted successfully"
            }
        
        # Ví dụ cho error response
        examples['error_response'] = {
            "status": "error",
            "status_code": 400,
            "message": "Invalid input",
            "errors": {
                "name": ["This field is required."],
                "description": ["This field cannot be blank."]
            }
        }
        
        return examples
    
    def _generate_markdown(self, viewsets, module_name, output_dir):
        """Sinh tài liệu Markdown cho các ViewSets."""
        markdown_dir = os.path.join(output_dir, 'markdown')
        os.makedirs(markdown_dir, exist_ok=True)
        
        # Tạo file Markdown
        output_file = os.path.join(markdown_dir, f"{module_name.split('.')[-1]}.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            # Tiêu đề
            f.write(f"# {module_name.split('.')[-1].title()} API\n\n")
            f.write(f"Tài liệu API cho module {module_name}.\n\n")
            
            # Phần nội dung cho từng ViewSet
            for viewset in viewsets:
                viewset_name = viewset.__name__
                resource_name = viewset_name.replace('ViewSet', '')
                
                f.write(f"## {resource_name}\n\n")
                
                # Thêm docstring của ViewSet nếu có
                if viewset.__doc__:
                    f.write(f"{viewset.__doc__.strip()}\n\n")
                
                # List endpoint
                f.write(f"### List {resource_name}s\n\n")
                f.write(f"**GET** `/api/v1/{resource_name.lower()}s`\n\n")
                f.write("**Parameters:**\n\n")
                f.write("| Name | Type | Description | Required |\n")
                f.write("|------|------|-------------|----------|\n")
                f.write("| page | integer | Page number | No |\n")
                f.write("| page_size | integer | Number of items per page | No |\n\n")
                
                # Retrieve endpoint
                f.write(f"### Get {resource_name} Details\n\n")
                f.write(f"**GET** `/api/v1/{resource_name.lower()}s/{{id}}`\n\n")
                f.write("**Parameters:**\n\n")
                f.write("| Name | Type | Description | Required |\n")
                f.write("|------|------|-------------|----------|\n")
                f.write("| id | integer | ID of the resource | Yes |\n\n")
                
                # Create endpoint
                if not issubclass(viewset, ReadOnlyStandardizedModelViewSet):
                    f.write(f"### Create {resource_name}\n\n")
                    f.write(f"**POST** `/api/v1/{resource_name.lower()}s`\n\n")
                    f.write("**Request Body:**\n\n")
                    f.write("```json\n")
                    f.write("{\n")
                    f.write(f'  "name": "New {resource_name}",\n')
                    f.write(f'  "description": "This is a new {resource_name}"\n')
                    f.write("}\n")
                    f.write("```\n\n")
                    
                    # Update endpoint
                    f.write(f"### Update {resource_name}\n\n")
                    f.write(f"**PUT** `/api/v1/{resource_name.lower()}s/{{id}}`\n\n")
                    f.write("**Parameters:**\n\n")
                    f.write("| Name | Type | Description | Required |\n")
                    f.write("|------|------|-------------|----------|\n")
                    f.write("| id | integer | ID of the resource | Yes |\n\n")
                    f.write("**Request Body:**\n\n")
                    f.write("```json\n")
                    f.write("{\n")
                    f.write(f'  "name": "Updated {resource_name}",\n')
                    f.write(f'  "description": "This is an updated {resource_name}"\n')
                    f.write("}\n")
                    f.write("```\n\n")
                    
                    # Delete endpoint
                    f.write(f"### Delete {resource_name}\n\n")
                    f.write(f"**DELETE** `/api/v1/{resource_name.lower()}s/{{id}}`\n\n")
                    f.write("**Parameters:**\n\n")
                    f.write("| Name | Type | Description | Required |\n")
                    f.write("|------|------|-------------|----------|\n")
                    f.write("| id | integer | ID of the resource | Yes |\n\n")
                
                # Thêm một dòng trống giữa các ViewSets
                f.write("\n")
        
        self.stdout.write(self.style.SUCCESS(f"Đã sinh tài liệu Markdown cho module {module_name} tại {output_file}"))
