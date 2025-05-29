"""
User controller implementing endpoint handlers for user operations.
Handles signup and login functionality with proper error handling.
"""

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.user import UserSignupRequest, UserLoginRequest, TokenResponse, UserResponse
from app.services.user_service import UserService
from app.utils.auth import ACCESS_TOKEN_EXPIRE_MINUTES


class UserController:
    """
    Controller class for user-related endpoint handlers.
    Implements business logic delegation to service layer.
    """
    
    @staticmethod
    async def signup(
        user_data: UserSignupRequest,
        db: Session = Depends(get_db)
    ) -> TokenResponse:
        """
        Handle user signup endpoint.
        Creates new user account and returns authentication token.
        
        Args:
            user_data: User signup request with email and password
            db: Database session dependency
            
        Returns:
            TokenResponse: JWT token for the newly created user
            
        Raises:
            HTTPException: If signup fails or email already exists
        """
        try:
            # Create new user through service layer
            user = UserService.create_user(db, user_data)
            
            # Generate token for the new user
            token = UserService.generate_token_for_user(user)
            
            return TokenResponse(
                token=token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
            )
            
        except HTTPException:
            # Re-raise HTTPExceptions from service layer
            raise
        except Exception as e:
            # Handle any unexpected errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during signup"
            )
    
    @staticmethod
    async def login(
        login_data: UserLoginRequest,
        db: Session = Depends(get_db)
    ) -> TokenResponse:
        """
        Handle user login endpoint.
        Authenticates user and returns token on success.
        
        Args:
            login_data: User login request with email and password
            db: Database session dependency
            
        Returns:
            TokenResponse: JWT token for authenticated user
            
        Raises:
            HTTPException: If login fails due to invalid credentials
        """
        try:
            # Authenticate user through service layer
            user, token = UserService.login_user(db, login_data)
            
            if not user or not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            return TokenResponse(
                token=token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
            )
            
        except HTTPException:
            # Re-raise HTTPExceptions
            raise
        except Exception as e:
            # Handle any unexpected errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during login"
            )
    
    @staticmethod
    async def get_current_user_info(
        current_user,
        db: Session = Depends(get_db)
    ) -> UserResponse:
        """
        Get current authenticated user information.
        Optional endpoint for user profile data.
        
        Args:
            current_user: Current authenticated user from dependency
            db: Database session dependency
            
        Returns:
            UserResponse: Current user's profile information
        """
        return UserResponse.from_orm(current_user)