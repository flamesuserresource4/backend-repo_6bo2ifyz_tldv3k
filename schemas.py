"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Handmade chocolate schema for this app
class Chocolate(BaseModel):
    """
    Chocolates collection schema
    Collection name: "chocolate"
    """
    name: str = Field(..., description="Chocolate name")
    description: str = Field(..., description="Tasting notes and description")
    price: float = Field(..., ge=0, description="Price per unit")
    category: str = Field(..., description="Type/category e.g., Truffle, Bar, Bonbon")
    cacao_percent: Optional[int] = Field(None, ge=0, le=100, description="Cocoa percentage")
    image: Optional[str] = Field(None, description="Image URL for display")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering/search")
    in_stock: bool = Field(True, description="Availability")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
