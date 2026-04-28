# ZERGO QR - Deployment & Infrastructure Guide

## Overview
This guide provides step-by-step instructions for deploying the ZERGO QR system with scalability for 100 concurrent users, including all infrastructure components and monitoring setup.

---

## Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PRODUCTION STACK                     │
├─────────────────────────────────────────────────────────┤
│  Flutter Web/Mobile Apps (Cloudflare Pages/App Stores) │
│                          │                              │
│  ┌───────────────────────▼──────────────────────────┐   │
│  │         Load Balancer (Railway/Render)          │   │
│  └───────────────────────┬──────────────────────────┘   │
│                          │                              │
│  ┌───────────────────────▼──────────────────────────┐   │
│  │       FastAPI Instances (Auto-scaled 2-8)       │   │
│  └───────────┬─────────────────────────────┬────────┘   │
│              │                             │            │
│  ┌───────────▼────────┐         ┌──────────▼────────┐   │
│  │  Supabase PostgreSQL │         │   Redis Cache     │   │
│  │  (Multi-tenant RLS)  │         │   (Railway/Upstash) │   │
│  └─────────────────────┘         └───────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │         Background Services                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │ │
│  │  │   Celery    │  │   Flower    │  │ Monitoring  │ │ │
│  │  │  Workers    │  │ Dashboard   │  │ & Alerting  │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## PHASE 1: Environment Setup & Core Services

### Step 1: Supabase Database Setup
**Time: 30 minutes**

1. **Create Supabase Project**
   ```bash
   # Visit https://supabase.com/dashboard
   # Create new project: "zergoqr-production"  
   # Note down:
   # - Project URL
   # - Anon Key
   # - Service Role Key
   # - Database URL
   ```

2. **Configure Database**
   ```sql
   -- Enable Row Level Security
   ALTER DATABASE postgres SET "app.jwt_secret" = 'your-jwt-secret-here';
   
   -- Create application schema
   CREATE SCHEMA IF NOT EXISTS public;
   
   -- Enable extensions
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   CREATE EXTENSION IF NOT EXISTS "postgis";
   CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
   ```

3. **Apply Migration Scripts**
   ```bash
   # Run initial schema migration
   supabase db push
   
   # Or manually execute SQL files
   psql $DATABASE_URL -f migrations/001_initial_schema.sql
   psql $DATABASE_URL -f migrations/002_rls_policies.sql
   psql $DATABASE_URL -f migrations/003_indexes.sql
   ```

4. **Set up Row Level Security Policies**
   ```sql
   -- Restaurant data isolation
   CREATE POLICY restaurant_isolation ON restaurants 
   FOR ALL USING (auth.jwt() ->> 'restaurant_id' = id::text);
   
   -- Order access policy
   CREATE POLICY order_access ON orders 
   FOR ALL USING (
     restaurant_id IN (
       SELECT id FROM restaurants 
       WHERE auth.jwt() ->> 'restaurant_id' = id::text
     )
   );
   ```

### Step 2: Redis Cache Deployment
**Time: 15 minutes**

**Option A: Railway Redis**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and create Redis service
railway login
railway add redis
railway redis:create --name zergoqr-redis

# Get connection URL
railway redis:url
```

**Option B: Upstash Redis**
```bash
# Visit https://upstash.com/
# Create Redis database
# Configuration:
# - Region: Closest to your users
# - Memory: 1GB
# - Max connections: 1000

