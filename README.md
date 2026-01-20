# BetterForces

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![Litestar](https://img.shields.io/badge/Litestar-green?style=for-the-badge&logo=lightning)
![UV](https://img.shields.io/badge/UV-red?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensource)

## Project Idea

API for analyzing Codeforces profiles that provides useful statistics for improving competitive programming skills.

## Goal

Help competitive programmers and their coaches:
- Identify weak spots in training
- Find knowledge gaps and shortcomings
- Determine strengths
- Track progress and development trends

## Core Features

### 1. Difficulty Distribution
Analyzes the distribution of solved problems by difficulty levels:
- Groups solved problems into rating bins (800, 900, 1000, 1100, etc.)
- Shows the count of solved problems in each bin
- Helps understand problem-solving patterns across different difficulty ranges

### 2. Abandoned Problems Analysis
Identifies problems user attempted but never solved:
- Groups failed attempts by tags to find problematic topics
- Groups failed attempts by rating bins to identify difficulty thresholds
- Provides insights into knowledge gaps and areas needing more practice

### 3. Tag Ratings Analysis
For each problem tag (dp, graphs, greedy, math, etc.) provides:
- Average rating of all solved problems with this tag
- Median rating for robust performance assessment
- Number of solved problems by tag
- Relative performance compared to overall rating

### 4. Weak Tag Ratings Detection
Automatically identifies topics needing improvement:
- Finds tags where the median rating is significantly lower than overall median
- Ranks problematic topics by performance gap
- Shows practice volume in weak areas to guide training focus

## Technical Approach

RESTful API that receives data through the public Codeforces API and provides processed analytics.

## Architecture

- **Backend-only**: No frontend in this repository
- **Redis storage**: Used for rate limiting, no data persistence for MVP
- **On-demand data fetching**: Fetches fresh data from Codeforces API for each request
- **Clean Architecture**: Separated into layers (api/, domain/, infrastructure/, services/)

## Project Structure

```
betterforces/
├── sources/                      # All source code
│   ├── api/                      # API layer
│   │   ├── app.py                # Litestar application
│   │   ├── routes/               # Route handlers
│   │   ├── schemas/              # Pydantic schemas
│   │   └── deps.py               # Dependencies
│   ├── domain/                   # Business logic layer
│   │   ├── models/               # Data models
│   │   └── services/             # Business services
│   ├── infrastructure/           # Infrastructure layer
│   │   ├── codeforces_client.py  # Codeforces API client
│   │   └── redis_client.py       # Redis cache client
│   ├── services/                 # Application services
│   │   └── codeforces_data_service.py  # Data synchronization service
│   ├── config.py                 # Application configuration
│   └── main.py                   # Entry point
├── tests/                        # Unit and integration tests
├── pyproject.toml                # Python dependencies and project configuration
├── uv.lock                       # UV lock file
├── README.md                     # This file
└── LICENSE                       # License
```

## API Endpoints

Base URL: `/`

### Difficulty Distribution
- `GET /difficulty-distribution/{handle}` - Get problem distribution by difficulty levels (800, 900, 1000...), showing count of solved problems in each bin

### Abandoned Problems
- `GET /abandoned-problems/by-tags/{handle}` - Get analysis of problems user attempted but never solved, grouped by tags
- `GET /abandoned-problems/by-ratings/{handle}` - Get analysis of problems user attempted but never solved, grouped by rating bins

### Tag Ratings
- `GET /tag-ratings/{handle}` - Get average and median rating by problem tags, number of solved problems per tag
- `GET /tag-ratings/{handle}/weak` - Get weak tag ratings analysis with threshold-based filtering

**Response format**: JSON with analytics data and metadata
