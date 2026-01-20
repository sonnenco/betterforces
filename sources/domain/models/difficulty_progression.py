"""Difficulty progression domain models."""

from typing import List
from pydantic import BaseModel, Field
from datetime import datetime


class DifficultyPoint(BaseModel):
    """A data point showing average difficulty at a specific time period."""

    date_month: str = Field(..., description="Month in YYYY-MM format")
    date_quarter: str = Field(..., description="Quarter in YYYY-Q format")
    average_rating: float = Field(
        ..., description="Average rating of problems solved in this period"
    )
    problem_count: int = Field(..., description="Number of problems solved in this period")
    period_start: datetime = Field(..., description="Start timestamp of this period")
    period_end: datetime = Field(..., description="End timestamp of this period")


class GrowthRate(BaseModel):
    """Growth rate calculation between two periods."""

    from_period: str = Field(..., description="From period (YYYY-MM or YYYY-Q)")
    to_period: str = Field(..., description="To period (YYYY-MM or YYYY-Q)")
    rating_change: float = Field(..., description="Change in average rating")
    monthly_growth: float = Field(..., description="Average monthly growth rate")
    months_difference: int = Field(..., description="Number of months between periods")


class DifficultyProgression(BaseModel):
    """Analysis of user's difficulty progression over time."""

    handle: str = Field(..., description="Codeforces handle")
    monthly_progression: List[DifficultyPoint] = Field(
        ..., description="Monthly difficulty progression data"
    )
    quarterly_progression: List[DifficultyPoint] = Field(
        ..., description="Quarterly difficulty progression data"
    )
    growth_rates: List[GrowthRate] = Field(
        ..., description="Calculated growth rates between periods"
    )
    total_solved: int = Field(..., description="Total number of problems solved")
    periods_analyzed: int = Field(..., description="Number of time periods analyzed")
    first_solve_date: datetime = Field(..., description="Date of first problem solved")
    latest_solve_date: datetime = Field(..., description="Date of most recent problem solved")
