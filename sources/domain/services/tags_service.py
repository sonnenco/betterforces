"""Tags analysis service for analyzing solved problems by tags."""

from typing import List
from collections import defaultdict
from statistics import mean

from sources.domain.models.codeforces import Submission
from sources.domain.models.tags import TagsAnalysis, TagInfo


class TagsService:
    """Service for generating tags analytics."""

    @staticmethod
    def analyze_tags(handle: str, submissions: List[Submission]) -> TagsAnalysis:
        """
        Analyze user's solved problems and generate tags statistics.

        Args:
            handle: Codeforces handle
            submissions: List of user's submissions

        Returns:
            TagsAnalysis with analyzed data
        """
        # Filter successful submissions
        successful_submissions = [s for s in submissions if s.is_solved]

        if not successful_submissions:
            return TagsAnalysis(handle=handle, tags=[], overall_average_rating=0, total_solved=0)

        # Remove duplicate problems (keep first solve)
        unique_solves = TagsService._deduplicate_problems(successful_submissions)

        # Group problems by tags and calculate statistics
        tags_data, overall_ratings = TagsService._analyze_tags(unique_solves)

        # Calculate overall average rating
        overall_average = mean(overall_ratings) if overall_ratings else 0

        # Convert to TagInfo objects
        tags_info = []
        for tag, (tag_ratings, problems) in tags_data.items():
            if tag_ratings:  # Only include tags with rated problems
                avg_rating = mean(tag_ratings)
                tag_info = TagInfo(
                    tag=tag,
                    average_rating=round(avg_rating, 1),
                    problem_count=len(tag_ratings),
                    problems=sorted(problems),
                )
                tags_info.append(tag_info)

        # Sort tags by problem count (most solved first)
        tags_info.sort(key=lambda x: x.problem_count, reverse=True)

        return TagsAnalysis(
            handle=handle,
            tags=tags_info,
            overall_average_rating=round(overall_average, 1),
            total_solved=len(unique_solves),
        )

    @staticmethod
    def _deduplicate_problems(submissions: List[Submission]) -> List[Submission]:
        """Remove duplicate problem solves, keeping only the first solution."""
        seen_problems = set()
        unique_submissions = []

        # Sort by time to ensure earliest solves come first
        sorted_submissions = sorted(submissions, key=lambda s: s.creation_time_seconds)

        for submission in sorted_submissions:
            problem_key = submission.problem.problem_key
            if problem_key not in seen_problems:
                seen_problems.add(problem_key)
                unique_submissions.append(submission)

        return unique_submissions

    @staticmethod
    def _analyze_tags(submissions):
        tags_data = defaultdict(lambda: ([], []))
        overall_ratings = []

        for submission in submissions:
            problem = submission.problem

            if problem.rating is None:
                continue

            overall_ratings.append(problem.rating)

            for tag in problem.tags:
                tags_data[tag][0].append(problem.rating)
                tags_data[tag][1].append(problem.name)

        return (tags_data, overall_ratings)
