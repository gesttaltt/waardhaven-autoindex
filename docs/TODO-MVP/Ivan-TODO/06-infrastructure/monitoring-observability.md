# 📊 Monitoring & Observability - Complete System Visibility

**Priority**: HIGH  
**Complexity**: High  
**Timeline**: 3-4 days  
**Value**: Critical for maintaining system reliability and performance optimization

## 🎯 Objective

Build a comprehensive monitoring and observability platform that:
- Provides real-time visibility into system health and performance
- Enables proactive issue detection and resolution
- Supports data-driven decision making for optimization
- Ensures compliance with SLA/SLO requirements
- Facilitates rapid troubleshooting and debugging

## 📡 Observability Architecture

### Three Pillars of Observability
```
┌────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY PLATFORM                      │
│              "Complete System Visibility"                     │
└──────────────────────┬─────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────┼────┐   ┌────┼────┐   ┌────┼────┐
    │METRICS│   │LOGS  │   │TRACES│
    │       │   │      │   │      │
    └─────────┘   └─────────┘   └─────────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
┌──────────────────────┼────────────────────────────────────────┐
│              ANALYSIS & ALERTING LAYER                        │
│        "Intelligence from Data"                               │
└──────────────────────┬────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────┼────┐   ┌────┼────┐   ┌────┼────┐
    │ALERT │   │DASH  │   │SLO   │
    │MANAGER│   │BOARDS│   │MONITOR│
    └─────────┘   └─────────┘   └─────────┘
```

### Monitoring Stack Architecture
```yaml
# monitoring/stack-configuration.yaml
monitoring_stack:
  metrics:
    primary: "Prometheus"
    secondary: "CloudWatch"
    retention: "1 year"
    scrape_interval: "15s"
    
  logs:
    aggregation: "ELK Stack (Elasticsearch, Logstash, Kibana)"
    shipping: "Fluent Bit"
    retention: "90 days (hot), 1 year (warm), 7 years (cold)"
    
  traces:
    system: "Jaeger"
    sampling_rate: "1% (production), 100% (development)"
    retention: "7 days"
    
  visualization:
    primary: "Grafana"
    business_metrics: "Custom Dashboard"
    alerts: "PagerDuty + Slack"
    
  synthetic_monitoring:
    uptime: "Pingdom"
    performance: "WebPageTest"
    api_monitoring: "Postman + Custom Scripts"

# Data sources integration
data_sources:
  infrastructure:
    - kubernetes_metrics
    - node_exporter
    - cadvisor
    - kube_state_metrics
    
  applications:
    - custom_application_metrics
    - jvm_metrics
    - python_metrics
    - database_metrics
    
  business:
    - user_activity_metrics
    - financial_metrics
    - trading_metrics
    - compliance_metrics
    
  external:
    - third_party_api_metrics
    - market_data_provider_status
    - news_feed_availability
```

## 📈 Metrics Collection & Management

### Prometheus Configuration
```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  scrape_timeout: 10s
  evaluation_interval: 15s
  external_labels:
    cluster: 'waardhaven-prod'
    region: 'us-east-1'

# Rule files
rule_files:
  - "rules/*.yml"

# Alerting configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

# Scrape configurations
scrape_configs:
  # Kubernetes components
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
      - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https

  # Node metrics
  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      - target_label: __address__
        replacement: kubernetes.default.svc:443
      - source_labels: [__meta_kubernetes_node_name]
        regex: (.+)
        target_label: __metrics_path__
        replacement: /api/v1/nodes/${1}/proxy/metrics

  # Pod metrics
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)

  # Application-specific metrics
  - job_name: 'waardhaven-api'
    kubernetes_sd_configs:
      - role: endpoints
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_label_app]
        action: keep
        regex: waardhaven-api
      - source_labels: [__meta_kubernetes_endpoint_port_name]
        action: keep
        regex: metrics

  # Database metrics
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']
    
  # Redis metrics  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Kafka metrics
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka-exporter:9308']

# Storage configuration
storage:
  tsdb:
    retention.time: 365d
    retention.size: 100GB
    path: /prometheus/data
    wal-compression: true
```

