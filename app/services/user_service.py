"""
User service layer implementing business logic for user operations.
Handles user authentication, registration, and database interactions.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserSignupRequest, UserLoginRequest
from app.utils.auth import hash_password, verify_password, create_access_token
from typing import Optional


class UserService:
    """
    Service class for user-related business logic.
    Implements efficient database operations with minimal queries.
    """
    
    @staticmethod
    def create_user(db: Session, user_data: UserSignupRequest) -> User:
        """
        Create a new user account with password hashing.
        
        Args:
            db: Database session
            user_data: User signup data with email and password
            
        Returns:
            User: Created user instance
            
        Raises:
            HTTPException: If email already exists or creation fails
        """
        try:
            # Hash password before storing
            hashed_password = hash_password(user_data.password)
            
            # Create new user instance
            db_user = User(
                email=user_data.email,
                password_hash=hashed_password,
                is_active=True
            )
            
            # Add to database with single transaction
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return db_user
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLoginRequest) -> Optional[User]:
        """
        Authenticate user with email and password.
        Single database query for efficient authentication.
        
        Args:
            db: Database session
            login_data: User login credentials
            
        Returns:
            User: Authenticated user if credentials are valid, None otherwise
        """
        # Single query to get user by email
        user = db.query(User).filter(
            User.email == login_data.email,
            User.is_active == True
        ).first()
        
        if not user:
            return None
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Retrieve user by ID with single database query.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            
        Returns:
            User: User instance if found, None otherwise
        """
        return db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Retrieve user by email with single database query.
        
        Args:
            db: Database session
            email: User's email address
            
        Returns:
            User: User instance if found, None otherwise
        """
        return db.query(User).filter(
            User.email == email,
            User.is_active == True
        ).first()
    
    @staticmethod
    def generate_token_for_user(user: User) -> str:
        """
        Generate JWT token for authenticated user.
        
        Args:
            user: Authenticated user instance
            
        Returns:
            str: JWT access token
        """
        token_data = {
            "user_id": user.id,
            "email": user.email
        }
        
        return create_access_token(data=token_data)
    
    @staticmethod
    def login_user(db: Session, login_data: UserLoginRequest) -> tuple[Optional[User], Optional[str]]:
        """
        Complete user login process with authentication and token generation.
        
        Args:
            db: Database session
            login_data: User login credentials
            
        Returns:
            tuple: (User instance, JWT token) if successful, (None, None) if failed
        """
        # Authenticate user
        user = UserService.authenticate_user(db, login_data)
        
        if not user:
            return None, None
        
        # Generate token
        token = UserService.generate_token_for_user(user)
        
        return user, token