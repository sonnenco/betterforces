"""Rating distribution API routes."""

from datetime import datetime

from litestar import Controller, get
from litestar.response import Response
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.pagination import OffsetPagination
from litestar.params import Parameter
from typing import Optional

from sources.api.deps import (
    codeforces_data_service_dependency,
    rating_distribution_service_dependency,
)
from sources.api.schemas.rating_distribution import RatingPointSchema
from sources.services.codeforces_data_service import CodeforcesDataService
from sources.domain.services.rating_distribution_service import RatingDistributionService
from sources.infrastructure.codeforces_client import CodeforcesAPIError


class RatingDistributionController(Controller):
    """Controller for rating distribution endpoints."""

    path = "/rating-distribution"
    tags = ["Rating Distribution"]

    @get(
        path="/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "rating_service": rating_distribution_service_dependency,
        },
    )
    async def get_rating_distribution(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        rating_service: RatingDistributionService,
        limit: int = Parameter(
            default=100, ge=1, le=1000, description="Maximum number of items to return"
        ),
        offset: int = Parameter(default=0, ge=0, description="Number of items to skip"),
        start_date: Optional[datetime] = Parameter(
            default=None,
            description="Start date/time (inclusive) - only return problems solved on or after this date. Format: ISO 8601 (e.g., 2024-01-01 or 2024-01-01T12:00:00)",
        ),
        end_date: Optional[datetime] = Parameter(
            default=None,
            description="End date/time (inclusive) - only return problems solved on or before this date. Format: ISO 8601 (e.g., 2024-12-31 or 2024-12-31T23:59:59)",
        ),
    ) -> OffsetPagination[RatingPointSchema]:
        """
        Get user's solved problems rated by time with pagination.
        Returns chronological progression of problem rating difficulties solved.
        Supports optional date range filtering.

        Args:
            handle: Codeforces handle
            limit: Maximum number of items per page (1-1000, default 100)
            offset: Number of items to skip (default 0)
            start_date: Optional start date (inclusive) - filter problems solved on or after this date
            end_date: Optional end date (inclusive) - filter problems solved on or before this date

        Returns:
            Paginated list of rating points with metadata
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

            # Analyze rating distribution
            distribution = rating_service.analyze_rating_distribution(handle, submissions)

            # Convert to response schema
            rating_points = [
                RatingPointSchema(
                    timestamp=point.timestamp,
                    rating=point.rating,
                    problem_name=point.problem_name,
                    date=point.date.strftime("%Y-%m-%d"),
                )
                for point in distribution.rating_points
            ]

            # Sort by timestamp to ensure chronological order
            rating_points.sort(key=lambda x: x.timestamp)

            # Apply date range filtering
            if start_date is not None:
                start_timestamp = int(start_date.timestamp())
                rating_points = [p for p in rating_points if p.timestamp >= start_timestamp]

            if end_date is not None:
                end_timestamp = int(end_date.timestamp())
                rating_points = [p for p in rating_points if p.timestamp <= end_timestamp]

            # Calculate pagination
            total = len(rating_points)
            paginated_items = rating_points[offset : offset + limit]

            return Response(
                OffsetPagination[RatingPointSchema](
                    items=paginated_items, limit=limit, offset=offset, total=total
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
