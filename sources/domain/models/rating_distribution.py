"""Rating distribution domain models."""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class RatingPoint(BaseModel):
    """A single data point in the rating distribution."""
    timestamp: int = Field(..., description="Unix timestamp when the problem was solved")
    rating: int = Field(..., description="Problem rating that was solved")
    problem_name: str = Field(..., description="Name of the solved problem")

    @property
    def date(self) -> datetime:
        """Convert timestamp to datetime object."""
        return datetime.fromtimestamp(self.timestamp)


class RatingDistribution(BaseModel):
    """Rating distribution over time for a user."""
    handle: str = Field(..., description="Codeforces handle")
    rating_points: List[RatingPoint] = Field(..., description="List of solved problems with timestamps and ratings")
    max_rating_achieved: int = Field(..., description="Highest rating problem solved so far")
    total_solved: int = Field(..., description="Total number of problems solved")
    rating_growth_periods: List[str] = Field(default_factory=list, description="Periods where significant rating growth occurred")

    def get_rating_points_sorted_by_time(self) -> List[RatingPoint]:
        """Get rating points sorted by timestamp."""
        return sorted(self.rating_points, key=lambda x: x.timestamp)