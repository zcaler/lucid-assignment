"""
Pydantic schemas for User-related API requests and responses.
Provides extensive type validation and data serialization.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserSignupRequest(BaseModel):
    """
    Schema for user signup request validation.
    
    Attributes:
        email: Valid email address with format validation
        password: Password with length and complexity requirements
    """
    email: EmailStr = Field(
        ..., 
        description="Valid email address for user registration",
        example="user@example.com"
    )
    
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128,
        description="Password must be 8-128 characters with complexity requirements"
    )
    
    @validator('password')
    def validate_password_strength(cls, v):
        """
        Validate password complexity requirements.
        Must contain at least one uppercase, lowercase, digit, and special character.
        
        Args:
            v: Password string to validate
            
        Returns:
            str: Validated password
            
        Raises:
            ValueError: If password doesn't meet complexity requirements
        """
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLoginRequest(BaseModel):
    """
    Schema for user login request validation.
    
    Attributes:
        email: Valid email address
        password: User password
    """
    email: EmailStr = Field(
        ..., 
        description="User's email address for authentication",
        example="user@example.com"
    )
    
    password: str = Field(
        ..., 
        min_length=1, 
        max_length=128,
        description="User's password for authentication"
    )


class TokenResponse(BaseModel):
    """
    Schema for authentication token response.
    
    Attributes:
        token: JWT or authentication token string
        token_type: Type of token (usually 'bearer')
        expires_in: Token expiration time in seconds
    """
    token: str = Field(
        ..., 
        description="Authentication token for API access",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    
    token_type: str = Field(
        default="bearer", 
        description="Token type for authorization header"
    )
    
    expires_in: int = Field(
        default=3600, 
        description="Token expiration time in seconds"
    )


class UserResponse(BaseModel):
    """
    Schema for user data response.
    
    Attributes:
        id: User's unique identifier
        email: User's email address
        is_active: User's account status
        created_at: Account creation timestamp
    """
    id: int = Field(..., description="User's unique identifier")
    email: EmailStr = Field(..., description="User's email address")
    is_active: bool = Field(..., description="User's account status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    class Config:
        """Pydantic configuration for ORM mode."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }