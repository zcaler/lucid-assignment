"""
Post service layer implementing business logic for post operations.
Handles post creation, retrieval, deletion, and caching management.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.post import Post
from app.schemas.post import PostCreateRequest, PostResponse, PostsListResponse
from app.utils.cache import CacheService
from typing import List, Optional


class PostService:
    """
    Service class for post-related business logic.
    Implements efficient database operations with caching and minimal queries.
    """
    
    @staticmethod
    def create_post(db: Session, user_id: int, post_data: PostCreateRequest) -> Post:
        """
        Create a new post for a user.
        Invalidates user's posts cache after creation.
        
        Args:
            db: Database session
            user_id: ID of the user creating the post
            post_data: Post content data
            
        Returns:
            Post: Created post instance
            
        Raises:
            HTTPException: If post creation fails
        """
        try:
            # Create new post instance
            db_post = Post(
                text=post_data.text,
                user_id=user_id
            )
            
            # Add to database with single transaction
            db.add(db_post)
            db.commit()
            db.refresh(db_post)
            
            # Invalidate user's posts cache since new post was added
            CacheService.invalidate_user_posts_cache(user_id)
            
            return db_post
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create post due to data integrity error"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create post"
            )
    
    @staticmethod
    def get_user_posts(db: Session, user_id: int) -> PostsListResponse:
        """
        Retrieve all posts for a user with caching support.
        Implements 5-minute cache TTL for improved performance.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            
        Returns:
            PostsListResponse: User's posts with total count
        """
        # Check cache first
        cached_posts = CacheService.get_cached_posts(user_id)
        if cached_posts:
            return cached_posts["data"]
        
        # Single query to get all user posts ordered by creation date
        posts = db.query(Post).filter(
            Post.user_id == user_id
        ).order_by(Post.created_at.desc()).all()
        
        # Convert to response format
        posts_response = PostsListResponse(
            posts=[PostResponse.from_orm(post) for post in posts],
            total_count=len(posts)
        )
        
        # Cache the response for 5 minutes
        CacheService.cache_user_posts(user_id, posts_response)
        
        return posts_response
    
    @staticmethod
    def get_post_by_id(db: Session, post_id: int, user_id: int) -> Optional[Post]:
        """
        Retrieve a specific post by ID and user ID.
        Ensures users can only access their own posts.
        
        Args:
            db: Database session
            post_id: Post's unique identifier
            user_id: User's unique identifier
            
        Returns:
            Post: Post instance if found and belongs to user, None otherwise
        """
        return db.query(Post).filter(
            Post.id == post_id,
            Post.user_id == user_id
        ).first()
    
    @staticmethod
    def delete_post(db: Session, post_id: int, user_id: int) -> bool:
        """
        Delete a post by ID if it belongs to the user.
        Invalidates user's posts cache after deletion.
        
        Args:
            db: Database session
            post_id: Post's unique identifier
            user_id: User's unique identifier
            
        Returns:
            bool: True if post was deleted, False if not found
            
        Raises:
            HTTPException: If deletion fails
        """
        try:
            # Single query to find and verify ownership
            post = db.query(Post).filter(
                Post.id == post_id,
                Post.user_id == user_id
            ).first()
            
            if not post:
                return False
            
            # Delete the post
            db.delete(post)
            db.commit()
            
            # Invalidate user's posts cache since post was deleted
            CacheService.invalidate_user_posts_cache(user_id)
            
            return True
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete post"
            )
    
    @staticmethod
    def get_post_count_for_user(db: Session, user_id: int) -> int:
        """
        Get total number of posts for a user.
        Efficient count query without loading post data.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            
        Returns:
            int: Total number of posts for the user
        """
        return db.query(Post).filter(Post.user_id == user_id).count()