### Custom Application Metrics
```python
# monitoring/custom_metrics.py
from prometheus_client import Counter, Histogram, Gauge, Summary
import time
from functools import wraps

# Business metrics
TRADES_EXECUTED = Counter(
    'trades_executed_total',
    'Total number of trades executed',
    ['symbol', 'side', 'order_type']
)

PORTFOLIO_VALUE = Gauge(
    'portfolio_value_usd',
    'Current portfolio value in USD',
    ['user_id', 'account_type']
)

API_REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'Time spent processing API requests',
    ['method', 'endpoint', 'status']
)

RECOMMENDATION_ACCURACY = Gauge(
    'recommendation_accuracy_ratio',
    'Accuracy of AI recommendations',
    ['recommendation_type', 'time_horizon']
)

# System performance metrics
DATABASE_QUERY_DURATION = Histogram(
    'database_query_duration_seconds',
    'Database query execution time',
    ['query_type', 'table']
)

CACHE_HIT_RATIO = Gauge(
    'cache_hit_ratio',
    'Cache hit ratio',
    ['cache_type', 'cache_key_prefix']
)

DATA_PIPELINE_LAG = Gauge(
    'data_pipeline_lag_seconds',
    'Data pipeline processing lag',
    ['pipeline', 'source']
)

# Financial industry specific metrics
MARKET_DATA_LATENCY = Histogram(
    'market_data_latency_seconds',
    'Market data end-to-end latency',
    ['provider', 'symbol']
)

COMPLIANCE_VIOLATIONS = Counter(
    'compliance_violations_total',
    'Number of compliance violations detected',
    ['violation_type', 'severity']
)

RISK_LIMIT_BREACHES = Counter(
    'risk_limit_breaches_total',
    'Number of risk limit breaches',
    ['limit_type', 'severity']
)

class MetricsCollector:
    """Central metrics collection and reporting"""
    
    def __init__(self):
        self.start_time = time.time()
        
    def record_trade(self, symbol: str, side: str, order_type: str):
        """Record a trade execution"""
        TRADES_EXECUTED.labels(
            symbol=symbol,
            side=side,
            order_type=order_type
        ).inc()
    
    def update_portfolio_value(self, user_id: str, account_type: str, value: float):
        """Update portfolio value metric"""
        PORTFOLIO_VALUE.labels(
            user_id=user_id,
            account_type=account_type
        ).set(value)
    
    def record_api_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record API request metrics"""
        API_REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint,
            status=str(status)
        ).observe(duration)
    
    def update_recommendation_accuracy(self, rec_type: str, horizon: str, accuracy: float):
        """Update recommendation accuracy metric"""
        RECOMMENDATION_ACCURACY.labels(
            recommendation_type=rec_type,
            time_horizon=horizon
        ).set(accuracy)
    
    def record_market_data_latency(self, provider: str, symbol: str, latency: float):
        """Record market data latency"""
        MARKET_DATA_LATENCY.labels(
            provider=provider,
            symbol=symbol
        ).observe(latency)
    
    def record_compliance_violation(self, violation_type: str, severity: str):
        """Record compliance violation"""
        COMPLIANCE_VIOLATIONS.labels(
            violation_type=violation_type,
            severity=severity
        ).inc()

# Decorators for automatic metrics collection
def monitor_api_performance(endpoint_name: str):
    """Decorator to monitor API endpoint performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                status = 200
                return result
            except Exception as e:
                status = 500
                raise
            finally:
                duration = time.time() - start_time
                API_REQUEST_DURATION.labels(
                    method="POST",  # Would extract from request context
                    endpoint=endpoint_name,
                    status=str(status)
                ).observe(duration)
        
        return wrapper
    return decorator

def monitor_database_query(query_type: str, table: str):
    """Decorator to monitor database query performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                DATABASE_QUERY_DURATION.labels(
                    query_type=query_type,
                    table=table
                ).observe(duration)
        
        return wrapper
    return decorator

# Usage examples
metrics = MetricsCollector()

@monitor_api_performance("get_portfolio")
def get_portfolio(user_id: str):
    # API implementation
    pass

@monitor_database_query("SELECT", "portfolios")
def fetch_portfolio_from_db(user_id: str):
    # Database query implementation
    pass
```

## 📊 Alerting & Notification System

