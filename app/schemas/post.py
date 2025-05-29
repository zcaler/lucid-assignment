"""
Pydantic schemas for Post-related API requests and responses.
Provides extensive type validation and data serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import sys


class PostCreateRequest(BaseModel):
    """
    Schema for post creation request validation.
    
    Attributes:
        text: Post content with size validation (max 1MB)
    """
    text: str = Field(
        ..., 
        min_length=1,
        max_length=1048576,  # 1MB in characters (assuming 1 byte per char)
        description="Post content, maximum 1MB size"
    )
    
    @validator('text')
    def validate_text_size(cls, v):
        """
        Validate that text content doesn't exceed 1MB.
        
        Args:
            v: Text content to validate
            
        Returns:
            str: Validated text content
            
        Raises:
            ValueError: If content exceeds 1MB
        """
        text_size = sys.getsizeof(v.encode('utf-8'))
        if text_size > 1048576:  # 1MB in bytes
            raise ValueError(f'Text content exceeds 1MB limit. Current size: {text_size} bytes')
        return v


class PostResponse(BaseModel):
    """
    Schema for post data response.
    
    Attributes:
        id: Post's unique identifier (postID)
        text: Post content
        user_id: ID of the user who created the post
        created_at: Post creation timestamp
        updated_at: Post last update timestamp
    """
    id: int = Field(..., description="Post's unique identifier (postID)")
    text: str = Field(..., description="Post content")
    user_id: int = Field(..., description="ID of the user who created the post")
    created_at: datetime = Field(..., description="Post creation timestamp")
    updated_at: datetime = Field(..., description="Post last update timestamp")
    
    class Config:
        """Pydantic configuration for ORM mode."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PostsListResponse(BaseModel):
    """
    Schema for multiple posts response.
    
    Attributes:
        posts: List of user's posts
        total_count: Total number of posts
    """
    posts: List[PostResponse] = Field(
        ..., 
        description="List of user's posts"
    )
    
    total_count: int = Field(
        ..., 
        description="Total number of posts for the user"
    )


class PostDeleteRequest(BaseModel):
    """
    Schema for post deletion request validation.
    
    Attributes:
        post_id: ID of the post to delete
    """
    post_id: int = Field(
        ..., 
        gt=0,
        description="ID of the post to delete, must be positive integer",
        alias="postID"
    )


class PostCreateResponse(BaseModel):
    """
    Schema for post creation response.
    
    Attributes:
        post_id: ID of the newly created post
        message: Success message
    """
    post_id: int = Field(
        ..., 
        description="ID of the newly created post",
        alias="postID"
    )
    
    message: str = Field(
        default="Post created successfully",
        description="Success message"
    )