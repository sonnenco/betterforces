"""Tags API schemas."""

from typing import List
from pydantic import BaseModel, Field
from datetime import datetime


class SimpleTagInfoSchema(BaseModel):
    """Schema for a single tag information (simplified version)."""

    tag: str = Field(..., description="The tag name")
    average_rating: float = Field(
        ..., description="Average rating of all solved problems with this tag"
    )
    problem_count: int = Field(..., description="Number of solved problems with this tag")

    class Config:
        from_attributes = True


class TagInfoSchema(SimpleTagInfoSchema):
    """Schema for a single tag information (detailed version for weak tags)."""

    problems: List[str] = Field(..., description="Names of solved problems with this tag")


class TagsResponse(BaseModel):
    """Response schema for tags analysis."""

    tags: List[SimpleTagInfoSchema] = Field(..., description="List of tags analysis")
    overall_average_rating: float = Field(
        ..., description="Overall average rating of all solved problems"
    )
    total_solved: int = Field(..., description="Total number of problems solved")
    last_updated: datetime = Field(..., description="Timestamp when data was last fetched")

    class Config:
        from_attributes = True


class WeakTagsResponse(BaseModel):
    """Response schema for weak tags analysis."""

    weak_tags: List[SimpleTagInfoSchema] = Field(
        ..., description="List of weak tags (significantly lower average rating)"
    )
    overall_average_rating: float = Field(
        ..., description="Overall average rating of all solved problems"
    )
    total_solved: int = Field(..., description="Total number of problems solved")
    threshold_used: int = Field(
        ..., description="Rating difference threshold used to identify weak tags"
    )
    last_updated: datetime = Field(..., description="Timestamp when data was last fetched")

    class Config:
        from_attributes = True
