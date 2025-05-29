"""
Post controller implementing endpoint handlers for post operations.
Handles post creation, retrieval, and deletion with authentication.
"""

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.post import (
    PostCreateRequest, 
    PostCreateResponse, 
    PostsListResponse, 
    PostDeleteRequest
)
from app.services.post_service import PostService
from app.models.user import User
from app.utils.dependencies import get_current_user_from_header_token


class PostController:
    """
    Controller class for post-related endpoint handlers.
    Implements business logic delegation to service layer with authentication.
    """
    
    @staticmethod
    async def add_post(
        post_data: PostCreateRequest,
        current_user: User = Depends(get_current_user_from_header_token),
        db: Session = Depends(get_db)
    ) -> PostCreateResponse:
        """
        Handle add post endpoint.
        Creates new post for authenticated user with payload validation.
        
        Args:
            post_data: Post creation request with text content
            current_user: Authenticated user from token dependency
            db: Database session dependency
            
        Returns:
            PostCreateResponse: Response with created post ID
            
        Raises:
            HTTPException: If post creation fails or payload exceeds 1MB
        """
        try:
            # Create post through service layer
            post = PostService.create_post(db, current_user.id, post_data)
            
            return PostCreateResponse(
                postID=post.id,
                message="Post created successfully"
            )
            
        except HTTPException:
            # Re-raise HTTPExceptions from service layer
            raise
        except Exception as e:
            # Handle any unexpected errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during post creation"
            )
    
    @staticmethod
    async def get_posts(
        current_user: User = Depends(get_current_user_from_header_token),
        db: Session = Depends(get_db)
    ) -> PostsListResponse:
        """
        Handle get posts endpoint.
        Retrieves all posts for authenticated user with 5-minute caching.
        
        Args:
            current_user: Authenticated user from token dependency
            db: Database session dependency
            
        Returns:
            PostsListResponse: List of user's posts with total count
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            # Get user posts through service layer (with caching)
            posts_response = PostService.get_user_posts(db, current_user.id)
            
            return posts_response
            
        except Exception as e:
            # Handle any unexpected errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during posts retrieval"
            )
    
    @staticmethod
    async def delete_post(
        delete_request: PostDeleteRequest,
        current_user: User = Depends(get_current_user_from_header_token),
        db: Session = Depends(get_db)
    ) -> dict:
        """
        Handle delete post endpoint.
        Deletes specified post if it belongs to authenticated user.
        
        Args:
            delete_request: Post deletion request with post ID
            current_user: Authenticated user from token dependency
            db: Database session dependency
            
        Returns:
            dict: Success message confirmation
            
        Raises:
            HTTPException: If post not found or deletion fails
        """
        try:
            # Attempt to delete post through service layer
            deleted = PostService.delete_post(
                db, 
                delete_request.post_id, 
                current_user.id
            )
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found or you don't have permission to delete it"
                )
            
            return {
                "message": "Post deleted successfully",
                "post_id": delete_request.post_id
            }
            
        except HTTPException:
            # Re-raise HTTPExceptions
            raise
        except Exception as e:
            # Handle any unexpected errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during post deletion"
            )