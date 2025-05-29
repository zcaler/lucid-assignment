"""
SQLAlchemy User model for user authentication and management.
Defines the database schema for user-related operations.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base


class User(Base):
    """
    User model representing users in the database.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        email: Unique email address for user authentication
        password_hash: Hashed password for security
        is_active: Boolean flag for account status
        created_at: Timestamp of user creation
        updated_at: Timestamp of last update
        posts: Relationship to user's posts
    """
    __tablename__ = "users"
    
    id = Column(
        Integer, 
        primary_key=True, 
        index=True, 
        autoincrement=True,
        comment="Unique identifier for the user"
    )
    
    email = Column(
        String(255), 
        unique=True, 
        index=True, 
        nullable=False,
        comment="User's email address, must be unique"
    )
    
    password_hash = Column(
        String(255), 
        nullable=False,
        comment="Hashed password for authentication"
    )
    
    is_active = Column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Account status flag"
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when user was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when user was last updated"
    )
    
    # Relationship with posts
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation of User model."""
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"