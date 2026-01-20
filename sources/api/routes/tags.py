"""Tags API routes."""

from datetime import datetime, timezone
from litestar import Controller, get
from litestar.response import Response
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.params import Parameter

from sources.api.deps import codeforces_data_service_dependency, tags_service_dependency
from sources.api.schemas.tags import TagsResponse, SimpleTagInfoSchema, WeakTagsResponse
from sources.services.codeforces_data_service import CodeforcesDataService
from sources.domain.services.tags_service import TagsService
from sources.infrastructure.codeforces_client import CodeforcesAPIError


class TagsController(Controller):
    """Controller for tags endpoints."""

    path = "/tags"
    tags = ["Tags"]

    @get(
        path="/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "tags_service": tags_service_dependency,
        },
    )
    async def get_tags(
        self, handle: str, data_service: CodeforcesDataService, tags_service: TagsService
    ) -> Response[TagsResponse]:
        """
        Get user's solved problems analyzed by tags.

        Returns statistics showing average rating for each tag and problem count.

        Args:
            handle: Codeforces handle

        Returns:
            Tags analysis with average ratings by tag
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

            # Analyze tags
            tags_analysis = tags_service.analyze_tags(handle, submissions)

            # Convert to response schema
            tags_info = [
                SimpleTagInfoSchema(
                    tag=tag.tag, average_rating=tag.average_rating, problem_count=tag.problem_count
                )
                for tag in tags_analysis.tags
            ]

            return Response(
                TagsResponse(
                    tags=tags_info,
                    overall_average_rating=tags_analysis.overall_average_rating,
                    total_solved=tags_analysis.total_solved,
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

    @get(
        path="/{handle:str}/weak",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "tags_service": tags_service_dependency,
        },
    )
    async def get_weak_tags(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        tags_service: TagsService,
        threshold: int = Parameter(
            default=200,
            ge=0,
            le=1000,
            description="Minimum rating difference to consider a tag 'weak'",
        ),
    ) -> Response[WeakTagsResponse]:
        """
        Get user's weak tags - topics where average rating is significantly lower.

        Returns tags that may need more practice based on rating threshold.

        Args:
            handle: Codeforces handle
            threshold: Minimum rating difference from overall average to be considered weak

        Returns:
            Weak tags analysis
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

            # Analyze tags
            tags_analysis = tags_service.analyze_tags(handle, submissions)

            # Get weak tags
            weak_tags = tags_analysis.get_weak_tags(threshold)

            # Convert to response schema
            weak_tags_info = [
                SimpleTagInfoSchema(
                    tag=tag.tag, average_rating=tag.average_rating, problem_count=tag.problem_count
                )
                for tag in weak_tags
            ]

            return Response(
                WeakTagsResponse(
                    weak_tags=weak_tags_info,
                    overall_average_rating=tags_analysis.overall_average_rating,
                    total_solved=tags_analysis.total_solved,
                    threshold_used=threshold,
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
