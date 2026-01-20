"""Litestar application configuration."""

import logging

from litestar import Litestar
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.openapi import OpenAPIConfig
from litestar.stores.redis import RedisStore

from sources.api.routes import routes
from sources.config import settings


def create_app() -> Litestar:
    """Create and configure the Litestar application."""

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Configure stores (using RedisStore for production caching)
    stores = {
        "default": RedisStore.with_client(url=settings.redis_url),
        "rate_limit": RedisStore.with_client(url=settings.redis_url),
    }

    # Configure rate limiting
    rate_limit_config = RateLimitConfig(
        rate_limit=(settings.rate_limit_period, settings.rate_limit_requests),
        store="rate_limit",
        exclude=["/schema"],  # Exclude OpenAPI schema endpoint
    )

    return Litestar(
        route_handlers=routes,
        stores=stores,
        middleware=[rate_limit_config.middleware],
        openapi_config=OpenAPIConfig(
            title="BetterForces API",
            version="1.0.0",
            description="API for Codeforces profile analysis",
        ),
    )
