# ZergoQRF Scalability Architecture Plan

This document outlines the comprehensive scalability architecture for the ZergoQRF platform, designed to support two distinct milestones: 100 concurrent users and 2000 concurrent users.

## 1. Architecture for 100 Concurrent Users

This architecture is designed for initial launch and validation, prioritizing simplicity, cost-effectiveness, and rapid development while being capable of handling up to 100 concurrent users during peak hours.

### 1.1. Backend Architecture (FastAPI)

- **Approach**: **Monolith**. A single FastAPI application is sufficient and simplifies development, deployment, and maintenance at this scale.
- **Database (Supabase/PostgreSQL)**:
  - **Connection Pooling**: Use the default Supabase connection pooler (PgBouncer). The default configuration is adequate.
  - **Instance Size**: A small to medium-sized Supabase instance is sufficient.
- **Caching**:
  - **Strategy**: Use an in-memory cache within the FastAPI application (e.g., `fastapi-cache2` with an in-memory backend) for frequently accessed, non-critical data like restaurant menus.
- **API Rate Limiting**: Implement basic rate limiting using a middleware in FastAPI (e.g., `slowapi`) to prevent abuse.

### 1.2. Message Queue & Real-time Communication

- **Real-time**: Leverage **Supabase Realtime** for order updates. It's built-in, easy to use, and can handle this load.
- **Background Tasks**: Use FastAPI's `BackgroundTasks` for simple, non-critical tasks like sending emails/OTP.

### 1.3. Deployment & Infrastructure

- **Deployment**: Deploy the FastAPI backend as a single container on a PaaS like **Render or Railway**. These platforms offer simple "git push to deploy" workflows.
- **Scaling**: Vertical scaling (upgrading the instance size) is the primary method. A single container instance should be sufficient.
- **Database**: Use the managed Supabase service.
- **CDN**: Use Supabase's built-in CDN for media files.

### 1.4. Frontend Architecture (Flutter)

- **State Management**: `GetX` is suitable. For real-time updates, listen to Supabase Realtime channels and update the GetX controllers.
- **Offline Support**: Basic caching of menu data on the device. No complex synchronization needed at this stage.

---

## 2. Architecture for 2000 Concurrent Users

This architecture is designed for scale, focusing on performance, reliability, and maintainability.

### 2.1. Backend Architecture (FastAPI)

- **Approach**: **Microservices or Service-Based Architecture**. The monolith should be broken down into smaller, independent services. Suggested services:
  - `Auth Service`: Manages user authentication, OTP, and sessions.
  - `Restaurant Service`: Manages restaurant data, menus, and tables.
  - `Order Service`: Manages the order lifecycle.
  - `Notification Service`: Manages real-time and push notifications.
- **Database (Supabase/PostgreSQL)**:
  - **Connection Pooling**: Continue using PgBouncer, but monitor pool size and adjust if necessary.
  - **Read Replicas**: Introduce one or more read replicas for read-heavy operations (e.g., fetching menus). Direct read queries to replicas from the services.
  - **Partitioning**: For the `orders` table, consider partitioning by `restaurant_id` or a date range (`created_at`) to improve query performance.
- **Caching (Redis)**:
  - **Strategy**: Introduce an external Redis instance.
  - **Use Cases**:
    - Cache frequently read data (menus, restaurant settings).
    - Session storage.
    - Rate limiting counters.
  - **Invalidation**: Use a cache-aside pattern with a TTL. For data that changes, use an event-driven approach to invalidate the cache (e.g., when a menu is updated, publish an event to a queue that a worker consumes to invalidate the cache).
- **API Rate Limiting**: Use a more robust implementation with Redis to share rate limit state across multiple service instances.

### 2.2. Message Queue & Real-time Communication

- **Queue System**: Use **RabbitMQ or Redis Pub/Sub**. RabbitMQ is more robust for critical tasks.
  - **Use Cases**: Decouple services. When an order is created, the `Order Service` publishes an event, and other services (like `Notification Service`) subscribe to it.
- **Real-time Communication**:
  - **WebSockets**: For 2000 concurrent users, managing WebSocket connections directly can be complex. A dedicated service or a third-party solution like **Pusher** or **Ably** is recommended to offload this. Supabase Realtime might still be viable but should be load-tested.
- **Background Tasks**: Use **Celery** with RabbitMQ or Redis as a broker for all asynchronous tasks (OTP, notifications, processing uploads). This provides retries and better monitoring.

### 2.3. Deployment & Infrastructure

