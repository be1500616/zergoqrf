# ZERGO QR System Monitoring and Maintenance Guide

**Version:** 1.0  
**Date:** September 24, 2025  
**System:** ZERGO QR Restaurant Management Platform

## Overview

This guide provides comprehensive monitoring and maintenance procedures to ensure the ZERGO QR system remains stable, secure, and performant. Follow these procedures to prevent connectivity issues and maintain optimal system health.

## 1. Health Monitoring Setup

### 1.1 API Health Checks
```bash
# Daily health check script
curl -f http://localhost:8000/healthz || echo "API DOWN" | mail -s "ZERGO API Alert" admin@zergo.com

# Expected response: {"status":"ok"}
```

### 1.2 Database Connectivity Monitoring
```python
# Monitor Supabase connectivity
from app.common.supabase_client import get_supabase

def check_database_health():
    try:
        client = get_supabase()
        result = client.table('restaurants').select('count').execute()
        return result.data[0]['count'] > 0
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False
```

### 1.3 Recommended Monitoring Tools
- **Uptime Monitoring:** UptimeRobot, Pingdom, or StatusCake
- **Application Monitoring:** Sentry for error tracking
- **Infrastructure Monitoring:** Supabase dashboard metrics
- **Log Aggregation:** Structured logging with JSON format

## 2. Daily Monitoring Checklist

### 2.1 System Health (Automated)
- [ ] API health endpoint responding (200 OK)
- [ ] Database connectivity working
- [ ] Authentication system functional
- [ ] QR code access working for sample restaurants

### 2.2 Performance Metrics
- [ ] API response times < 500ms for 95th percentile
- [ ] Database query performance within acceptable limits
- [ ] Error rate < 1% for all endpoints
- [ ] Memory usage within normal ranges

### 2.3 Security Monitoring
- [ ] No unauthorized access attempts
- [ ] RLS policies functioning correctly
- [ ] JWT token validation working
- [ ] No suspicious database queries

## 3. Weekly Maintenance Tasks

### 3.1 Database Maintenance
```sql
-- Check database performance
SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del 
FROM pg_stat_user_tables 
ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC;

-- Verify RLS policies are active
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';
```

### 3.2 Authentication System Check
```python
# Verify helper functions are working
def verify_auth_functions():
    client = get_supabase()
    
    # Test helper functions
    functions_to_test = [
        'get_user_restaurant_id',
        'user_has_role', 
        'user_has_permission'
    ]
    
    for func in functions_to_test:
        try:
            # Test with dummy data
            result = client.rpc(func, {'user_id': '00000000-0000-0000-0000-000000000000'})
            print(f"✅ {func}: Working")
        except Exception as e:
            print(f"❌ {func}: Error - {e}")
```

### 3.3 Data Integrity Checks
```sql
-- Check for orphaned records
SELECT COUNT(*) as orphaned_staff 
FROM restaurant_staff rs 
LEFT JOIN restaurants r ON rs.restaurant_id = r.id 
WHERE r.id IS NULL;

-- Verify restaurant codes are unique
SELECT code, COUNT(*) 
FROM restaurants 
GROUP BY code 
HAVING COUNT(*) > 1;
```

## 4. Monthly Maintenance Tasks

### 4.1 Performance Review
- Analyze API response time trends
- Review database query performance
- Check for slow queries and optimize
- Review error logs and patterns

### 4.2 Security Audit
- Review access logs for anomalies
- Verify RLS policies are still effective
- Check for unused or inactive staff accounts
- Validate JWT token expiration settings

### 4.3 Backup Verification
- Verify Supabase automatic backups are working
- Test backup restoration process (in staging)
- Document backup retention policies
- Verify point-in-time recovery capabilities

## 5. Alerting Configuration

### 5.1 Critical Alerts (Immediate Response)
- API endpoint returning 5xx errors
- Database connectivity failures
- Authentication system failures
- High error rates (>5%)

### 5.2 Warning Alerts (Response within 1 hour)
- API response times >1 second
- Database query performance degradation
- Unusual traffic patterns
- Memory usage >80%

### 5.3 Info Alerts (Daily review)
- New restaurant registrations
- Staff account changes
- Configuration updates
- Performance trend changes

## 6. Incident Response Procedures

