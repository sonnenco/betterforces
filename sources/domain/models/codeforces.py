"""Codeforces API domain models."""

from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class SubmissionStatus(str, Enum):
    """Submission status enumeration."""

    OK = "OK"  # Accepted
    WRONG_ANSWER = "WRONG_ANSWER"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    IDLENESS_LIMIT_EXCEEDED = "IDLENESS_LIMIT_EXCEEDED"


class Problem(BaseModel):
    """Codeforces problem model."""

    contest_id: int
    index: str
    name: str
    rating: Optional[int] = None
    tags: List[str] = []

    @property
    def problem_key(self) -> str:
        """Unique identifier for a problem."""
        return f"{self.contest_id}{self.index}"


class Submission(BaseModel):
    """Codeforces submission model."""

    id: int
    contest_id: int
    creation_time_seconds: int
    problem: Problem
    verdict: SubmissionStatus
    programming_language: str

    @property
    def is_solved(self) -> bool:
        """Check if the submission was accepted."""
        return self.verdict == SubmissionStatus.OK
