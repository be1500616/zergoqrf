# Load Testing Plan: 2000 User Simulation

This document outlines the plan for preparing and executing a 2000-user load test to identify and address potential bottlenecks in the system.

## Phase 1: Environment Setup & Tooling

### 1.1. Dedicated Load Testing Environment

To avoid impacting the production environment, we will set up a dedicated environment for load testing. This environment should be as close to a mirror of production as possible, including:

*   **Infrastructure:** A separate Supabase project and a cloud hosting environment (e.g., Railway, Render) with similar specifications to production.
*   **Data:** A sanitized and anonymized snapshot of the production database to ensure realistic test scenarios.
*   **Configuration:** The same environment variables and service configurations as production.

### 1.2. Load Testing Tool Selection

We will use a modern, open-source load testing tool to simulate user traffic. The primary candidates are:

*   **Locust:** A Python-based tool that allows you to write tests in code, making it highly customizable and developer-friendly.
*   **k6:** A Go-based tool with a JavaScript scripting API, known for its high performance and ease of use.

The selected tool will be configured to simulate a realistic user scenario, including browsing the menu, adding items to the cart, and placing orders.

## Phase 2: Backend Optimization

### 2.1. Caching with Redis

To reduce the load on the database and improve response times, we will implement a caching layer with Redis. This will involve:

*   **Identifying Cacheable Data:** We will analyze the application's data access patterns to identify frequently read, non-critical data that is suitable for caching (e.g., menu items, restaurant details).
*   **Implementing a Caching Strategy:** We will implement a cache-aside strategy to ensure that the cache is updated appropriately when the underlying data changes.
*   **Configuring Redis:** We will configure Redis with an appropriate eviction policy and memory limit to ensure optimal performance.

### 2.2. Database Optimization

We will analyze and optimize the database to ensure it can handle the increased load. This will include:

#### 2.1.1. Implementation Steps

1.  **Add Redis Dependency:** Add `redis` to the `[tool.poetry.dependencies]` section of `apps/backend/pyproject.toml`.
2.  **Update Configuration:** Add a `redis_url` setting to the `Settings` class in `apps/backend/app/core/config.py`.
3.  **Create Redis Client:** Create a new file, `apps/backend/app/core/redis_client.py`, to initialize and manage the Redis connection pool.
4.  **Implement Caching Decorator:** Create a file, `apps/backend/app/common/caching.py`, with a decorator that:
    *   Accepts a `ttl` (time-to-live) argument.
    *   Generates a cache key based on the function name and arguments.
    *   Checks for the key in Redis. If found, it deserializes the JSON data and returns it.
    *   If not found, it calls the original function, serializes the result to JSON, and stores it in Redis with the specified TTL.
5.  **Apply to Endpoint:** Apply the decorator to the `get_restaurant_by_code` function in `apps/backend/app/features/restaurants/presentation/restaurant_router.py`.

*   **Query Analysis:** We will use `EXPLAIN ANALYZE` to identify slow-running queries and optimize them.
*   **Indexing:** We will add indexes to frequently queried columns to improve query performance.
*   **Connection Pooling:** We will configure a connection pooler (e.g., PgBouncer) to efficiently manage database connections and prevent exhaustion.

### 2.3. Horizontal Scaling
#### 2.2.1. Implementation Steps

1.  **Identify Slow Queries:** Use the `pg_stat_statements` extension in Supabase to identify the most time-consuming queries.
2.  **Analyze Query Plans:** For each slow query, use `EXPLAIN ANALYZE` to understand its execution plan and identify bottlenecks.
3.  **Add Indexes:** Based on the query analysis, add indexes to frequently queried columns. Focus on columns used in `WHERE` clauses, `JOIN` conditions, and `ORDER BY` clauses.
4.  **Configure Connection Pooling:**
    *   Enable the Supabase connection pooler (PgBouncer) for your project.
    *   Update your `database_url` in `.env` to use the connection pooler URL.
    *   Configure the pool size and mode (`session` or `transaction`) based on your application's needs.


To handle the increased number of requests, we will configure the FastAPI application to scale horizontally. This will involve:

#### 2.3.1. Implementation Steps

