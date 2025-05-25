# Hướng dẫn tích hợp Frontend với Backend API

Tài liệu này hướng dẫn cách tích hợp giao diện người dùng (Frontend) với các API của hệ thống E-commerce và Midimo Chat.

## 1. Kiến trúc tích hợp

### 1.1. Tổng quan

Frontend Admin Panel tương tác với backend thông qua hai loại API:
- **REST API** từ E-commerce backend (Django)
- **WebSocket API** từ Midimo Chat (realtime features)

```
┌─────────────────┐          ┌─────────────────┐
│                 │  REST    │                 │
│  Admin Panel    │◄────────►│  E-commerce     │
│  (React)        │  API     │  Backend        │
│                 │          │                 │
└────────┬────────┘          └────────┬────────┘
         │                            │
         │                            │ gRPC
         │                            │
         │                            ▼
         │                   ┌─────────────────┐
         │  WebSocket       │                 │
         └──────────────────►  Midimo Chat    │
                            │  Service        │
                            │                 │
                            └─────────────────┘
```

### 1.2. Luồng dữ liệu

1. Frontend gọi REST API từ E-commerce để thực hiện các thao tác CRUD
2. Frontend kết nối WebSocket với Midimo Chat để nhận thông báo realtime
3. E-commerce Backend gọi gRPC API từ Midimo Chat khi cần

## 2. API Client cho Frontend

### 2.1. Cấu trúc API Client

Tạo thư mục `src/api` trong project admin panel với cấu trúc:

```
src/
└── api/
    ├── index.js         # Điểm nhập chính, export tất cả client
    ├── base.js          # Client API cơ sở
    ├── auth.js          # API xác thực
    ├── products.js      # API sản phẩm
    ├── orders.js        # API đơn hàng
    ├── customers.js     # API khách hàng
    ├── chat.js          # API chat (kết nối Midimo Chat)
    └── config.js        # Cấu hình API (endpoint, timeout, etc.)
```

### 2.2. Base API Client

Tạo file `src/api/base.js` với nội dung:

```javascript
import axios from 'axios';
import { API_BASE_URL, API_TIMEOUT } from './config';
import { getToken, refreshToken, logout } from '../utils/auth';

// Tạo instance axios
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Interceptor cho request
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor cho response
api.interceptors.response.use(
  (response) => {
    // Trả về dữ liệu trong trường "data" nếu có
    return response.data?.data !== undefined ? response.data.data : response.data;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Xử lý token hết hạn
    if (error.response?.status === 401 && 
        error.response?.data?.code === 'token_expired' && 
        !originalRequest._retry) {
      
      originalRequest._retry = true;
      
      try {
        // Thử làm mới token
        await refreshToken();
        
        // Cập nhật token mới trong header
        originalRequest.headers['Authorization'] = `Bearer ${getToken()}`;
        
        // Thử lại request
        return api(originalRequest);
      } catch (refreshError) {
        // Nếu không thể làm mới token, đăng xuất
        logout();
        return Promise.reject(refreshError);
      }
    }
    
    // Chuẩn hóa lỗi
    return Promise.reject({
      status: error.response?.status,
      ...error.response?.data,
      message: error.response?.data?.message || 'Đã xảy ra lỗi không xác định'
    });
  }
);

// Helper methods
export const apiClient = {
  /**
   * Gửi GET request
   * @param {string} url - URL endpoint
   * @param {Object} params - Query params
   */
  async get(url, params = {}) {
    return api.get(url, { params });
  },
  
  /**
   * Gửi POST request
   * @param {string} url - URL endpoint
   * @param {Object} data - Request body
   */
  async post(url, data = {}) {
    return api.post(url, data);
  },
  
  /**
   * Gửi PUT request
   * @param {string} url - URL endpoint
   * @param {Object} data - Request body
   */
  async put(url, data = {}) {
    return api.put(url, data);
  },
  
  /**
   * Gửi DELETE request
   * @param {string} url - URL endpoint
   */
  async delete(url) {
    return api.delete(url);
  },
  
  /**
   * Gửi PATCH request
   * @param {string} url - URL endpoint
   * @param {Object} data - Request body
   */
  async patch(url, data = {}) {
    return api.patch(url, data);
  }
};

export default api;
```

