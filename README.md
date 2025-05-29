# Lucid Task API

A FastAPI web application following the MVC design pattern with MySQL database integration, JWT authentication, and comprehensive field validation.

## Features

- **MVC Architecture**: Clean separation of concerns with Models, Views (Controllers), and Services
- **JWT Authentication**: Token-based authentication for secure API access
- **MySQL Database**: SQLAlchemy ORM with MySQL backend
- **Field Validation**: Extensive Pydantic validation for all endpoints
- **Response Caching**: 5-minute TTL caching for GetPosts endpoint
- **Dependency Injection**: Clean dependency management for authentication
- **Comprehensive Documentation**: Auto-generated API docs with Swagger/OpenAPI

## API Endpoints

### User Authentication
- `POST /api/users/signup` - User registration with email and password
- `POST /api/users/login` - User authentication returning JWT token

### Post Management
- `POST /api/posts/add` - Create new post (requires authentication)
- `GET /api/posts/get` - Retrieve user's posts with caching (requires authentication)
- `DELETE /api/posts/delete` - Delete specific post (requires authentication)

## Requirements

- Python 3.8+
- MySQL 5.7+ or 8.0+
- pip or pipenv for dependency management

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/zcaler/lucid-assignment
cd lucid
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Database Setup**
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE lucid_db;
```

4. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Run the application**
```bash
python main.py
```

The application will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

All post-related endpoints require authentication using a JWT token obtained from the login endpoint. Include the token in the request header:

```
token: <your-jwt-token>
```

## Validation Rules

### User Registration
- **Email**: Valid email format, must be unique
- **Password**: Minimum 8 characters, must contain uppercase, lowercase, digit, and special character

### Post Creation
- **Text**: Required, maximum 1MB size
- **Token**: Valid JWT token required

## Caching

The GetPosts endpoint implements 5-minute response caching for improved performance. Cache is automatically invalidated when posts are created or deleted.

## Error Handling

The API provides consistent error responses with appropriate HTTP status codes and descriptive error messages.

## Development

### Project Structure
```
app/
├── config/          # Database configuration
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas
├── services/        # Business logic layer
├── controllers/     # Request handlers
├── routes/          # API route definitions
└── utils/           # Authentication and caching utilities
```

### Running Tests
```bash
# Add your test commands here
pytest
```

## Database Schema

### Users Table
- `id` (Primary Key)
- `email` (Unique)
- `password_hash`
- `is_active`
- `created_at`
- `updated_at`

### Posts Table
- `id` (Primary Key)
- `text`
- `user_id` (Foreign Key)
- `created_at`
- `updated_at`

## License

This project is licensed under the MIT License.