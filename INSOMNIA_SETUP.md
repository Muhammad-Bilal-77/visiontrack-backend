# Insomnia Setup Guide for Attendance APIs

## Quick Start

### 1. Install Insomnia
Download from: https://insomnia.rest/

### 2. Create a New Request

#### Step 1: Set the HTTP Method & URL
- Click **+** to create a new request
- Select method: **GET** (or **POST** for config/notify endpoints)
- Enter URL: `http://localhost:8000/api/attendance/config/`

#### Step 2: Add Headers
Click on the **Header** tab below the URL bar and add:

| Key | Value |
|-----|-------|
| `Authorization` | `JWT <your_admin_token>` |
| `Content-Type` | `application/json` |

**How to get your admin token:**
1. First, you need to log in via Djoser to get a JWT token.
2. In Insomnia, create a POST request to `http://localhost:8000/auth/jwt/create/`
3. Set method to **POST**, **Header** tab: `Content-Type: application/json`
4. Go to **Body** tab, select **JSON** and paste:
   ```json
   {
     "email": "your_admin@email.com",
     "password": "your_password"
   }
   ```
5. Click **Send**. The response will contain `"access"` — that's your JWT token.
6. Copy the `access` value and use it in the `Authorization` header as `JWT <token>`

---

## API Endpoints in Insomnia

### 1. GET Config
**Method:** GET  
**URL:** `http://localhost:8000/api/attendance/config/`  
**Headers:**
- `Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImFkbWluQGV4YW1wbGUuY29tIiwiZXhwIjoxNzAxMDAwMDAwfQ.abcdefghijklmnopqrstuvwxyz1234567890`

### 2. POST Update Config
**Method:** POST  
**URL:** `http://localhost:8000/api/attendance/config/`  
**Headers:**
- `Authorization: JWT <token>`
- `Content-Type: application/json`

**Body (JSON):**
```json
{
  "start_time": "09:30:00",
  "end_time": "18:30:00",
  "late_buffer_minutes": 20
}
```

### 3. GET Summary Stats (Dashboard Cards + Pie Chart)
**Method:** GET  
**URL:** `http://localhost:8000/api/attendance/stats/summary/?month=11`  
**Headers:**
- `Authorization: JWT <token>`

(Remove `?month=11` to use current month)

### 4. GET Daily Stats (Last 7 Days)
**Method:** GET  
**URL:** `http://localhost:8000/api/attendance/stats/daily/`  
**Headers:**
- `Authorization: JWT <token>`

### 5. GET Employee Stats (Current Month)
**Method:** GET  
**URL:** `http://localhost:8000/api/attendance/stats/employees/`  
**Headers:**
- `Authorization: JWT <token>`

### 6. GET Today's Logs (Table)
**Method:** GET  
**URL:** `http://localhost:8000/api/attendance/logs/today/`  
**Headers:**
- `Authorization: JWT <token>`

### 7. POST Send Notification
**Method:** POST  
**URL:** `http://localhost:8000/api/attendance/notify/`  
**Headers:**
- `Authorization: JWT <token>`
- `Content-Type: application/json`

**Body (JSON):**
```json
{
  "employee_id": "1",
  "message_type": "late_warning"
}
```

---

## How to Set Headers in Insomnia UI

1. Open a request
2. Click the **Header** tab (below the URL bar)
3. Click **+ Add** or just type directly in the table:
   - Column 1 (Key): `Authorization`
   - Column 2 (Value): `JWT your_token_here`
4. Add another row:
   - Column 1 (Key): `Content-Type`
   - Column 2 (Value): `application/json`

---

## Pro Tips

### Use Insomnia Environment Variables (Optional)
Instead of pasting the token every time, save it as a variable:

1. Click **Manage Environments** (gear icon, top-left)
2. Click **Create**
3. Name it: `VisionTrack Dev`
4. Add:
   ```json
   {
     "base_url": "http://localhost:8000",
     "token": "JWT your_admin_token_here"
   }
   ```
5. In requests, use:
   - URL: `{{ base_url }}/api/attendance/config/`
   - Header: `Authorization: {{ token }}`

### Get Token via Insomnia (Save Time)
1. Create POST request to `{{ base_url }}/auth/jwt/create/`
2. Body:
   ```json
   {
     "email": "admin@example.com",
     "password": "password123"
   }
   ```
3. Click **Send**
4. Copy the `access` value from response
5. Use it in other requests

---

## Common Issues

**401 Unauthorized**
- Your token is invalid or expired. Get a fresh token by logging in again.
- Make sure you're using `JWT ` prefix: `JWT eyJ0...` not just `eyJ0...`

**403 Forbidden**
- Your user account is not an admin or superuser.
- Log in with an admin account to get an admin token.

**CORS Error (if calling from frontend)**
- The backend already has `CORS_ALLOW_ALL_ORIGINS = True`, so this shouldn't happen in development.

**500 Email Error (on /notify/)**
- Ensure your Gmail SMTP settings are correct in `settings.py`
- If testing, use `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` to print emails to terminal instead.