1.  **Update Docker Compose:** Modify your `docker-compose.yml` to use a production-ready ASGI server like Gunicorn or Uvicorn with multiple workers.
2.  **Configure a Load Balancer:** Use a load balancer (e.g., Nginx, Traefik, or a cloud provider's load balancer) to distribute traffic across multiple instances of your backend container.
3.  **Implement a Health Check Endpoint:** Create a simple `/health` endpoint in your FastAPI application that the load balancer can use to determine if an instance is healthy.
4.  **Configure Autoscaling:** If you're deploying to a cloud provider, configure autoscaling to automatically adjust the number of backend instances based on CPU utilization or other metrics.

*   **Containerization:** Ensuring the application is properly containerized with Docker.
*   **Load Balancing:** Setting up a load balancer to distribute traffic across multiple instances of the application.
*   **Autoscaling:** Configuring autoscaling to automatically adjust the number of instances based on traffic.

## Phase 3: Supabase Configuration

#### 3.1.1. Plan Selection

1.  **Analyze Current Usage:** Review your Supabase project's current resource utilization (CPU, memory, I/O) to establish a baseline.
2.  **Estimate Load Test Requirements:** Based on the 2000-user test scenario, estimate the required database and authentication capacity.
3.  **Select Appropriate Plan:** Choose a Supabase plan that provides sufficient resources for the load test. Consider a plan with dedicated resources to ensure consistent performance.

#### 3.2.1. RLS Policy Optimization

1.  **Identify Performance-Critical Policies:** Review the RLS policies on your most frequently accessed tables (e.g., `restaurants`, `menu_items`, `orders`).
2.  **Benchmark Policy Performance:** Use `EXPLAIN ANALYZE` to measure the performance overhead of your RLS policies.
3.  **Refactor Complex Policies:**
    *   Replace complex joins in RLS policies with `SECURITY DEFINER` functions to improve performance.
    *   Cache frequently accessed, non-sensitive data in a separate, less restrictive table.
    *   Denormalize data where appropriate to avoid complex joins.

### 3.1. Plan Review

We will review the current Supabase plan to ensure it can handle the anticipated load. If necessary, we will upgrade to a higher-tier plan with more resources.

### 3.2. RLS Policy Optimization

We will analyze the existing Row Level Security (RLS) policies to ensure they are as efficient as possible. This will involve:

*   **Simplifying Policies:** Refactoring complex policies to reduce their overhead.
*   **Using Functions:** Moving complex logic into database functions to improve performance.

## Phase 4: Frontend & CDN

### 4.1. CDN for Static Assets

To reduce the load on the web server and improve frontend performance, we will configure a Content Delivery Network (CDN) to serve static assets (e.g., images, CSS, JavaScript).

## Phase 5: Monitoring & Analysis

### 5.1. Centralized Logging and Monitoring

To effectively monitor the system during the load test, we will set up a centralized logging and monitoring solution. This will involve:

*   **Log Aggregation:** Configuring a log aggregation tool (e.g., Grafana Loki, Datadog) to collect logs from all services.
*   **Metrics Collection:** Using a monitoring tool (e.g., Prometheus, Grafana) to collect and visualize key performance metrics (e.g., CPU, memory, response times).
*   **Dashboarding:** Creating dashboards to visualize the health of the system in real-time.

## Phase 6: Execution & Reporting

### 6.1. Test Scenario Definition

We will define a realistic load test scenario that simulates the behavior of 2000 concurrent users. This will include:

*   **User Journeys:** Defining the specific actions that users will take (e.g., browsing the menu, adding items to the cart, placing an order).
*   **Think Time:** Adding realistic delays between actions to simulate human behavior.
*   **Ramp-Up Period:** Gradually increasing the number of users to identify the point at which the system starts to degrade.

### 6.2. Test Execution and Analysis

We will execute the load test and collect the results. This will involve:

*   **Running the Test:** Executing the load test script against the dedicated testing environment.
*   **Monitoring the System:** Closely monitoring the system's health and performance during the test.
*   **Analyzing the Results:** Analyzing the test results to identify bottlenecks and areas for improvement.

### 6.3. Final Report

We will create a final report that summarizes the findings of the load test. This will include:

*   **Executive Summary:** A high-level overview of the test results and recommendations.
*   **Detailed Findings:** A detailed breakdown of the test results, including performance metrics and identified bottlenecks.
*   **Recommendations:** A list of specific, actionable recommendations for improving the system's performance and scalability.
