# BetterForces

## Project Idea

API for analyzing Codeforces profiles that provides useful statistics for improving competitive programming skills.

## Goal

Help competitive programmers and their coaches:
- Identify weak spots in training
- Find knowledge gaps and shortcomings
- Determine strengths
- Track progress and development trends

## Core Features

### 1. Comfort Zone
Determines the range of problem ratings where the user feels confident:
- Finds problems with success rate > 80%
- Shows boundaries: lower and upper limits of comfortable range
- Helps understand when to move to more challenging problems

### 2. Solved Problems Velocity
Tracks activity and training pace:
- Number of solved problems in the last week
- Number of solved problems in the last month
- Trend: acceleration or deceleration of pace
- Activity graph by days/weeks

### 3. Difficulty Progression
Shows growth in the level of solved problems:
- Average rating of solved problems by periods (month, quarter)
- Graph of average problem rating changes over time
- Rate of difficulty growth (how much problem rating increases per month)

### 4. Problem Rating Distribution Over Time
Visualization of solved problems by rating over time:
- Graph distribution: X-axis - time, Y-axis - problem rating
- Shows how the "upper limit" of solved problems grows over time
- Helps identify periods of stagnation and rapid growth

### 5. Average Rating by Tag
For each tag (dp, graphs, greedy, math, etc.) calculates:
- Average rating of all solved problems with this tag
- Number of solved problems by tag
- Percentile relative to the overall average problem rating

### 6. Weak Tags Detection
Automatically identifies problematic topics:
- Finds tags where the average rating of solved problems is significantly lower (e.g., 200+ points) than the overall average
- Ranks weak tags by degree of lag
- Shows how many problems were solved in weak topics (little practice or actually difficult)

## Technical Approach

RESTful API that receives data through the public Codeforces API and provides processed analytics.
