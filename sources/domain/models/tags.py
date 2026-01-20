"""Tags domain models."""

from typing import List
from pydantic import BaseModel, Field


class TagInfo(BaseModel):
    """Information about a single tag."""

    tag: str = Field(..., description="The tag name")
    average_rating: float = Field(
        ..., description="Average rating of all solved problems with this tag"
    )
    problem_count: int = Field(..., description="Number of solved problems with this tag")
    problems: List[str] = Field(..., description="Names of solved problems with this tag")


class TagsAnalysis(BaseModel):
    """Analysis of user's problem-solving activity by tags."""

    handle: str = Field(..., description="Codeforces handle")
    tags: List[TagInfo] = Field(..., description="List of tags analysis")
    overall_average_rating: float = Field(
        ..., description="Overall average rating of all solved problems"
    )
    total_solved: int = Field(..., description="Total number of problems solved")

    def get_weak_tags(self, threshold_diff: int = 200) -> List[TagInfo]:
        """
        Get tags where average rating is significantly lower than overall average.

        Args:
            threshold_diff: Minimum rating difference to consider a tag "weak"

        Returns:
            List of tags with average rating significantly below overall average
        """
        if not self.tags or self.total_solved == 0:
            return []

        weak_tags = []
        for tag_info in self.tags:
            if self.overall_average_rating - tag_info.average_rating >= threshold_diff:
                weak_tags.append(tag_info)

        # Sort by how much lower the average is
        weak_tags.sort(key=lambda x: self.overall_average_rating - x.average_rating, reverse=True)
        return weak_tags