### AlertManager Configuration
```yaml
# alertmanager/alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@waardhaven.com'
  smtp_auth_username: 'alerts@waardhaven.com'
  smtp_auth_password: 'secure_password'

# Routing configuration
route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'default'
  
  routes:
    # Critical alerts
    - match:
        severity: critical
      receiver: 'critical-alerts'
      group_wait: 5s
      repeat_interval: 5m
      
    # Security alerts
    - match:
        category: security
      receiver: 'security-team'
      group_wait: 1m
      repeat_interval: 15m
      
    # Business alerts
    - match:
        category: business
      receiver: 'business-team'
      group_wait: 5m
      repeat_interval: 1h
      
    # Infrastructure alerts
    - match:
        category: infrastructure
      receiver: 'devops-team'
      group_wait: 2m
      repeat_interval: 30m

# Receivers configuration
receivers:
  - name: 'default'
    email_configs:
      - to: 'devops@waardhaven.com'
        subject: '[Waardhaven] {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}

  - name: 'critical-alerts'
    pagerduty_configs:
      - service_key: 'critical-service-key'
        description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'
        severity: 'critical'
    email_configs:
      - to: 'critical@waardhaven.com'
        subject: '[CRITICAL] {{ .GroupLabels.alertname }}'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/critical'
        channel: '#critical-alerts'
        title: '🚨 Critical Alert'
        text: '{{ .CommonAnnotations.description }}'

  - name: 'security-team'
    email_configs:
      - to: 'security@waardhaven.com'
        subject: '[SECURITY] {{ .GroupLabels.alertname }}'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/security'
        channel: '#security-alerts'
        title: '🔒 Security Alert'

  - name: 'business-team'
    email_configs:
      - to: 'business@waardhaven.com'
        subject: '[BUSINESS] {{ .GroupLabels.alertname }}'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/business'
        channel: '#business-alerts'
        title: '📊 Business Alert'

  - name: 'devops-team'
    email_configs:
      - to: 'devops@waardhaven.com'
        subject: '[INFRA] {{ .GroupLabels.alertname }}'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/devops'
        channel: '#infrastructure-alerts'
        title: '🏗️ Infrastructure Alert'

# Inhibition rules
inhibit_rules:
  # Inhibit warning alerts if critical alert is firing
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']
```

### Prometheus Alert Rules
```yaml
# prometheus/rules/infrastructure.yml
groups:
  - name: infrastructure
    rules:
      # High CPU usage
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
          category: infrastructure
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for more than 5 minutes on {{ $labels.instance }}"

      # High memory usage
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
          category: infrastructure
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85% on {{ $labels.instance }}"

      # Disk space low
      - alert: DiskSpaceLow
        expr: node_filesystem_avail_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"} * 100 < 10
        for: 5m
        labels:
          severity: critical
          category: infrastructure
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk space is below 10% on {{ $labels.instance }}, mount point: {{ $labels.mountpoint }}"

# prometheus/rules/application.yml
groups:
  - name: application
    rules:
      # High API error rate
      - alert: HighAPIErrorRate
        expr: rate(api_request_duration_seconds_count{status=~"5.."}[5m]) / rate(api_request_duration_seconds_count[5m]) * 100 > 5
        for: 2m
        labels:
          severity: critical
          category: application
        annotations:
          summary: "High API error rate"
          description: "API error rate is above 5% for {{ $labels.endpoint }}"

      # High API response time
      - alert: HighAPIResponseTime
        expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
          category: application
        annotations:
          summary: "High API response time"
          description: "95th percentile response time is above 2 seconds for {{ $labels.endpoint }}"

      # Database connection pool exhausted
      - alert: DatabaseConnectionPoolExhausted
        expr: database_connections_active / database_connections_max > 0.9
        for: 2m
        labels:
          severity: critical
          category: application
        annotations:
          summary: "Database connection pool near exhaustion"
          description: "Database connection pool is 90% full"

# prometheus/rules/business.yml
groups:
  - name: business
    rules:
      # Trading volume anomaly
      - alert: TradingVolumeAnomaly
        expr: trades_executed_total offset 1h > trades_executed_total * 3
        for: 10m
        labels:
          severity: warning
          category: business
        annotations:
          summary: "Unusual trading volume detected"
          description: "Trading volume is 3x higher than the previous hour"

      # Market data lag
      - alert: MarketDataLag
        expr: data_pipeline_lag_seconds{pipeline="market-data"} > 30
        for: 1m
        labels:
          severity: critical
          category: business
        annotations:
          summary: "Market data lag detected"
          description: "Market data is lagging by {{ $value }} seconds"

      # Low recommendation accuracy
      - alert: LowRecommendationAccuracy
        expr: recommendation_accuracy_ratio < 0.6
        for: 10m
        labels:
          severity: warning
          category: business
        annotations:
          summary: "Recommendation accuracy below threshold"
          description: "Recommendation accuracy is {{ $value }}, below 60% threshold"

# prometheus/rules/security.yml
groups:
  - name: security
    rules:
      # Multiple failed login attempts
      - alert: MultipleFailedLogins
        expr: increase(login_attempts_total{status="failed"}[5m]) > 10
        for: 0m
        labels:
          severity: warning
          category: security
        annotations:
          summary: "Multiple failed login attempts"
          description: "{{ $value }} failed login attempts in the last 5 minutes"

      # Compliance violation detected
      - alert: ComplianceViolation
        expr: increase(compliance_violations_total[1m]) > 0
        for: 0m
        labels:
          severity: critical
          category: security
        annotations:
          summary: "Compliance violation detected"
          description: "{{ $labels.violation_type }} violation detected"

      # Unusual data access pattern
      - alert: UnusualDataAccess
        expr: rate(sensitive_data_access_total[10m]) > 100
        for: 5m
        labels:
          severity: warning
          category: security
        annotations:
          summary: "Unusual data access pattern"
          description: "High rate of sensitive data access: {{ $value }} requests/second"
```