- **Container Orchestration**: **Docker + Kubernetes (K8s)** or a managed K8s service (EKS, GKE, AKS). This is necessary for managing microservices.
- **Auto-scaling**: Configure Horizontal Pod Autoscalers (HPA) in K8s based on CPU and memory usage to automatically scale service replicas.
- **Load Balancing**: Use a K8s Ingress Controller (like NGINX or Traefik) with a cloud load balancer to distribute traffic.
- **Database**: For production, consider a managed PostgreSQL service like Amazon RDS or Google Cloud SQL for better control over backups, scaling, and monitoring, in addition to Supabase for its BaaS features.
- **CDN**: Use a global CDN like **Cloudflare or AWS CloudFront** for all static assets, including the Flutter web app bundle.
- **Monitoring**: Use **Prometheus and Grafana** for monitoring metrics from K8s and applications. Use a structured logging solution like the **ELK stack** (Elasticsearch, Logstash, Kibana) or **Loki**.

### 2.4. Frontend Architecture (Flutter)

- **State Management**: `GetX` is still fine, but ensure controllers are well-scoped to features to avoid performance issues. For complex, shared state, consider more structured solutions like `Riverpod`.
- **Offline Support**: Implement a more robust offline strategy. Use a local database (like `Isar` or `Drift`) on the device to store data. Implement a synchronization mechanism to sync local changes with the backend when the device is online.

### 2.5. Performance & Reliability

- **Database Query Optimization**: Regularly analyze slow queries. Ensure all foreign keys and frequently queried columns are indexed.
- **Circuit Breaker**: Implement circuit breaker patterns (e.g., using a library like `pybreaker`) in service-to-service communication to prevent cascading failures.
- **Disaster Recovery**:
  - Regular, automated database backups.
  - Deploy services across multiple availability zones (AZs).
  - Have a documented plan for restoring from backups.

---

## 3. Key Differences: 100 vs 2000 Concurrent Users

| Feature              | 100 Concurrent Users      | 2000 Concurrent Users                                              | Why it Changes                                                                                                                   |
| -------------------- | ------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| **Backend**          | Monolith                  | Microservices                                                      | Monoliths become hard to scale and maintain. Microservices allow independent scaling and development.                            |
| **Database**         | Single DB instance        | DB with Read Replicas & Partitioning                               | A single DB becomes a bottleneck. Replicas distribute read load. Partitioning improves query speed on large tables.              |
| **Caching**          | In-memory (inside app)    | External (Redis)                                                   | In-memory cache is not shared across multiple app instances. Redis provides a shared, scalable cache.                            |
| **Real-time**        | Supabase Realtime         | Dedicated WebSocket service (e.g., Pusher) or self-hosted solution | Supabase Realtime may hit connection limits. A dedicated service is built for high concurrency.                                  |
| **Background Tasks** | FastAPI `BackgroundTasks` | Celery + RabbitMQ/Redis                                            | `BackgroundTasks` are simple but offer no retries or persistence. Celery is a robust, production-grade task queue.               |
| **Deployment**       | PaaS (Render/Railway)     | Kubernetes (K8s)                                                   | PaaS is simple but less flexible. K8s is complex but provides powerful orchestration, scaling, and resilience for microservices. |
| **Scaling**          | Vertical (bigger server)  | Horizontal (more servers/pods)                                     | Vertical scaling has limits and causes downtime. Horizontal scaling is more resilient and scalable.                              |
| **Monitoring**       | Basic PaaS logging        | Prometheus, Grafana, ELK/Loki                                      | At scale, you need a comprehensive observability stack to understand system behavior and diagnose issues.                        |
| **Offline Sync**     | Basic caching             | Local DB with sync logic                                           | With more users, the expectation for a seamless experience (even with spotty internet) increases.                                |

## 4. Phased Implementation Plan (From 100 to 2000 users)

1.  **Phase 1 (0-100 users)**: Build with the 100-user architecture. Focus on delivering features and validating the product.
2.  **Phase 2 (100-500 users)**:
    - Introduce **Redis** for caching.
    - Move background tasks to **Celery**.
    - Begin containerizing the application with **Docker** and deploy to a more robust PaaS or a simple K8s setup.
    - Set up basic monitoring with tools like **Sentry** for error tracking.
3.  **Phase 3 (500-1000 users)**:
    - Start breaking the monolith into the most critical microservices (e.g., `Orders` and `Notifications`).
    - Set up a **Kubernetes** cluster.
    - Introduce **database read replicas**.
4.  **Phase 4 (1000-2000+ users)**:
    - Complete the transition to microservices.
    - Implement advanced K8s features like auto-scaling (HPA).
    - Implement a robust **CI/CD pipeline** for automated testing and deployment of services.
    - Implement a full observability stack (Prometheus, Grafana, etc.).
    - Consider database partitioning.
    - Load test the system at each phase to identify bottlenecks before they affect users.
