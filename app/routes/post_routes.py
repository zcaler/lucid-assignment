"""
Post routing layer defining API endpoints for post operations.
Maps HTTP routes to controller methods with authentication and documentation.
"""

from fastapi import APIRouter, Depends, Header
from app.controllers.post_controller import PostController
from app.schemas.post import (
    PostCreateRequest, 
    PostCreateResponse, 
    PostsListResponse, 
    PostDeleteRequest
)
from app.utils.dependencies import get_current_user_from_header_token
from app.models.user import User
from typing import Dict

# Create router instance for post endpoints
post_router = APIRouter(
    prefix="/api/posts",
    tags=["Posts"],
    responses={
        401: {"description": "Authentication required"},
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


@post_router.post(
    "/add",
    response_model=PostCreateResponse,
    status_code=201,
    summary="Create New Post",
    description="Create a new post with text content. Requires authentication token. Maximum payload size is 1MB."
)
async def add_post_endpoint(
    post_data: PostCreateRequest,
    current_user: User = Depends(get_current_user_from_header_token)
) -> PostCreateResponse:
    """
    Add post endpoint for creating new posts.
    
    - **text**: Post content (required, max 1MB)
    - **token**: Authentication token (required in header)
    
    Validates payload size and saves post to database.
    Returns postID of the created post.
    """
    return await PostController.add_post(post_data, current_user)


@post_router.get(
    "/get",
    response_model=PostsListResponse,
    status_code=200,
    summary="Get User Posts",
    description="Retrieve all posts for the authenticated user. Implements 5-minute response caching."
)
async def get_posts_endpoint(
    current_user: User = Depends(get_current_user_from_header_token)
) -> PostsListResponse:
    """
    Get posts endpoint for retrieving user's posts.
    
    - **token**: Authentication token (required in header)
    
    Returns all posts for the authenticated user with caching.
    Cache TTL is 5 minutes for improved performance.
    """
    return await PostController.get_posts(current_user)


@post_router.delete(
    "/delete",
    response_model=Dict[str, str],
    status_code=200,
    summary="Delete Post",
    description="Delete a specific post by ID. User can only delete their own posts."
)
async def delete_post_endpoint(
    delete_request: PostDeleteRequest,
    current_user: User = Depends(get_current_user_from_header_token)
) -> Dict[str, str]:
    """
    Delete post endpoint for removing posts.
    
    - **postID**: ID of the post to delete (required)
    - **token**: Authentication token (required in header)
    
    Deletes the specified post if it belongs to the authenticated user.
    Returns success confirmation message.
    """
    return await PostController.delete_post(delete_request, current_user)