"""
SQLAlchemy Post model for user posts management.
Defines the database schema for post-related operations.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base


class Post(Base):
    """
    Post model representing user posts in the database.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        text: Post content with size validation
        user_id: Foreign key referencing the user who created the post
        created_at: Timestamp of post creation
        updated_at: Timestamp of last update
        author: Relationship to the user who created the post
    """
    __tablename__ = "posts"
    
    id = Column(
        Integer, 
        primary_key=True, 
        index=True, 
        autoincrement=True,
        comment="Unique identifier for the post"
    )
    
    text = Column(
        Text, 
        nullable=False,
        comment="Post content, limited to 1MB in validation layer"
    )
    
    user_id = Column(
        Integer, 
        ForeignKey("users.id"), 
        nullable=False,
        index=True,
        comment="ID of the user who created this post"
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when post was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when post was last updated"
    )
    
    # Relationship with user
    author = relationship("User", back_populates="posts")
    
    def __repr__(self):
        """String representation of Post model."""
        return f"<Post(id={self.id}, user_id={self.user_id}, text_length={len(self.text) if self.text else 0})>"