### 2.3. API Config

Tạo file `src/api/config.js`:

```javascript
// Cấu hình API
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api/v1';
export const API_TIMEOUT = 30000; // 30 seconds

// Cấu hình Midimo Chat
export const CHAT_WS_URL = process.env.REACT_APP_CHAT_WS_URL || 'wss://chat.example.com/ws';
export const CHAT_API_BASE_URL = process.env.REACT_APP_CHAT_API_BASE_URL || '/api/chat';
```

### 2.4. API Modules

#### Ví dụ: Products API

Tạo file `src/api/products.js`:

```javascript
import { apiClient } from './base';

export const productsApi = {
  /**
   * Lấy danh sách sản phẩm
   * @param {Object} params - Tham số lọc
   */
  getProducts(params = {}) {
    return apiClient.get('/products', params);
  },
  
  /**
   * Lấy chi tiết sản phẩm
   * @param {number} id - ID sản phẩm
   */
  getProduct(id) {
    return apiClient.get(`/products/${id}`);
  },
  
  /**
   * Tạo sản phẩm mới
   * @param {Object} data - Dữ liệu sản phẩm
   */
  createProduct(data) {
    return apiClient.post('/products', data);
  },
  
  /**
   * Cập nhật sản phẩm
   * @param {number} id - ID sản phẩm
   * @param {Object} data - Dữ liệu cập nhật
   */
  updateProduct(id, data) {
    return apiClient.put(`/products/${id}`, data);
  },
  
  /**
   * Xóa sản phẩm
   * @param {number} id - ID sản phẩm
   */
  deleteProduct(id) {
    return apiClient.delete(`/products/${id}`);
  }
};
```

#### Ví dụ: Chat API

Tạo file `src/api/chat.js`:

```javascript
import { apiClient } from './base';
import { CHAT_WS_URL } from './config';

export const chatApi = {
  /**
   * Lấy danh sách thread chat
   * @param {Object} params - Tham số lọc
   */
  getThreads(params = {}) {
    return apiClient.get('/chat/threads', params);
  },
  
  /**
   * Lấy tin nhắn trong thread
   * @param {string} threadId - ID thread
   * @param {Object} params - Tham số phân trang
   */
  getThreadMessages(threadId, params = {}) {
    return apiClient.get(`/chat/threads/${threadId}/messages`, params);
  },
  
  /**
   * Tạo thread chat mới
   * @param {Object} data - Dữ liệu thread
   */
  createThread(data) {
    return apiClient.post('/chat/threads', data);
  },
  
  /**
   * Gửi tin nhắn
   * @param {string} threadId - ID thread
   * @param {Object} data - Nội dung tin nhắn
   */
  sendMessage(threadId, data) {
    return apiClient.post(`/chat/threads/${threadId}/messages`, data);
  },
  
  /**
   * Kết nối WebSocket
   * @param {Function} onMessage - Callback khi nhận tin nhắn
   * @param {Function} onPresenceUpdate - Callback khi có cập nhật trạng thái
   * @param {Function} onError - Callback khi có lỗi
   * @returns {WebSocket} - WebSocket instance
   */
  connectWebSocket(onMessage, onPresenceUpdate, onError) {
    const token = localStorage.getItem('token');
    const ws = new WebSocket(`${CHAT_WS_URL}?token=${token}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'message':
          onMessage && onMessage(data.data);
          break;
        case 'presence':
          onPresenceUpdate && onPresenceUpdate(data.data);
          break;
        default:
          console.log('Unknown message type:', data.type);
      }
    };
    
    ws.onerror = (error) => {
      onError && onError(error);
    };
    
    return ws;
  }
};
```

### 2.5. Export API Modules

Tạo file `src/api/index.js`:

```javascript
export * from './auth';
export * from './products';
export * from './orders';
export * from './customers';
export * from './chat';
```

## 3. Sử dụng API trong React Components

### 3.1. Hooks-based API

Tạo custom hooks để sử dụng API:

```javascript
// src/hooks/useProducts.js
import { useState, useEffect } from 'react';
import { productsApi } from '../api';