## 📊 Grafana Dashboards

### Infrastructure Dashboard
```json
{
  "dashboard": {
    "id": null,
    "title": "Waardhaven Infrastructure Overview",
    "tags": ["infrastructure", "overview"],
    "timezone": "utc",
    "panels": [
      {
        "id": 1,
        "title": "System Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "up",
            "legendFormat": "Services Up",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 0.8},
                {"color": "green", "value": 0.95}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "CPU Usage by Node",
        "type": "timeseries",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "custom": {
              "drawStyle": "line",
              "lineInterpolation": "linear",
              "spanNulls": false
            },
            "unit": "percent"
          }
        }
      },
      {
        "id": 3,
        "title": "Memory Usage",
        "type": "timeseries",
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
            "legendFormat": "{{instance}}",
            "refId": "A"
          }
        ]
      },
      {
        "id": 4,
        "title": "Network I/O",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(node_network_receive_bytes_total[5m])",
            "legendFormat": "{{instance}} - Receive",
            "refId": "A"
          },
          {
            "expr": "rate(node_network_transmit_bytes_total[5m])",
            "legendFormat": "{{instance}} - Transmit",
            "refId": "B"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

### Business Metrics Dashboard
```json
{
  "dashboard": {
    "title": "Waardhaven Business Metrics",
    "panels": [
      {
        "id": 1,
        "title": "Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(active_users_total)",
            "refId": "A"
          }
        ]
      },
      {
        "id": 2,
        "title": "Portfolio Values",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum by(account_type) (portfolio_value_usd)",
            "legendFormat": "{{account_type}}",
            "refId": "A"
          }
        ]
      },
      {
        "id": 3,
        "title": "Trades Executed",
        "type": "bargauge",
        "targets": [
          {
            "expr": "sum by(symbol) (increase(trades_executed_total[1h]))",
            "legendFormat": "{{symbol}}",
            "refId": "A"
          }
        ]
      },
      {
        "id": 4,
        "title": "API Performance",
        "type": "timeseries",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile",
            "refId": "A"
          },
          {
            "expr": "histogram_quantile(0.50, rate(api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile",
            "refId": "B"
          }
        ]
      },
      {
        "id": 5,
        "title": "Recommendation Accuracy",
        "type": "gauge",
        "targets": [
          {
            "expr": "avg(recommendation_accuracy_ratio)",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0,
            "max": 1,
            "unit": "percentunit",
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 0.6},
                {"color": "green", "value": 0.8}
              ]
            }
          }
        }
      }
    ]
  }
}
```

## 🔍 Distributed Tracing

### Jaeger Configuration
```yaml
# jaeger/jaeger-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
        - name: jaeger
          image: jaegertracing/all-in-one:1.50
          ports:
            - containerPort: 16686
              name: ui
            - containerPort: 14268
              name: collector
            - containerPort: 6831
              name: agent-udp
            - containerPort: 6832
              name: agent-binary
          env:
            - name: COLLECTOR_ZIPKIN_HOST_PORT
              value: ":9411"
            - name: SPAN_STORAGE_TYPE
              value: "elasticsearch"
            - name: ES_SERVER_URLS
              value: "http://elasticsearch:9200"
          resources:
            requests:
              memory: 1Gi
              cpu: 500m
            limits:
              memory: 2Gi
              cpu: 1000m

---
apiVersion: v1
kind: Service
metadata:
  name: jaeger
  namespace: monitoring
