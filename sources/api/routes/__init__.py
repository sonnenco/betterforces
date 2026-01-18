"""API routes package."""

from litestar import Router

from sources.api.routes.rating_distribution import RatingDistributionController

routes = [
    RatingDistributionController,
]