export function useProducts(filters = {}) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const data = await productsApi.getProducts(filters);
        setProducts(data);
        setError(null);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProducts();
  }, [filters]);
  
  return { products, loading, error };
}
```

### 3.2. Redux Integration

Nếu dự án sử dụng Redux, tạo các action và reducer:

```javascript
// src/redux/slices/productsSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { productsApi } from '../../api';

export const fetchProducts = createAsyncThunk(
  'products/fetchProducts',
  async (filters, { rejectWithValue }) => {
    try {
      return await productsApi.getProducts(filters);
    } catch (err) {
      return rejectWithValue(err);
    }
  }
);

export const productsSlice = createSlice({
  name: 'products',
  initialState: {
    items: [],
    loading: false,
    error: null
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export default productsSlice.reducer;
```

### 3.3. Sử dụng trong Components

```jsx
// src/pages/ProductsPage.js
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchProducts } from '../redux/slices/productsSlice';

const ProductsPage = () => {
  const dispatch = useDispatch();
  const { items, loading, error } = useSelector((state) => state.products);
  
  useEffect(() => {
    dispatch(fetchProducts({ page: 1, limit: 20 }));
  }, [dispatch]);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      <h1>Danh sách sản phẩm</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Tên sản phẩm</th>
            <th>Giá</th>
            <th>Thao tác</th>
          </tr>
        </thead>
        <tbody>
          {items.map((product) => (
            <tr key={product.id}>
              <td>{product.id}</td>
              <td>{product.name}</td>
              <td>{product.price.toLocaleString('vi-VN')} đ</td>
              <td>
                <button>Sửa</button>
                <button>Xóa</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ProductsPage;
```

## 4. Tích hợp Chat và Realtime Features

### 4.1. Chat Component

```jsx
// src/components/Chat/ChatWindow.js
import React, { useState, useEffect, useRef } from 'react';
import { chatApi } from '../../api';

const ChatWindow = ({ threadId }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const wsRef = useRef(null);
  
  // Tải tin nhắn
  useEffect(() => {
    const loadMessages = async () => {
      try {
        setLoading(true);
        const data = await chatApi.getThreadMessages(threadId);
        setMessages(data);
      } catch (err) {
        console.error('Failed to load messages:', err);
      } finally {
        setLoading(false);
      }
    };
    
    loadMessages();
  }, [threadId]);
  
  // Kết nối WebSocket
  useEffect(() => {
    const handleNewMessage = (msg) => {
      if (msg.thread_id === threadId) {
        setMessages((prev) => [...prev, msg]);
      }
    };
    
    const handleError = (error) => {
      console.error('WebSocket error:', error);
    };
    
    // Tạo kết nối WebSocket
    wsRef.current = chatApi.connectWebSocket(
      handleNewMessage,
      () => {}, // Presence updates
      handleError
    );
    
    // Đóng kết nối khi unmount
    return () => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, [threadId]);
  
  // Gửi tin nhắn
  const sendMessage = async () => {
    if (!message.trim()) return;
    
    try {
      await chatApi.sendMessage(threadId, { content: message });
      setMessage('');
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };
  
  if (loading) return <div>Loading messages...</div>;
  
  return (
    <div className="chat-window">
      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className="message">
            <div className="message-sender">{msg.user_id}</div>
            <div className="message-content">{msg.content}</div>
            <div className="message-time">
              {new Date(msg.created_at).toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
      
      <div className="chat-input">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Nhập tin nhắn..."
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button onClick={sendMessage}>Gửi</button>
      </div>
    </div>
  );
};

export default ChatWindow;
```

### 4.2. Presence Component

```jsx
// src/components/Presence/UserPresence.js
import React, { useState, useEffect } from 'react';
import { chatApi } from '../../api';

const UserPresence = ({ userId }) => {
  const [status, setStatus] = useState('offline');
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);
  
  useEffect(() => {
    // Lấy trạng thái ban đầu
    const fetchInitialStatus = async () => {
      try {
        const response = await chatApi.getPresence([userId]);
        if (response && response.length > 0) {
          setStatus(response[0].status.toLowerCase());
        }
      } catch (err) {
        console.error('Failed to fetch presence:', err);
      }
    };
    
    fetchInitialStatus();
    
    // Theo dõi cập nhật qua WebSocket
    const handlePresenceUpdate = (data) => {
      if (data.user_id === userId) {
        setStatus(data.status.toLowerCase());
      }
    };
    
    // Kết nối WebSocket
    wsRef.current = chatApi.connectWebSocket(
      null, // Không quan tâm đến tin nhắn
      handlePresenceUpdate,
      (error) => console.error('WebSocket error:', error)
    );
    
    setWsConnected(true);
    
    // Đóng kết nối khi unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [userId]);
  
  // Màu sắc theo trạng thái
  const getStatusColor = () => {
    switch (status) {
      case 'online': return 'green';
      case 'away': return 'orange';
      case 'busy': return 'red';
      default: return 'gray';
    }
  };
  
  return (
    <div className="user-presence">
      <span
        className="status-indicator"
        style={{ backgroundColor: getStatusColor() }}
      />
      <span className="status-text">{status}</span>
      {!wsConnected && <span className="warning">(Không có kết nối realtime)</span>}
    </div>
  );
};

export default UserPresence;
```

## 5. Xử lý lỗi

### 5.1. Component xử lý lỗi

```jsx
// src/components/common/ErrorHandler.js
import React from 'react';
import { useDispatch } from 'react-redux';
import { showNotification } from '../../redux/slices/uiSlice';

// Các loại lỗi
const ERROR_TYPES = {
  VALIDATION: 'validation_error',
  NOT_FOUND: 'not_found',
  UNAUTHORIZED: 'unauthorized',
  FORBIDDEN: 'forbidden',
  SERVER_ERROR: 'server_error'
};

export const ErrorHandler = ({ error, children }) => {
  const dispatch = useDispatch();
  
  // Nếu không có lỗi, hiển thị children bình thường
  if (!error) return children;
  
  // Xử lý các loại lỗi
  switch (error.code) {
    case ERROR_TYPES.VALIDATION:
      // Hiển thị lỗi validation trong form
      return (
        <>
          {children}
          <div className="error-summary">
            <h4>Vui lòng kiểm tra lại thông tin:</h4>
            <ul>
              {Object.entries(error.errors || {}).map(([field, errors]) => (
                <li key={field}>
                  <strong>{field}:</strong> {errors.join(', ')}
                </li>
              ))}
            </ul>
          </div>
        </>
      );
      
    case ERROR_TYPES.NOT_FOUND:
      return <div className="error-page">Không tìm thấy tài nguyên yêu cầu</div>;
      
    case ERROR_TYPES.UNAUTHORIZED:
      // Chuyển hướng đến trang đăng nhập
      // ...
      return <div className="error-page">Phiên đăng nhập đã hết hạn</div>;
      
    case ERROR_TYPES.FORBIDDEN:
      return <div className="error-page">Bạn không có quyền truy cập tài nguyên này</div>;
      
    default:
      // Hiển thị thông báo lỗi
      dispatch(showNotification({
        type: 'error',
        message: error.message || 'Đã xảy ra lỗi không xác định'
      }));
      
      return children;
  }
};
```

### 5.2. Sử dụng ErrorHandler

```jsx
// src/pages/ProductFormPage.js
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { ErrorHandler } from '../components/common/ErrorHandler';
import { productsApi } from '../api';

const ProductFormPage = () => {
  const [product, setProduct] = useState({ name: '', price: 0 });
  const [error, setError] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await productsApi.createProduct(product);
      // Redirect or show success message
    } catch (err) {
      setError(err);
    }
  };
  
  return (
    <ErrorHandler error={error}>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Tên sản phẩm:</label>
          <input
            type="text"
            value={product.name}
            onChange={(e) => setProduct({ ...product, name: e.target.value })}
          />
        </div>
        <div>
          <label>Giá:</label>
          <input
            type="number"
            value={product.price}
            onChange={(e) => setProduct({ ...product, price: e.target.value })}
          />
        </div>
        <button type="submit">Lưu</button>
      </form>
    </ErrorHandler>
  );
};
```

## 6. Các vấn đề phổ biến và giải pháp

### 6.1. CORS

Vấn đề: Lỗi CORS khi frontend gọi API từ domain khác.

Giải pháp:
- Cấu hình CORS trên backend Django:
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://admin.example.com"
]
CORS_ALLOW_CREDENTIALS = True
```

### 6.2. Authentication

Vấn đề: Quản lý token và refresh token.

Giải pháp:
- Lưu token trong localStorage hoặc secure cookie
- Tự động refresh token khi hết hạn
- Logout khi không thể refresh

### 6.3. Rate Limiting

Vấn đề: API bị giới hạn request.

Giải pháp:
- Triển khai caching cho API calls
- Debounce hoặc throttle các request từ frontend

### 6.4. WebSocket Reconnection

Vấn đề: Kết nối WebSocket bị ngắt.

Giải pháp:
- Triển khai auto-reconnect với backoff
```javascript
function connectWithRetry(onMessage, onError) {
  const ws = chatApi.connectWebSocket(onMessage, onError);
  
  ws.onclose = (event) => {
    if (!event.wasClean) {
      // Kết nối bị ngắt bất ngờ, thử kết nối lại sau 5s
      setTimeout(() => {
        connectWithRetry(onMessage, onError);
      }, 5000);
    }
  };
  
  return ws;
}
```

## 7. Kiểm thử tích hợp

### 7.1. Mock API cho Testing

Sử dụng MSW (Mock Service Worker) để mock API:

```javascript
// src/mocks/handlers.js
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/v1/products', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        status: 'success',
        data: [
          { id: 1, name: 'Sản phẩm 1', price: 100000 },
          { id: 2, name: 'Sản phẩm 2', price: 200000 },
        ]
      })
    );
  }),
  
  rest.post('/api/v1/products', (req, res, ctx) => {
    const { name } = req.body;
    
    if (!name) {
      return res(
        ctx.status(400),
        ctx.json({
          status: 'error',
          code: 'validation_error',
          message: 'Dữ liệu không hợp lệ',
          errors: {
            name: ['Tên sản phẩm không được để trống']
          }
        })
      );
    }
    
    return res(
      ctx.status(201),
      ctx.json({
        status: 'success',
        data: {
          id: Math.floor(Math.random() * 1000),
          ...req.body
        }
      })
    );
  })
];
```

### 7.2. Integration Tests

```javascript
// src/__tests__/ProductsPage.test.js
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import productsReducer from '../redux/slices/productsSlice';
import ProductsPage from '../pages/ProductsPage';

const store = configureStore({
  reducer: {
    products: productsReducer
  }
});

test('renders products list', async () => {
  render(
    <Provider store={store}>
      <ProductsPage />
    </Provider>
  );
  
  // Kiểm tra loading
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
  
  // Đợi dữ liệu tải xong
  await waitFor(() => {
    expect(screen.getByText('Sản phẩm 1')).toBeInTheDocument();
    expect(screen.getByText('Sản phẩm 2')).toBeInTheDocument();
  });
});
```

## 8. Checklist tích hợp

- [ ] Thiết lập API client cơ bản
- [ ] Cấu hình interceptors cho xác thực và xử lý lỗi
- [ ] Triển khai API modules cho từng entity
- [ ] Tạo Redux slices hoặc React hooks
- [ ] Tích hợp WebSocket cho chat và presence
- [ ] Triển khai components sử dụng API
- [ ] Kiểm thử tích hợp với mock API
- [ ] Xác thực và giải quyết vấn đề CORS
- [ ] Triển khai error handling