spec:
  selector:
    app: jaeger
  ports:
    - name: ui
      port: 16686
      targetPort: 16686
    - name: collector
      port: 14268
      targetPort: 14268
    - name: agent-udp
      port: 6831
      targetPort: 6831
      protocol: UDP
    - name: agent-binary
      port: 6832
      targetPort: 6832
```

### Application Tracing Implementation
```python
# tracing/tracing_setup.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

def setup_tracing():
    """Setup distributed tracing"""
    
    # Set up the tracer provider
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger-agent",
        agent_port=6831,
    )
    
    # Add span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Auto-instrument common libraries
    FlaskInstrumentor().instrument()
    Psycopg2Instrumentor().instrument()
    RedisInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    
    return tracer

# Custom tracing decorators
def trace_function(operation_name: str):
    """Decorator to trace function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            
            with tracer.start_as_current_span(operation_name) as span:
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("function.result.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("function.result.success", False)
                    span.set_attribute("function.error", str(e))
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator

# Usage examples
tracer = setup_tracing()

@trace_function("portfolio.calculate_value")
def calculate_portfolio_value(user_id: str):
    """Calculate total portfolio value with tracing"""
    
    with tracer.start_as_current_span("portfolio.fetch_positions") as span:
        span.set_attribute("user.id", user_id)
        positions = fetch_user_positions(user_id)
        span.set_attribute("positions.count", len(positions))
    
    total_value = 0
    for position in positions:
        with tracer.start_as_current_span("portfolio.price_position") as span:
            span.set_attribute("position.symbol", position.symbol)
            span.set_attribute("position.quantity", position.quantity)
            
            current_price = get_current_price(position.symbol)
            position_value = position.quantity * current_price
            total_value += position_value
            
            span.set_attribute("position.value", position_value)
    
    return total_value

@trace_function("market_data.fetch_price")
def get_current_price(symbol: str) -> float:
    """Fetch current price with tracing"""
    
    with tracer.start_as_current_span("cache.check_price") as span:
        span.set_attribute("symbol", symbol)
        cached_price = redis_client.get(f"price:{symbol}")
        
        if cached_price:
            span.set_attribute("cache.hit", True)
            return float(cached_price)
        
        span.set_attribute("cache.hit", False)
    
    with tracer.start_as_current_span("api.fetch_price") as span:
        span.set_attribute("symbol", symbol)
        span.set_attribute("provider", "polygon")
        
        # External API call
        price = external_api.get_price(symbol)
        
        # Cache the result
        redis_client.setex(f"price:{symbol}", 300, price)
        
        span.set_attribute("price.value", price)
        return price
```

## 📈 Service Level Objectives (SLOs)

### SLO Configuration
```yaml
# slo/slo-definitions.yaml
service_level_objectives:
  api_availability:
    description: "API service availability"
    slo_target: 99.9%  # 8.76 hours downtime per year
    measurement_window: "30d"
    error_budget: 0.1%
    
    indicators:
      - name: "http_requests_success"
        query: |
          sum(rate(api_request_duration_seconds_count{status!~"5.."}[5m])) /
          sum(rate(api_request_duration_seconds_count[5m]))
        threshold: 0.999
        
  api_latency:
    description: "API response time performance"
    slo_target: 95%    # 95% of requests under 500ms
    measurement_window: "30d"
    
    indicators:
      - name: "http_request_latency_p95"
        query: |
          histogram_quantile(0.95, 
            sum(rate(api_request_duration_seconds_bucket[5m])) by (le)
          )
        threshold: 0.5  # 500ms
        
  data_freshness:
    description: "Market data freshness"
    slo_target: 99%    # 99% of data within 5 seconds
    measurement_window: "24h"
    
    indicators:
      - name: "market_data_lag"
        query: |
          (sum(data_pipeline_lag_seconds <= 5) / 
           sum(data_pipeline_lag_seconds)) by (pipeline)
        threshold: 0.99

# SLO monitoring automation
slo_monitoring:
  error_budget_alerts:
    - name: "Error Budget 50% Consumed"
      threshold: 0.5
      severity: warning
      
    - name: "Error Budget 90% Consumed"
      threshold: 0.9
      severity: critical
      
  slo_breach_alerts:
    - name: "SLO Breach Detected"
      condition: "slo_target_missed"
      severity: critical
      escalation: "immediate"
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| System uptime | >99.9% | - |
| Alert noise ratio | <5% false positives | - |
| Mean time to detection | <5 minutes | - |
| Mean time to resolution | <30 minutes | - |
| Monitoring coverage | >95% of services | - |

---

**Next**: Complete infrastructure section with DevOps automation.