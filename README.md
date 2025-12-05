# VisionTrack - Face Recognition Attendance System

A comprehensive Django-based attendance tracking system with face recognition capabilities and RESTful API.

## Features

- 🔐 JWT Authentication with role-based access control
- 👤 Employee management with face recognition support
- ⏰ Check-in/check-out tracking with face verification
- 📊 Attendance history and reporting
- 🔒 Secure API endpoints with permission controls
- 📧 Email notifications (activation, password reset)
- 📱 RESTful API for easy integration

## Tech Stack

- **Backend**: Django 5.2.8, Django REST Framework
- **Authentication**: JWT (Simple JWT), Djoser
- **Database**: PostgreSQL
- **Face Recognition**: Face encoding storage for verification
- **Environment Management**: python-decouple

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd visiontrack
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and update with your credentials:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
- `SECRET_KEY`: Django secret key
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: PostgreSQL credentials
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Email configuration

### 5. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

## API Documentation

See [EMPLOYEE_API_DOCUMENTATION.md](EMPLOYEE_API_DOCUMENTATION.md) for detailed API endpoints and usage examples.

### Key Endpoints

- `POST /auth/jwt/create/` - Login (get JWT token)
- `POST /auth/jwt/refresh/` - Refresh token
- `GET /api/employees/` - List employees (Admin)
- `POST /api/attendance/check-in/` - Check in with face verification
- `POST /api/attendance/check-out/` - Check out
- `GET /api/attendance/today/` - Today's attendance records

## Security Features

- Environment variables for sensitive data
- JWT token authentication
- Role-based permissions (Employee, Admin)
- Password validation and hashing
- CORS configuration for frontend integration
- `.gitignore` configured to exclude sensitive files

## Project Structure

```
visiontrack/
├── attendenceapp/      # Attendance tracking module
├── core/               # Core employee management
├── user/               # User authentication
├── media/              # Uploaded employee images
├── visiontrack/        # Project settings
└── manage.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is for educational purposes.

## Important Notes

- Never commit `.env` file to version control
- Keep face verification images secure and private
- Use strong passwords for production deployment
- Configure ALLOWED_HOSTS for production
- Set DEBUG=False in production
