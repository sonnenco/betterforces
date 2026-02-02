# API Reference

All endpoints accept a Codeforces handle as a path parameter and return JSON analytics.

## Base URL

- Local development: `http://localhost:8000/api`
- Production: `https://betterforces.deyna.xyz/api`

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/difficulty-distribution/{handle}` | Distribution of solved problems by rating |
| `GET` | `/tag-ratings/{handle}` | Tag statistics (average/median rating) |
| `GET` | `/tag-ratings/{handle}/weak` | Weak topics (with `?threshold=200` parameter) |
| `GET` | `/abandoned-problems/by-tags/{handle}` | Abandoned problems grouped by tags |
| `GET` | `/abandoned-problems/by-ratings/{handle}` | Abandoned problems grouped by rating |

## Response Examples

### Difficulty Distribution

```bash
GET /difficulty-distribution/tourist
```

```json
{
  "ranges": [
    {"rating": 800, "problem_count": 42},
    {"rating": 900, "problem_count": 38},
    {"rating": 1000, "problem_count": 45}
  ],
  "total_solved": 3157,
  "last_updated": "2026-01-30T12:34:56"
}
```

### Tag Statistics

```bash
GET /tag-ratings/tourist
```

```json
{
  "tags": [
    {"tag": "dp", "average_rating": 2150.5, "median_rating": 2100, "problem_count": 156},
    {"tag": "graphs", "average_rating": 2080.3, "median_rating": 2000, "problem_count": 142}
  ],
  "overall_average_rating": 1980.5,
  "overall_median_rating": 1900,
  "total_solved": 3157,
  "last_updated": "2026-01-30T12:34:56"
}
```

### Weak Topics

```bash
GET /tag-ratings/tourist/weak?threshold=200
```

```json
{
  "weak_tags": [
    {"tag": "geometry", "average_rating": 1650.0, "median_rating": 1600, "problem_count": 23}
  ],
  "overall_average_rating": 1980.5,
  "overall_median_rating": 1900,
  "total_solved": 3157,
  "threshold_used": 200,
  "last_updated": "2026-01-30T12:34:56"
}
```

### Abandoned Problems by Tags

```bash
GET /abandoned-problems/by-tags/tourist
```

```json
{
  "tags": [
    {"tag": "dp", "problem_count": 5, "total_failed_attempts": 18},
    {"tag": "trees", "problem_count": 3, "total_failed_attempts": 12}
  ],
  "total_abandoned_problems": 23,
  "last_updated": "2026-01-30T12:34:56"
}
```

### Abandoned Problems by Rating

```bash
GET /abandoned-problems/by-ratings/tourist
```

```json
{
  "ratings": [
    {"rating": 2400, "problem_count": 8, "total_failed_attempts": 31},
    {"rating": 2600, "problem_count": 5, "total_failed_attempts": 22}
  ],
  "total_abandoned_problems": 23,
  "last_updated": "2026-01-30T12:34:56"
}
```

## Interactive API Documentation

Full interactive documentation with request/response schemas is available at:

- Swagger UI: `http://localhost:8000/schema/swagger`
- ReDoc: `http://localhost:8000/schema/redoc`
- OpenAPI JSON: `http://localhost:8000/schema/openapi.json`