### 6.1 Database Connectivity Issues
1. Check Supabase status page
2. Verify DNS resolution: `nslookup kpsyzsmgzuweadpnffwy.supabase.co`
3. Test direct API access: `curl https://kpsyzsmgzuweadpnffwy.supabase.co/rest/v1/`
4. Check environment variables and credentials
5. Review recent configuration changes

### 6.2 API Performance Issues
1. Check server resources (CPU, memory)
2. Review recent deployments
3. Analyze slow query logs
4. Check for database connection pool exhaustion
5. Scale resources if necessary

### 6.3 Authentication Failures
1. Verify JWT secret configuration
2. Check Supabase auth service status
3. Test helper functions manually
4. Review RLS policy changes
5. Validate user permissions

## 7. Preventive Maintenance

### 7.1 Regular Updates
- Keep dependencies updated (security patches)
- Monitor Supabase service updates
- Update monitoring tools and scripts
- Review and update documentation

### 7.2 Capacity Planning
- Monitor database storage growth
- Track API request volume trends
- Plan for traffic spikes (marketing campaigns)
- Review and adjust rate limits

### 7.3 Disaster Recovery Testing
- Test backup restoration procedures quarterly
- Verify failover mechanisms
- Document recovery time objectives (RTO)
- Train team on incident response procedures

## 8. Monitoring Scripts

### 8.1 Health Check Script
```bash
#!/bin/bash
# health_check.sh - Run every 5 minutes

API_URL="http://localhost:8000"
ALERT_EMAIL="admin@zergo.com"

# Check API health
if ! curl -f "$API_URL/healthz" > /dev/null 2>&1; then
    echo "API health check failed" | mail -s "ZERGO API Alert" $ALERT_EMAIL
fi

# Check sample restaurant access
if ! curl -f "$API_URL/restaurants/TEST001" > /dev/null 2>&1; then
    echo "Restaurant access failed" | mail -s "ZERGO QR Access Alert" $ALERT_EMAIL
fi
```

### 8.2 Database Health Script
```python
#!/usr/bin/env python3
# db_health_check.py - Run every 15 minutes

import sys
import smtplib
from email.mime.text import MIMEText
sys.path.append('apps/backend')
from app.common.supabase_client import get_supabase

def send_alert(message):
    msg = MIMEText(message)
    msg['Subject'] = 'ZERGO Database Alert'
    msg['From'] = 'system@zergo.com'
    msg['To'] = 'admin@zergo.com'
    
    # Configure SMTP settings
    # smtp_server.send_message(msg)

def check_database():
    try:
        client = get_supabase()
        
        # Test basic connectivity
        result = client.table('restaurants').select('count').execute()
        restaurant_count = result.data[0]['count'] if result.data else 0
        
        # Test helper functions
        client.rpc('get_user_restaurant_id', {'user_id': '00000000-0000-0000-0000-000000000000'}).execute()
        
        print(f"✅ Database health check passed - {restaurant_count} restaurants")
        return True
        
    except Exception as e:
        error_msg = f"Database health check failed: {e}"
        print(f"❌ {error_msg}")
        send_alert(error_msg)
        return False

if __name__ == "__main__":
    success = check_database()
    sys.exit(0 if success else 1)
```

## 9. Performance Baselines

### 9.1 API Response Times (95th percentile)
- `/healthz`: < 50ms
- `/restaurants/{code}`: < 200ms
- `/restaurants/me`: < 300ms
- `/restaurants/register`: < 2000ms

### 9.2 Database Query Performance
- Simple SELECT queries: < 50ms
- Complex JOIN queries: < 200ms
- INSERT/UPDATE operations: < 100ms
- RPC function calls: < 150ms

### 9.3 System Resources
- CPU usage: < 70% average
- Memory usage: < 80% average
- Database connections: < 80% of pool
- Disk I/O: < 80% capacity

## 10. Contact Information

### 10.1 Emergency Contacts
- **System Administrator:** admin@zergo.com
- **Database Administrator:** dba@zergo.com
- **Development Team:** dev@zergo.com

### 10.2 Service Providers
- **Supabase Support:** https://supabase.com/support
- **Hosting Provider:** [Your hosting provider]
- **Domain Registrar:** [Your domain registrar]

## 11. Documentation Updates

This guide should be reviewed and updated:
- After any major system changes
- Quarterly for accuracy and completeness
- When new monitoring tools are added
- After any significant incidents

**Last Updated:** September 24, 2025  
**Next Review Date:** December 24, 2025
