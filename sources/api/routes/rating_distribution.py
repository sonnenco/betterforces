"""Rating distribution API routes."""

from datetime import datetime
from typing import Dict, Any

from litestar import Controller, get
from litestar.response import Response
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from sources.api.deps import codeforces_data_service_dependency, rating_distribution_service_dependency
from sources.api.schemas.rating_distribution import RatingDistributionResponse, RatingPointSchema
from sources.api.schemas.common import ErrorResponse
from sources.services.codeforces_data_service import CodeforcesDataService
from sources.domain.services.rating_distribution_service import RatingDistributionService
from sources.infrastructure.codeforces_client import CodeforcesAPIError


class RatingDistributionController(Controller):
    """Controller for rating distribution endpoints."""

    path = "/rating-distribution"
    tags = ["Rating Distribution"]

    @get(path="/{handle:str}",
         dependencies={
             "data_service": codeforces_data_service_dependency,
             "rating_service": rating_distribution_service_dependency
         })
    async def get_rating_distribution(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        rating_service: RatingDistributionService
    ) -> RatingDistributionResponse:
        """
        Get user's solved problems rated by time.
        Returns chronological progression of problem rating difficulties solved.
        """
        try:
            # Fetch user submissions
            submissions = await data_service.get_user_submissions(handle)

            if not submissions:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail=f"No submissions found for user '{handle}'",
                    extra={"handle": handle}
                )

            # Analyze rating distribution
            distribution = rating_service.analyze_rating_distribution(handle, submissions)

            # Convert to response schema
            rating_points = [
                RatingPointSchema(
                    timestamp=point.timestamp,
                    rating=point.rating,
                    problem_name=point.problem_name,
                    date=point.date.strftime("%Y-%m-%d")
                )
                for point in distribution.rating_points
            ]

            return Response(
                RatingDistributionResponse(
                    handle=handle,
                    rating_points=rating_points,
                    last_updated=datetime.now()
                ),
                headers={"Cache-Control": "public, max-age=14400"}  # 4 hours like our TTL
            )

        except CodeforcesAPIError as e:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch data from Codeforces API: {str(e)}",
                extra={"handle": handle, "error": str(e)}
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}",
                extra={"handle": handle, "error": str(e)}
            )