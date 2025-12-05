# Employee Management API Documentation

Base URL: `http://localhost:8000`

## Authentication
All endpoints require JWT authentication with admin or superuser role.

**Header:**
```
Authorization: JWT <access_token>
```

**Error Responses:**
- `401 Unauthorized`: `{ "detail": "Authentication credentials were not provided." }`
- `403 Forbidden`: `{ "detail": "You do not have permission to perform this action." }`

---

## Endpoints

### 1. List / Search Employees

**GET** `/core/api/employees/` or `/api_core/api/employees/`

**Query Parameters:**
- `search` (optional): Matches first_name, last_name, empId (username), email (case-insensitive)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10, max: 100)

**Response (200 OK):**
```json
{
  "count": 90,
  "next": "http://localhost:8000/core/api/employees/?page=2",
  "previous": null,
  "results": [
    {
      "id": "42",
      "empId": "employee42",
      "first_name": "Jane",
      "last_name": "Doe",
      "name": "Jane Doe",
      "email": "employee42@visiontrack.com",
      "role": "employee",
      "status": "Active",
      "photo_url": "http://localhost:8000/media/employee_images/employee_42.jpg",
      "created_at": "2025-12-01T09:33:12Z",
      "updated_at": "2025-12-01T09:33:12Z"
    }
  ]
}
```

**Example Requests:**

```bash
# List all employees
curl -H "Authorization: JWT <token>" \
  http://localhost:8000/core/api/employees/

# Search employees
curl -H "Authorization: JWT <token>" \
  "http://localhost:8000/core/api/employees/?search=Jane"

# With pagination
curl -H "Authorization: JWT <token>" \
  "http://localhost:8000/core/api/employees/?page=2&page_size=20"
```

---

### 2. Create Employee

**POST** `/core/api/employees/` or `/api_core/api/employees/`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `first_name` (string, required): Employee's first name
- `last_name` (string, required): Employee's last name
- `email` (string, required, unique): Employee's email address
- `empId` (string, required, unique): Employee ID/username
- `role` (string, optional): Default is "employee"
- `photo` (file, optional): Employee photo (JPEG/PNG, max 5MB)

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "121",
    "empId": "EMP121",
    "first_name": "Alan",
    "last_name": "Turing",
    "name": "Alan Turing",
    "email": "alan.turing@example.com",
    "role": "employee",
    "status": "Active",
    "photo_url": "http://localhost:8000/media/employee_images/employee_121.jpg",
    "created_at": "2025-12-01T11:04:22Z",
    "updated_at": "2025-12-01T11:04:22Z"
  },
  "message": "Employee created"
}
```

**Validation Error (400 Bad Request):**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "empId": ["empId already exists"],
    "email": ["Email already exists"]
  }
}
```

**Example Requests:**

```bash
# Create employee without photo
curl -X POST \
  -H "Authorization: JWT <token>" \
  -F "first_name=Alan" \
  -F "last_name=Turing" \
  -F "email=alan.turing@example.com" \
  -F "empId=EMP121" \
  http://localhost:8000/core/api/employees/

# Create employee with photo
curl -X POST \
  -H "Authorization: JWT <token>" \
  -F "first_name=Alan" \
  -F "last_name=Turing" \
  -F "email=alan.turing@example.com" \
  -F "empId=EMP121" \
  -F "photo=@/path/to/photo.jpg" \
  http://localhost:8000/core/api/employees/
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('first_name', 'Alan');
formData.append('last_name', 'Turing');
formData.append('email', 'alan.turing@example.com');
formData.append('empId', 'EMP121');
formData.append('photo', fileInput.files[0]); // optional

fetch('http://localhost:8000/core/api/employees/', {
  method: 'POST',
  headers: {
    'Authorization': 'JWT ' + token
  },
  body: formData
})
.then(r => r.json())
.then(data => console.log(data));
```

---

### 3. Get Single Employee

**GET** `/core/api/employees/{id}/` or `/api_core/api/employees/{id}/`

**Path Parameters:**
- `id` (string): User ID of the employee

**Success Response (200 OK):**
```json
{
  "id": "42",
  "empId": "employee42",
  "first_name": "Jane",
  "last_name": "Doe",
  "name": "Jane Doe",
  "email": "employee42@visiontrack.com",
  "role": "employee",
  "status": "Active",
  "photo_url": "http://localhost:8000/media/employee_images/employee_42.jpg",
  "created_at": "2025-12-01T09:33:12Z",
  "updated_at": "2025-12-01T09:33:12Z"
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "message": "Employee not found"
}
```

**Example Request:**
```bash
curl -H "Authorization: JWT <token>" \
  http://localhost:8000/core/api/employees/42/
```

---

### 4. Toggle Employee Status (Activate/Deactivate)

