"""
FastAPI dependency injection utilities for authentication and authorization.
Provides reusable dependencies for token validation and user authentication.
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import verify_access_token
from app.services.user_service import UserService
from app.models.user import User
from typing import Optional

# HTTP Bearer token scheme for automatic OpenAPI documentation
security = HTTPBearer()


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to extract and validate current user from JWT token.
    Used for endpoints requiring authentication.
    
    Args:
        credentials: HTTP Bearer credentials from request header
        db: Database session dependency
        
    Returns:
        User: Authenticated user instance
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Verify the JWT token
    token_data = verify_access_token(credentials.credentials)
    
    # Get user from database using token data
    user = UserService.get_user_by_id(db, token_data["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


async def get_current_user_from_header_token(
    token: Optional[str] = Header(None, alias="token"),
    db: Session = Depends(get_db)
) -> User:
    """
    Alternative dependency to extract user from token in custom header.
    Used when token is passed as a custom header instead of Authorization header.
    
    Args:
        token: Token from custom 'token' header
        db: Database session dependency
        
    Returns:
        User: Authenticated user instance
        
    Raises:
        HTTPException: If token is missing, invalid, or user not found
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing in request header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify the JWT token
    token_data = verify_access_token(token)
    
    # Get user from database using token data
    user = UserService.get_user_by_id(db, token_data["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


async def validate_token_dependency(
    token: Optional[str] = Header(None, alias="token")
) -> str:
    """
    Simple dependency to validate token presence.
    Returns the token string if present.
    
    Args:
        token: Token from custom 'token' header
        
    Returns:
        str: Valid token string
        
    Raises:
        HTTPException: If token is missing
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return token


class AuthenticationDependency:
    """
    Class-based dependency for more complex authentication scenarios.
    Provides flexible token validation with different extraction methods.
    """
    
    def __init__(self, require_active: bool = True):
        """
        Initialize authentication dependency.
        
        Args:
            require_active: Whether to require user to be active
        """
        self.require_active = require_active
    
    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        """
        Authenticate user with configurable requirements.
        
        Args:
            credentials: HTTP Bearer credentials
            db: Database session
            
        Returns:
            User: Authenticated user instance
            
        Raises:
            HTTPException: If authentication fails
        """
        # Verify the JWT token
        token_data = verify_access_token(credentials.credentials)
        
        # Get user from database
        user = UserService.get_user_by_id(db, token_data["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if self.require_active and not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user


# Pre-configured dependency instances
require_auth = AuthenticationDependency(require_active=True)
require_auth_allow_inactive = AuthenticationDependency(require_active=False)