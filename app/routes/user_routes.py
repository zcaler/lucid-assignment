"""
User routing layer defining API endpoints for user operations.
Maps HTTP routes to controller methods with proper documentation.
"""

from fastapi import APIRouter, Depends
from app.controllers.user_controller import UserController
from app.schemas.user import UserSignupRequest, UserLoginRequest, TokenResponse, UserResponse
from app.utils.dependencies import get_current_user_from_header_token
from app.models.user import User

# Create router instance for user endpoints
user_router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


@user_router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=201,
    summary="User Registration",
    description="Register a new user account with email and password. Returns authentication token upon successful registration."
)
async def signup_endpoint(user_data: UserSignupRequest) -> TokenResponse:
    """
    Signup endpoint for user registration.
    
    - **email**: Valid email address (must be unique)
    - **password**: Password with complexity requirements (8+ chars, uppercase, lowercase, digit, special char)
    
    Returns JWT token for immediate authentication after registration.
    """
    return await UserController.signup(user_data)


@user_router.post(
    "/login",
    response_model=TokenResponse,
    status_code=200,
    summary="User Authentication",
    description="Authenticate user with email and password. Returns authentication token upon successful login."
)
async def login_endpoint(login_data: UserLoginRequest) -> TokenResponse:
    """
    Login endpoint for user authentication.
    
    - **email**: User's registered email address
    - **password**: User's password
    
    Returns JWT token for API access. Token expires in 60 minutes.
    """
    return await UserController.login(login_data)


@user_router.get(
    "/me",
    response_model=UserResponse,
    status_code=200,
    summary="Get Current User",
    description="Retrieve current authenticated user's profile information."
)
async def get_current_user_endpoint(
    current_user: User = Depends(get_current_user_from_header_token)
) -> UserResponse:
    """
    Get current user profile endpoint.
    
    Requires authentication token in 'token' header.
    Returns user profile information including ID, email, and account status.
    """
    return await UserController.get_current_user_info(current_user)