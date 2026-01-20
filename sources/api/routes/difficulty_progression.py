"""Difficulty progression API routes."""

from datetime import datetime, timezone
from typing import Optional

from litestar import Controller, get
from litestar.response import Response
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from sources.api.deps import (
    codeforces_data_service_dependency,
    difficulty_progression_service_dependency,
)
from sources.api.schemas.difficulty_progression import (
    DifficultyProgressionResponse,
    DifficultyPointSchema,
    GrowthRateSchema,
)
from sources.services.codeforces_data_service import CodeforcesDataService
from sources.domain.services.difficulty_progression_service import DifficultyProgressionService
from sources.infrastructure.codeforces_client import CodeforcesAPIError


class DifficultyProgressionController(Controller):
    """Controller for difficulty progression endpoints."""

    path = "/difficulty-progression"
    tags = ["Difficulty Progression"]

    @get(
        path="/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "progression_service": difficulty_progression_service_dependency,
        },
    )
    async def get_difficulty_progression(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        progression_service: DifficultyProgressionService,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Response[DifficultyProgressionResponse]:
        """
        Get user's difficulty progression over time.

        Analyzes how problem difficulty has evolved for the user within the specified date range,
        showing monthly and quarterly progression with growth rates.

        Args:
            handle: Codeforces handle
            start_date: Optional start date/time (inclusive) - only analyze problems solved on or after this date. Format: ISO 8601 (e.g., 2024-01-01 or 2024-01-01T12:00:00)
            end_date: Optional end date/time (inclusive) - only analyze problems solved on or before this date. Format: ISO 8601 (e.g., 2024-12-31 or 2024-12-31T23:59:59)

        Returns:
            Difficulty progression analysis with growth metrics for the specified period
        """
        try:
            # Fetch user submissions
            submissions = await data_service.get_user_submissions(handle)

            if not submissions:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail=f"No submissions found for user '{handle}'",
                    extra={"handle": handle},
                )

            # Filter submissions by date range before analysis
            if start_date is not None:
                start_timestamp = int(start_date.timestamp())
                submissions = [s for s in submissions if s.creation_time_seconds >= start_timestamp]

            if end_date is not None:
                end_timestamp = int(end_date.timestamp())
                submissions = [s for s in submissions if s.creation_time_seconds <= end_timestamp]

            if not submissions:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail=f"No submissions found for user '{handle}' in the specified date range",
                    extra={"handle": handle, "start_date": start_date, "end_date": end_date},
                )

            # Analyze difficulty progression
            progression = progression_service.analyze_difficulty_progression(handle, submissions)

            # Convert domain model to API schema
            monthly_progression = [
                DifficultyPointSchema(
                    date_month=point.date_month,
                    date_quarter=point.date_quarter,
                    average_rating=point.average_rating,
                    problem_count=point.problem_count,
                    period_start=point.period_start,
                    period_end=point.period_end,
                )
                for point in progression.monthly_progression
            ]

            quarterly_progression = [
                DifficultyPointSchema(
                    date_month=point.date_month,
                    date_quarter=point.date_quarter,
                    average_rating=point.average_rating,
                    problem_count=point.problem_count,
                    period_start=point.period_start,
                    period_end=point.period_end,
                )
                for point in progression.quarterly_progression
            ]

            growth_rates = [
                GrowthRateSchema(
                    from_period=rate.from_period,
                    to_period=rate.to_period,
                    rating_change=rate.rating_change,
                    monthly_growth=rate.monthly_growth,
                    months_difference=rate.months_difference,
                )
                for rate in progression.growth_rates
            ]

            return Response(
                DifficultyProgressionResponse(
                    monthly_progression=monthly_progression,
                    quarterly_progression=quarterly_progression,
                    growth_rates=growth_rates,
                    total_solved=progression.total_solved,
                    periods_analyzed=progression.periods_analyzed,
                    first_solve_date=progression.first_solve_date,
                    latest_solve_date=progression.latest_solve_date,
                    last_updated=datetime.now(timezone.utc),
                ),
                headers={"Cache-Control": "public, max-age=14400"},  # 4 hours like our TTL
            )

        except CodeforcesAPIError as e:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch data from Codeforces API: {str(e)}",
                extra={"handle": handle, "error": str(e)},
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}",
                extra={"handle": handle, "error": str(e)},
            )
