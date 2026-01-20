"""API schemas package."""

from .difficulty_progression import (
    DifficultyProgressionResponse,
    DifficultyPointSchema,
    GrowthRateSchema,
)
from .rating_distribution import RatingDistributionResponse, RatingPointSchema
from .tags import TagsResponse, TagInfoSchema, WeakTagsResponse
from .common import APIResponse, ErrorResponse

__all__ = [
    "DifficultyProgressionResponse",
    "DifficultyPointSchema",
    "GrowthRateSchema",
    "RatingDistributionResponse",
    "RatingPointSchema",
    "TagsResponse",
    "TagInfoSchema",
    "WeakTagsResponse",
    "APIResponse",
    "ErrorResponse",
]