**PATCH** `/core/api/employees/{id}/` or `/api_core/api/employees/{id}/`

**Path Parameters:**
- `id` (string): User ID of the employee

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "status": "Inactive"
}
```

**Valid Status Values:**
- `"Active"` - Enable employee account
- `"Inactive"` - Disable employee account

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "42",
    "status": "Inactive",
    "updated_at": "2025-12-01T12:15:09Z"
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "message": "Employee not found"
}
```

**Validation Error (400 Bad Request):**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "status": ["\"invalid\" is not a valid choice."]
  }
}
```

**Example Requests:**

```bash
# Deactivate employee
curl -X PATCH \
  -H "Authorization: JWT <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "Inactive"}' \
  http://localhost:8000/core/api/employees/42/

# Activate employee
curl -X PATCH \
  -H "Authorization: JWT <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "Active"}' \
  http://localhost:8000/core/api/employees/42/
```

**JavaScript Example:**
```javascript
fetch('http://localhost:8000/core/api/employees/42/', {
  method: 'PATCH',
  headers: {
    'Authorization': 'JWT ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ status: 'Inactive' })
})
.then(r => r.json())
.then(data => console.log(data));
```

---

### 5. Delete Employee (Optional)

**DELETE** `/core/api/employees/{id}/` or `/api_core/api/employees/{id}/`

**Path Parameters:**
- `id` (string): User ID of the employee

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Employee deleted"
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "message": "Employee not found"
}
```

**Example Request:**
```bash
curl -X DELETE \
  -H "Authorization: JWT <token>" \
  http://localhost:8000/core/api/employees/42/
```

**Note:** Deleting an employee also deletes the associated User record (cascade delete).

---

## Data Model Details

### Employee Object
```typescript
{
  id: string;              // User ID
  empId: string;           // Username/Employee ID
  first_name: string;      // First name
  last_name: string;       // Last name
  name: string;            // Full name (computed)
  email: string;           // Email address (unique)
  role: string;            // User role (always "employee" for employees)
  status: "Active" | "Inactive";  // Account status
  photo_url: string | null;       // Full URL to photo or null
  created_at: string;      // ISO 8601 timestamp
  updated_at: string;      // ISO 8601 timestamp
}
```

---

## URL Patterns

The employee APIs are available under two URL patterns:

1. **Recommended for frontend:** `/core/api/employees/`
2. **Alternative:** `/api_core/api/employees/`

Both patterns work identically.

---

## Authentication Flow

1. **Login to get JWT token:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"admin1@visiontrack.com","password":"admin123"}' \
  http://localhost:8000/auth/jwt/create/
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

2. **Use access token in subsequent requests:**
```
Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## Testing with Insomnia/Postman

### Setup Environment Variables
- `base_url`: `http://localhost:8000`
- `token`: Your JWT access token

### Collection

**1. Login (Get Token)**
- Method: `POST`
- URL: `{{base_url}}/auth/jwt/create/`
- Body (JSON):
  ```json
  {
    "email": "admin1@visiontrack.com",
    "password": "admin123"
  }
  ```

**2. List Employees**
- Method: `GET`
- URL: `{{base_url}}/core/api/employees/`
- Headers: `Authorization: JWT {{token}}`

**3. Search Employees**
- Method: `GET`
- URL: `{{base_url}}/core/api/employees/?search=Jane`
- Headers: `Authorization: JWT {{token}}`

**4. Create Employee**
- Method: `POST`
- URL: `{{base_url}}/core/api/employees/`
- Headers: `Authorization: JWT {{token}}`
- Body: `multipart/form-data`
  - `first_name`: Alan
  - `last_name`: Turing
  - `email`: alan@example.com
  - `empId`: EMP200
  - `photo`: (file upload)

**5. Get Employee**
- Method: `GET`
- URL: `{{base_url}}/core/api/employees/42/`
- Headers: `Authorization: JWT {{token}}`

**6. Toggle Status**
- Method: `PATCH`
- URL: `{{base_url}}/core/api/employees/42/`
- Headers: `Authorization: JWT {{token}}`, `Content-Type: application/json`
- Body (JSON):
  ```json
  {
    "status": "Inactive"
  }
  ```

**7. Delete Employee**
- Method: `DELETE`
- URL: `{{base_url}}/core/api/employees/42/`
- Headers: `Authorization: JWT {{token}}`

---

## Notes

- Default password for created employees: `employee123`
- Status values are case-sensitive: `"Active"` and `"Inactive"` only
- Photo uploads support JPEG and PNG formats
- Maximum photo size: 5MB (configurable in Django settings)
- Employee records automatically generate face encodings when photos are uploaded
- Deleting an employee cascades to delete the User record and Employee record
- Search is case-insensitive and searches across first_name, last_name, empId, and email
- Pagination uses standard Django REST framework pagination format