# Note connection details:
UPSTASH_REDIS_REST_URL=https://...
UPSTASH_REDIS_REST_TOKEN=...
```

**Redis Configuration**
```bash
# Add to .env
REDIS_URL=redis://username:password@host:port
REDIS_MAX_CONNECTIONS=50
REDIS_DEFAULT_TTL=3600
REDIS_KEY_PREFIX=zergoqr:
```

### Step 3: Celery Background Workers Setup  
**Time: 45 minutes**

1. **Create Celery Configuration**
   ```python
   # celery_config.py
   from celery import Celery
   import os
   
   celery_app = Celery('zergoqr')
   
   celery_app.conf.update(
       broker_url=os.getenv('REDIS_URL'),
       result_backend=os.getenv('REDIS_URL'),
       task_serializer='json',
       accept_content=['json'],
       result_serializer='json',
       timezone='Asia/Kolkata',
       enable_utc=True,
       worker_prefetch_multiplier=1,
       task_acks_late=True,
       task_reject_on_worker_lost=True,
       task_routes={
           'notifications.whatsapp.*': {'queue': 'notifications'},
           'notifications.email.*': {'queue': 'notifications'},
           'analytics.*': {'queue': 'analytics'},
           'orders.*': {'queue': 'orders'},
       },
       beat_schedule={
           'cleanup-expired-sessions': {
               'task': 'maintenance.cleanup_expired_sessions',
               'schedule': 3600.0,  # Every hour
           },
           'update-analytics': {
               'task': 'analytics.update_daily_stats', 
               'schedule': 1800.0,  # Every 30 minutes
           },
       }
   )
   
   # Auto-discover tasks
   celery_app.autodiscover_tasks(['app.tasks'])
   ```

2. **Create Task Modules**
   ```python
   # app/tasks/notifications.py
   from celery import current_app as celery_app
   from app.services.whatsapp import WhatsAppService
   
   @celery_app.task(bind=True, max_retries=3)
   def send_whatsapp_order_confirmation(self, order_data: dict):
       try:
           whatsapp_service = WhatsAppService()
           result = whatsapp_service.send_order_confirmation(order_data)
           return {"status": "sent", "message_id": result.message_id}
       except Exception as exc:
           # Exponential backoff
           countdown = 60 * (2 ** self.request.retries)
           raise self.retry(exc=exc, countdown=countdown)
   
   @celery_app.task(bind=True, max_retries=3)
   def send_restaurant_order_alert(self, order_data: dict):
       try:
           whatsapp_service = WhatsAppService()
           result = whatsapp_service.send_restaurant_alert(order_data)
           return {"status": "sent", "message_id": result.message_id}
       except Exception as exc:
           countdown = 30 * (2 ** self.request.retries)  
           raise self.retry(exc=exc, countdown=countdown)
   ```

3. **Worker Deployment Scripts**
   ```bash
   #!/bin/bash
   # start_celery_worker.sh
   
   echo "Starting Celery worker..."
   celery -A celery_config worker \
     --loglevel=info \
     --concurrency=4 \
     --max-tasks-per-child=1000 \
     --time-limit=300 \
     --soft-time-limit=240
   ```

   ```bash
   #!/bin/bash  
   # start_celery_beat.sh
   
   echo "Starting Celery beat scheduler..."
   celery -A celery_config beat \
     --loglevel=info \
     --pidfile=/tmp/celerybeat.pid \
     --schedule=/tmp/celerybeat-schedule
   ```

4. **Flower Monitoring Setup**
   ```bash
   #!/bin/bash
   # start_flower.sh
   
   echo "Starting Flower monitoring..."
   celery -A celery_config flower \
     --port=5555 \
     --basic_auth=admin:your-secure-password
   ```

---

## PHASE 2: Application Deployment

### Step 4: FastAPI Application Deployment
**Time: 60 minutes**

1. **Create Production Dockerfile**
   ```dockerfile
   # Dockerfile
   FROM python:3.12-slim as builder
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       gcc \
       postgresql-client \
       && rm -rf /var/lib/apt/lists/*
   
   # Install Python dependencies
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   FROM python:3.12-slim as runtime
   
   # Copy installed packages
   COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
   COPY --from=builder /usr/local/bin /usr/local/bin
   
   # Create non-root user
   RUN useradd --create-home --shell /bin/bash app
   
   WORKDIR /app
   COPY . .
   RUN chown -R app:app /app
   
   USER app
   EXPOSE 8000
   
   # Health check
   HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
     CMD curl -f http://localhost:8000/health || exit 1
   
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
   ```

2. **Railway Deployment Configuration**
   ```toml
   # railway.toml
   [build]
     builder = "dockerfile"
     dockerfilePath = "Dockerfile"
   
   [deploy]
     numReplicas = 2
     sleepApplication = false
     restartPolicyType = "on-failure"
     restartPolicyMaxRetries = 3
     healthcheckPath = "/health"
     healthcheckTimeout = 30
   
   [scaling]
     minInstances = 2
     maxInstances = 8
     targetCPU = 70
     targetMemory = 80
   ```

3. **Environment Variables Configuration**
   ```bash
   # Production environment variables
   DATABASE_URL=postgresql://...
   SUPABASE_URL=https://...
   SUPABASE_ANON_KEY=eyJ...
   SUPABASE_SERVICE_ROLE_KEY=eyJ...
   
   REDIS_URL=redis://...
   
   # JWT Configuration
   JWT_SECRET=your-super-secret-jwt-key
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
   
   # WhatsApp Business API
   WHATSAPP_ACCESS_TOKEN=...
   WHATSAPP_PHONE_NUMBER_ID=...
   WHATSAPP_WEBHOOK_VERIFY_TOKEN=...
   
   # Razorpay Payments
   RAZORPAY_KEY_ID=rzp_live_...
   RAZORPAY_KEY_SECRET=...
   
   # Monitoring
   SENTRY_DSN=https://...
   
   # Application Configuration
   ENVIRONMENT=production
   DEBUG=false
   CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com
   ```

4. **Deploy to Railway**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and connect to project
   railway login
   railway link
   
   # Deploy application
   railway up
   
   # Check deployment status
   railway status
   
   # View logs
   railway logs
   ```

### Step 5: Background Services Deployment
**Time: 30 minutes**

1. **Separate Celery Worker Service**
   ```dockerfile
   # Dockerfile.worker
   FROM python:3.12-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   # Start Celery worker
   CMD ["celery", "-A", "celery_config", "worker", "--loglevel=info", "--concurrency=4"]
   ```

2. **Deploy Worker as Separate Service**
   ```bash
   # Deploy worker service
   railway add
   # Select "Empty Service"
   # Name: zergoqr-worker
   
   # Configure worker service
   railway variables set WORKER_TYPE=celery
   railway up --dockerfile Dockerfile.worker
   ```

3. **Deploy Flower Monitoring**
   ```dockerfile
   # Dockerfile.flower
   FROM python:3.12-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 5555
   CMD ["celery", "-A", "celery_config", "flower", "--port=5555"]
   ```

---

## PHASE 3: Frontend Deployment

### Step 6: Flutter Web Deployment
**Time: 45 minutes**

1. **Build Flutter Web**
   ```bash
   # Navigate to Flutter project
   cd apps/frontend
   
   # Clean and get dependencies
   flutter clean
   flutter pub get
   
   # Build for production
   flutter build web --release --web-renderer canvaskit
   
   # Optimize build
   flutter build web --release --dart-define=FLUTTER_WEB_USE_SKIA=true
   ```

2. **Configure Cloudflare Pages**
   ```yaml
   # Build settings
   build_command: "flutter build web --release"
   build_output_directory: "build/web"
   root_directory: "apps/frontend"
   
   # Environment variables
   environment_variables:
     API_BASE_URL: "https://your-api-domain.com"
     SUPABASE_URL: "https://your-project.supabase.co"
     SUPABASE_ANON_KEY: "eyJ..."
   ```

3. **Custom Headers Configuration**
   ```toml
   # _headers file for Cloudflare Pages
   /*
     X-Frame-Options: DENY
     X-Content-Type-Options: nosniff
     Referrer-Policy: strict-origin-when-cross-origin
     Cache-Control: public, max-age=31536000, immutable
   
   *.html
     Cache-Control: public, max-age=0, must-revalidate
   
   /api/*
     Cache-Control: no-cache, no-store, must-revalidate
   ```

4. **Deploy to Cloudflare Pages**
   ```bash
   # Install Wrangler CLI
   npm install -g @cloudflare/wrangler
   
   # Login to Cloudflare
   wrangler login
   
   # Deploy
   wrangler pages publish build/web --project-name zergoqr
   ```

### Step 7: Mobile App Deployment
**Time: 90 minutes**

1. **Android Build Configuration**
   ```gradle
   // android/app/build.gradle
   android {
       compileSdkVersion 34
       ndkVersion flutter.ndkVersion
   
       defaultConfig {
           applicationId "com.zergoqr.app"
           minSdkVersion 21
           targetSdkVersion 34
           versionCode flutterVersionCode.toInteger()
           versionName flutterVersionName
       }
   
       buildTypes {
           release {
               signingConfig signingConfigs.release
               minifyEnabled true
               useProguard true
               proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
           }
       }
   }
   ```

2. **iOS Build Configuration**
   ```xml
   <!-- ios/Runner/Info.plist -->
   <dict>
       <key>CFBundleDisplayName</key>
       <string>ZergoQR</string>
       <key>CFBundleIdentifier</key>
       <string>com.zergoqr.app</string>
       <key>CFBundleVersion</key>
       <string>$(FLUTTER_BUILD_NUMBER)</string>
       <key>CFBundleShortVersionString</key>
       <string>$(FLUTTER_BUILD_NAME)</string>
       
       <!-- Camera permission for QR scanning -->
       <key>NSCameraUsageDescription</key>
       <string>This app needs camera access to scan QR codes for menu access</string>
   </dict>
   ```

3. **Build and Deploy**
   ```bash
   # Android build
   flutter build appbundle --release
   
   # iOS build  
   flutter build ipa --release
   
   # Upload to stores using CI/CD or manually
   ```

---

## PHASE 4: Monitoring & Observability

### Step 8: Monitoring Setup
**Time: 60 minutes**

1. **Sentry Error Tracking**
   ```python
   # Add to main.py
   import sentry_sdk
   from sentry_sdk.integrations.fastapi import FastApiIntegration
   from sentry_sdk.integrations.celery import CeleryIntegration
   
   sentry_sdk.init(
       dsn=os.getenv("SENTRY_DSN"),
       integrations=[
           FastApiIntegration(auto_enable=True),
           CeleryIntegration()
       ],
       traces_sample_rate=0.1,
       profiles_sample_rate=0.1,
       environment=os.getenv("ENVIRONMENT", "production")
   )
   ```

2. **Prometheus Metrics Endpoint**
   ```python
   # metrics.py
   from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
   
   # Business metrics
   orders_created = Counter('orders_created_total', 'Total orders created', ['restaurant_id'])
   order_processing_time = Histogram('order_processing_seconds', 'Order processing time')
   active_users = Gauge('active_users_current', 'Current active users')
   qr_scans = Counter('qr_scans_total', 'Total QR code scans', ['restaurant_id', 'table_id'])
   
   # Technical metrics
   api_requests = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
   api_request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['method', 'endpoint'])
   
   # Cache metrics
   cache_hits = Counter('cache_hits_total', 'Cache hits', ['cache_type'])
   cache_misses = Counter('cache_misses_total', 'Cache misses', ['cache_type'])
   
   # Create metrics ASGI app
   metrics_app = make_asgi_app()
   ```

3. **Health Check Endpoints**
   ```python
   @app.get("/health")
   async def health_check():
       return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
   
   @app.get("/health/detailed")
   async def detailed_health():
       checks = {}
       overall_status = "healthy"
       
       # Database check
       try:
           await database.fetch_one("SELECT 1")
           checks["database"] = {"status": "healthy", "response_time_ms": 10}
       except Exception as e:
           checks["database"] = {"status": "unhealthy", "error": str(e)}
           overall_status = "unhealthy"
       
       # Redis check
       try:
           await redis_client.ping()
           checks["redis"] = {"status": "healthy", "response_time_ms": 5}
       except Exception as e:
           checks["redis"] = {"status": "unhealthy", "error": str(e)}
           overall_status = "unhealthy"
       
       # Celery check
       try:
           inspect = celery_app.control.inspect()
           active_workers = inspect.active()
           checks["celery"] = {
               "status": "healthy" if active_workers else "unhealthy",
               "active_workers": len(active_workers) if active_workers else 0
           }
       except Exception as e:
           checks["celery"] = {"status": "unhealthy", "error": str(e)}
           overall_status = "unhealthy"
       
       return {
           "status": overall_status,
           "checks": checks,
           "timestamp": datetime.utcnow().isoformat()
       }
   ```

4. **Grafana Dashboard Configuration**
   ```json
   {
     "dashboard": {
       "id": null,
       "title": "ZergoQR Production Dashboard",
       "panels": [
         {
           "title": "API Request Rate",
           "type": "graph",
           "targets": [
             {
               "expr": "rate(api_requests_total[5m])",
               "legendFormat": "{{method}} {{endpoint}}"
             }
           ]
         },
         {
           "title": "Order Processing Time", 
           "type": "graph",
           "targets": [
             {
               "expr": "histogram_quantile(0.95, rate(order_processing_seconds_bucket[5m]))",
               "legendFormat": "95th percentile"
             }
           ]
         },
         {
           "title": "Active Users",
           "type": "stat",
           "targets": [
             {
               "expr": "active_users_current",
               "legendFormat": "Current Users"
             }
           ]
         }
       ]
     }
   }
   ```

### Step 9: Alerting Configuration
**Time: 30 minutes**

1. **AlertManager Configuration**
   ```yaml
   # alertmanager.yml
   global:
     smtp_smarthost: 'smtp.gmail.com:587'
     smtp_from: 'alerts@zergoqr.com'
   
   route:
     group_by: ['alertname']
     group_wait: 10s
     group_interval: 10s
     repeat_interval: 1h
     receiver: 'team-notifications'
   
   receivers:
   - name: 'team-notifications'
     email_configs:
     - to: 'team@zergoqr.com'
       subject: 'ZergoQR Alert: {{ .GroupLabels.alertname }}'
       body: |
         {{ range .Alerts }}
         Alert: {{ .Annotations.summary }}
         Description: {{ .Annotations.description }}
         {{ end }}
   ```

2. **Prometheus Alert Rules**
   ```yaml
   # alert_rules.yml
   groups:
   - name: zergoqr_alerts
     rules:
     - alert: HighErrorRate
       expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.1
       for: 5m
       labels:
         severity: critical
       annotations:
         summary: High error rate detected
         description: "Error rate is {{ $value }} errors per second"
   
     - alert: HighResponseTime
       expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 0.5
       for: 10m
       labels:
         severity: warning
       annotations:
         summary: High response time
         description: "95th percentile response time is {{ $value }}s"
   
     - alert: ServiceDown
       expr: up{job="zergoqr-api"} == 0
       for: 1m
       labels:
         severity: critical
       annotations:
         summary: Service is down
         description: "ZergoQR API service is not responding"
   ```

---

## PHASE 5: Production Readiness

### Step 10: Security Configuration
**Time: 45 minutes**

1. **SSL/TLS Configuration**
   ```nginx
   # nginx.conf (if using custom nginx)
   server {
       listen 443 ssl http2;
       server_name api.zergoqr.com;
   
       ssl_certificate /path/to/ssl/cert.pem;
       ssl_certificate_key /path/to/ssl/private.key;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
       ssl_prefer_server_ciphers off;
   
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

2. **Security Headers Middleware**
   ```python
   from fastapi.middleware.trustedhost import TrustedHostMiddleware
   from fastapi.middleware.cors import CORSMiddleware
   
   # Trusted hosts
   app.add_middleware(
       TrustedHostMiddleware, 
       allowed_hosts=["api.zergoqr.com", "*.zergoqr.com"]
   )
   
   # CORS configuration
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://app.zergoqr.com", "https://zergoqr.com"],
       allow_credentials=True,
       allow_methods=["GET", "POST", "PUT", "DELETE"],
       allow_headers=["*"],
   )
   
   # Security headers middleware
   @app.middleware("http")
   async def add_security_headers(request: Request, call_next):
       response = await call_next(request)
       response.headers["X-Content-Type-Options"] = "nosniff"
       response.headers["X-Frame-Options"] = "DENY"
       response.headers["X-XSS-Protection"] = "1; mode=block"
       response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
       return response
   ```

3. **Rate Limiting Configuration**
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(
       key_func=get_remote_address,
       storage_uri=os.getenv("REDIS_URL")
   )
   
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   
   # Apply rate limits
   @app.post("/api/orders")
   @limiter.limit("10/minute")
   async def create_order(request: Request, order: OrderCreate):
       pass
   
   @app.post("/api/auth/login")  
   @limiter.limit("5/minute")
   async def login(request: Request, credentials: LoginCredentials):
       pass
   ```

### Step 11: Backup & Recovery Setup
**Time: 30 minutes**

1. **Database Backup Strategy**
   ```bash
   #!/bin/bash
   # backup_database.sh
   
   BACKUP_DIR="/backups/postgres"
   TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
   BACKUP_FILE="$BACKUP_DIR/zergoqr_backup_$TIMESTAMP.sql"
   
   # Create backup
   pg_dump $DATABASE_URL > $BACKUP_FILE
   
   # Compress backup
   gzip $BACKUP_FILE
   
   # Upload to cloud storage (e.g., S3)
   aws s3 cp $BACKUP_FILE.gz s3://zergoqr-backups/postgres/
   
   # Keep only last 30 days of local backups
   find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
   ```

2. **Redis Backup Configuration**
   ```bash
   #!/bin/bash
   # backup_redis.sh
   
   BACKUP_DIR="/backups/redis"
   TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
   
   # Create Redis backup
   redis-cli --rdb $BACKUP_DIR/dump_$TIMESTAMP.rdb
   
   # Upload to cloud storage
   aws s3 cp $BACKUP_DIR/dump_$TIMESTAMP.rdb s3://zergoqr-backups/redis/
   ```

3. **Automated Backup Scheduling**
   ```yaml
   # Add to Celery beat schedule
   beat_schedule:
     'backup-database': {
       'task': 'maintenance.backup_database',
       'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
     },
     'backup-redis': {
       'task': 'maintenance.backup_redis', 
       'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
     },
   ```

### Step 12: Load Testing & Performance Validation
**Time: 60 minutes**

1. **Load Testing Script**
   ```python
   # load_test.py
   from locust import HttpUser, task, between
   import random
   
   class ZergoQRUser(HttpUser):
       wait_time = between(1, 3)
       
       def on_start(self):
           # Login or authenticate
           response = self.client.post("/api/auth/login", json={
               "username": "test@example.com",
               "password": "testpass123"
           })
           self.token = response.json().get("access_token")
           self.client.headers.update({"Authorization": f"Bearer {self.token}"})
       
       @task(3)
       def get_menu(self):
           restaurant_id = random.choice(["rest_1", "rest_2", "rest_3"])
           self.client.get(f"/api/menu/{restaurant_id}")
       
       @task(1)
       def create_order(self):
           restaurant_id = random.choice(["rest_1", "rest_2", "rest_3"])
           self.client.post(f"/api/orders", json={
               "restaurant_id": restaurant_id,
               "items": [
                   {"menu_item_id": "item_1", "quantity": 2},
                   {"menu_item_id": "item_2", "quantity": 1}
               ],
               "customer_phone": "+919876543210"
           })
       
       @task(2)
       def get_order_status(self):
           order_id = random.choice(["order_1", "order_2", "order_3"])
           self.client.get(f"/api/orders/{order_id}")
   ```

2. **Run Load Tests**
   ```bash
   # Install Locust
   pip install locust
   
   # Run load test
   locust -f load_test.py --host=https://api.zergoqr.com
   
   # Or run headless with specific parameters
   locust -f load_test.py --host=https://api.zergoqr.com \
     --users 100 --spawn-rate 10 --run-time 10m --headless
   ```

3. **Performance Validation Checklist**
   ```yaml
   performance_targets:
     - api_response_time_p95: "<200ms"
     - concurrent_users_supported: ">=100"
     - orders_per_minute: ">=1000" 
     - cache_hit_rate: ">=80%"
     - database_connection_pool_utilization: "<80%"
     - memory_usage: "<80%"
     - cpu_usage: "<70%"
     - error_rate: "<1%"
   ```

---

## Production Checklist

### Pre-Launch Validation
- [ ] All environment variables configured correctly
- [ ] Database migrations applied successfully  
- [ ] SSL certificates installed and valid
- [ ] Rate limiting configured and tested
- [ ] Backup procedures tested and verified
- [ ] Monitoring dashboards functional
- [ ] Alert notifications working
- [ ] Load testing passed for 100 concurrent users
- [ ] Security scan completed with no critical issues
- [ ] WAF/DDoS protection configured

### Launch Day Checklist
- [ ] All services healthy (API, Worker, Redis, Database)
- [ ] Monitoring dashboards active
- [ ] Support team briefed and ready
- [ ] Rollback procedures documented and tested
- [ ] Customer communication prepared
- [ ] Performance baselines recorded

### Post-Launch Monitoring (First 48 Hours)
- [ ] Monitor error rates and response times hourly
- [ ] Check queue lengths and worker performance
- [ ] Verify all background tasks processing correctly
- [ ] Monitor WhatsApp delivery rates
- [ ] Check payment processing success rates
- [ ] Monitor resource utilization (CPU, memory, database connections)
- [ ] Verify auto-scaling triggers working correctly

## Support & Troubleshooting

### Common Issues & Solutions

1. **High Response Times**
   - Check database query performance
   - Verify cache hit rates
   - Monitor connection pool utilization
   - Check for background task backlog

2. **WhatsApp Delivery Failures**
   - Verify API credentials and quotas
   - Check message template approval status
   - Monitor rate limiting
   - Verify webhook endpoints

3. **Auto-scaling Not Working**
   - Check CPU/memory thresholds
   - Verify scaling policies configuration
   - Monitor application startup time
   - Check health check endpoints

4. **Database Connection Issues**
   - Monitor connection pool utilization
   - Check for long-running queries
   - Verify RLS policies not causing locks
   - Monitor database resource usage

### Emergency Procedures

1. **API Service Down**
   ```bash
   # Check service status
   railway status
   
   # View recent logs
   railway logs --lines 100
   
   # Restart service
   railway redeploy
   ```

2. **Database Issues**
   ```bash
   # Check database health
   psql $DATABASE_URL -c "SELECT 1;"
   
   # Monitor active connections
   psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"
   
   # Kill long-running queries if needed
   psql $DATABASE_URL -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state_change < now() - interval '5 minutes';"
   ```

3. **Redis Cache Issues**
   ```bash
   # Check Redis connectivity
   redis-cli -u $REDIS_URL ping
   
   # Monitor memory usage
   redis-cli -u $REDIS_URL info memory
   
   # Clear cache if needed (use carefully)
   redis-cli -u $REDIS_URL flushdb
   ```

This comprehensive deployment guide ensures your ZERGO QR system is production-ready with proper monitoring, security, and scalability measures in place.