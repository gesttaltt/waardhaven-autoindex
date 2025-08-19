# 🚀 Deployment Architecture - Cloud-Native Scalable Platform

**Priority**: CRITICAL  
**Complexity**: Very High  
**Timeline**: 4-5 days  
**Value**: Foundation for all platform operations and global scalability

## 🎯 Objective

Design and implement a cloud-native deployment architecture that:
- Supports global operations with low latency
- Scales automatically based on demand
- Provides 99.9% uptime with disaster recovery
- Ensures cost efficiency through intelligent resource management
- Maintains security and compliance across all regions

## 🌍 Global Architecture Overview

### Multi-Region Strategy
```yaml
# Global Deployment Topology
production_regions:
  primary:
    us_east_1:
      purpose: Primary North American operations
      services: [api, web, data_processing, ml_training]
      users: North America (60% of traffic)
      data_centers: [Virginia]
      
    eu_west_1:
      purpose: European operations center
      services: [api, web, data_processing]
      users: Europe, Africa, Middle East (25% of traffic)
      data_centers: [Ireland]
      
    ap_southeast_1:
      purpose: Asian Pacific operations
      services: [api, web, data_processing]
      users: Asia Pacific (15% of traffic)
      data_centers: [Singapore]

  disaster_recovery:
    us_west_2:
      purpose: DR for us-east-1
      services: [standby_api, backup_storage]
      rto: 30 minutes
      rpo: 5 minutes
      
    eu_central_1:
      purpose: DR for eu-west-1 + GDPR compliance
      services: [standby_api, gdpr_compliant_storage]
      rto: 30 minutes
      rpo: 5 minutes

# Edge Locations (CDN)
edge_locations:
  cloudfront_pops: 300+ locations globally
  content_types: [static_assets, cached_api_responses, market_data]
  cache_ttl:
    static_assets: 1 year
    market_data: 5 seconds
    api_responses: 1 minute
```

## 🏗️ Infrastructure as Code

### Terraform Infrastructure Modules
```hcl
# terraform/main.tf
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
  
  backend "s3" {
    bucket         = "waardhaven-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

# Global Infrastructure Module
module "global_infrastructure" {
  source = "./modules/global"
  
  environment = var.environment
  project     = var.project_name
  
  # Multi-region configuration
  regions = {
    primary = {
      us_east_1    = { enabled = true, is_primary = true }
      eu_west_1    = { enabled = true, is_primary = false }
      ap_southeast_1 = { enabled = true, is_primary = false }
    }
    disaster_recovery = {
      us_west_2    = { enabled = true, role = "dr" }
      eu_central_1 = { enabled = true, role = "dr_gdpr" }
    }
  }
  
  # Global services
  global_services = {
    cloudfront    = true
    route53       = true
    waf           = true
    shield        = true
  }
}

# Regional Infrastructure Modules
module "regional_infrastructure" {
  source = "./modules/regional"
  
  for_each = var.regions
  
  region      = each.key
  environment = var.environment
  
  # Kubernetes cluster configuration
  eks_config = {
    cluster_version = "1.28"
    node_groups = {
      api_nodes = {
        instance_types = ["c5.2xlarge"]
        min_size      = 3
        max_size      = 20
        desired_size  = 5
      }
      data_processing_nodes = {
        instance_types = ["r5.4xlarge"]
        min_size      = 2
        max_size      = 10
        desired_size  = 3
      }
      ml_nodes = {
        instance_types = ["p3.2xlarge"]
        min_size      = 0
        max_size      = 5
        desired_size  = 1
      }
    }
  }
  
  # Database configuration
  database_config = {
    engine_version = "15.4"
    instance_class = "db.r6g.2xlarge"
    multi_az      = true
    backup_retention = 30
    
    # Read replicas per region
    read_replicas = {
      count          = 2
      instance_class = "db.r6g.xlarge"
    }
  }
  
  # Cache configuration
  cache_config = {
    redis_version = "7.0"
    node_type    = "cache.r6g.xlarge"
    num_shards   = 3
    replicas     = 2
  }
}
```

### Kubernetes Cluster Configuration
```yaml
# k8s/cluster-config/eks-cluster.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: waardhaven-prod
  region: us-east-1
  version: "1.28"

# IAM configuration
iam:
  withOIDC: true
  serviceAccounts:
    - metadata:
        name: aws-load-balancer-controller
        namespace: kube-system
      wellKnownPolicies:
        awsLoadBalancerController: true
    - metadata:
        name: cluster-autoscaler
        namespace: kube-system
      wellKnownPolicies:
        autoScaling: true

# VPC configuration
vpc:
  id: "vpc-12345678"
  subnets:
    private:
      us-east-1a: { id: "subnet-private-1a" }
      us-east-1b: { id: "subnet-private-1b" }
      us-east-1c: { id: "subnet-private-1c" }
    public:
      us-east-1a: { id: "subnet-public-1a" }
      us-east-1b: { id: "subnet-public-1b" }
      us-east-1c: { id: "subnet-public-1c" }

# Node groups
nodeGroups:
  # API application nodes
  - name: api-nodes
    instanceType: c5.2xlarge
    minSize: 3
    maxSize: 20
    desiredCapacity: 5
    volumeSize: 100
    volumeType: gp3
    
    labels:
      workload-type: api
      node-class: compute-optimized
    
    taints:
      - key: workload-type
        value: api
        effect: NoSchedule
    
    iam:
      attachPolicyARNs:
        - arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy
        - arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy
        - arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
    
    ssh:
      enableSsm: true
    
    # Spot instances for cost optimization
    spot: true
    instancesDistribution:
      maxPrice: 0.20
      instanceTypes: ["c5.2xlarge", "c5.4xlarge", "m5.2xlarge"]
      spotInstancePools: 3
  
  # Data processing nodes
  - name: data-processing-nodes
    instanceType: r5.4xlarge
    minSize: 2
    maxSize: 10
    desiredCapacity: 3
    volumeSize: 500
    volumeType: gp3
    
    labels:
      workload-type: data-processing
      node-class: memory-optimized
    
    taints:
      - key: workload-type
        value: data-processing
        effect: NoSchedule
  
  # ML training nodes
  - name: ml-nodes
    instanceType: p3.2xlarge
    minSize: 0
    maxSize: 5
    desiredCapacity: 1
    volumeSize: 1000
    volumeType: gp3
    
    labels:
      workload-type: ml-training
      node-class: gpu-accelerated
    
    taints:
      - key: workload-type
        value: ml-training
        effect: NoSchedule
      - key: nvidia.com/gpu
        value: "true"
        effect: NoSchedule

# Add-ons
addons:
  - name: vpc-cni
    version: latest
  - name: coredns
    version: latest
  - name: kube-proxy
    version: latest
  - name: aws-ebs-csi-driver
    version: latest

# CloudWatch logging
cloudWatch:
  clusterLogging:
    enableTypes: ["api", "audit", "authenticator", "controllerManager", "scheduler"]
    logRetentionInDays: 30
```

## 🐳 Container Platform Architecture

### Application Deployment Manifests
```yaml
# k8s/applications/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: waardhaven-api
  namespace: production
  labels:
    app: waardhaven-api
    version: v1.0.0
    tier: backend
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  
  selector:
    matchLabels:
      app: waardhaven-api
  
  template:
    metadata:
      labels:
        app: waardhaven-api
        version: v1.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    
    spec:
      # Node selection
      nodeSelector:
        workload-type: api
      
      tolerations:
        - key: workload-type
          value: api
          effect: NoSchedule
      
      # Service account
      serviceAccountName: waardhaven-api
      
      # Security context
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      
      # Init containers
      initContainers:
        - name: migration
          image: waardhaven/api:v1.0.0
          command: ["python", "manage.py", "migrate"]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: database-secrets
                  key: url
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
      
      # Application containers
      containers:
        - name: api
          image: waardhaven/api:v1.0.0
          ports:
            - containerPort: 8000
              name: http
            - containerPort: 8080
              name: metrics
          
          # Environment variables
          env:
            - name: ENVIRONMENT
              value: "production"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: database-secrets
                  key: url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: cache-secrets
                  key: url
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: secret-key
          
          # Resource limits
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 2000m
              memory: 4Gi
          
          # Health checks
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          
          # Startup probe for slow starting apps
          startupProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 10
          
          # Security context
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          
          # Volume mounts
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: app-logs
              mountPath: /app/logs
      
      # Volumes
      volumes:
        - name: tmp
          emptyDir: {}
        - name: app-logs
          emptyDir: {}

---
# Service configuration
apiVersion: v1
kind: Service
metadata:
  name: waardhaven-api-service
  namespace: production
  labels:
    app: waardhaven-api
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: http
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8000
      protocol: TCP
      name: http
  selector:
    app: waardhaven-api

---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: waardhaven-api-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: waardhaven-api
  minReplicas: 5
  maxReplicas: 50
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
```

### Data Processing Services
```yaml
# k8s/data-processing/kafka-cluster.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: waardhaven-kafka
  namespace: data-processing
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
        authentication:
          type: tls
    
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
      inter.broker.protocol.version: "3.6"
      log.retention.hours: 168  # 7 days
      log.segment.bytes: 1073741824  # 1GB
      auto.create.topics.enable: false
      
    storage:
      type: jbod
      volumes:
        - id: 0
          type: persistent-claim
          size: 1000Gi
          storageClass: gp3
          deleteClaim: false
    
    resources:
      requests:
        memory: 8Gi
        cpu: 2000m
      limits:
        memory: 16Gi
        cpu: 4000m
    
    # JVM configuration
    jvmOptions:
      -Xms: 4g
      -Xmx: 8g
      -XX:+UseG1GC
      -XX:MaxGCPauseMillis: 20
      -XX:InitiatingHeapOccupancyPercent: 35
    
    # Metrics
    metricsConfig:
      type: jmxPrometheusExporter
      valueFrom:
        configMapKeyRef:
          name: kafka-metrics
          key: kafka-metrics-config.yml
  
  zookeeper:
    replicas: 3
    
    storage:
      type: persistent-claim
      size: 100Gi
      storageClass: gp3
      deleteClaim: false
    
    resources:
      requests:
        memory: 2Gi
        cpu: 500m
      limits:
        memory: 4Gi
        cpu: 1000m
    
    # Metrics
    metricsConfig:
      type: jmxPrometheusExporter
      valueFrom:
        configMapKeyRef:
          name: kafka-metrics
          key: zookeeper-metrics-config.yml
  
  entityOperator:
    topicOperator: {}
    userOperator: {}

---
# Kafka Topics
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: market-data-stream
  namespace: data-processing
  labels:
    strimzi.io/cluster: waardhaven-kafka
spec:
  partitions: 12
  replicas: 3
  config:
    retention.ms: 604800000  # 7 days
    segment.ms: 86400000     # 1 day
    compression.type: lz4
    cleanup.policy: delete

---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: news-sentiment-stream
  namespace: data-processing
  labels:
    strimzi.io/cluster: waardhaven-kafka
spec:
  partitions: 6
  replicas: 3
  config:
    retention.ms: 2592000000  # 30 days
    segment.ms: 86400000      # 1 day
    compression.type: gzip
    cleanup.policy: delete
```

## 🌐 Network Architecture

### Load Balancing & Traffic Management
```yaml
# k8s/networking/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: waardhaven-ingress
  namespace: production
  annotations:
    # AWS Load Balancer Controller
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/backend-protocol: HTTP
    
    # SSL/TLS
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:123456789:certificate/cert-id
    alb.ingress.kubernetes.io/ssl-policy: ELBSecurityPolicy-TLS-1-2-2017-01
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    
    # Health checks
    alb.ingress.kubernetes.io/healthcheck-path: /health
    alb.ingress.kubernetes.io/healthcheck-interval-seconds: '10'
    alb.ingress.kubernetes.io/healthcheck-timeout-seconds: '5'
    alb.ingress.kubernetes.io/healthy-threshold-count: '2'
    alb.ingress.kubernetes.io/unhealthy-threshold-count: '3'
    
    # Traffic distribution
    alb.ingress.kubernetes.io/target-group-attributes: |
      stickiness.enabled=false,
      load_balancing.algorithm.type=least_outstanding_requests,
      deregistration_delay.timeout_seconds=30
    
    # Rate limiting
    nginx.ingress.kubernetes.io/rate-limit: "1000"
    nginx.ingress.kubernetes.io/rate-limit-burst: "2000"
    
spec:
  tls:
    - hosts:
        - api.waardhaven.com
        - app.waardhaven.com
      secretName: waardhaven-tls
  
  rules:
    # API endpoints
    - host: api.waardhaven.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: waardhaven-api-service
                port:
                  number: 80
    
    # Web application
    - host: app.waardhaven.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: waardhaven-web-service
                port:
                  number: 80

---
# Service Mesh Configuration (Istio)
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: waardhaven-api-vs
  namespace: production
spec:
  hosts:
    - api.waardhaven.com
  gateways:
    - waardhaven-gateway
  http:
    # API versioning
    - match:
        - uri:
            prefix: "/v1/"
      route:
        - destination:
            host: waardhaven-api-service
            subset: v1
          weight: 100
    
    # Health checks
    - match:
        - uri:
            exact: "/health"
      route:
        - destination:
            host: waardhaven-api-service
      timeout: 5s
    
    # Rate limiting
    - match:
        - uri:
            prefix: "/api/"
      route:
        - destination:
            host: waardhaven-api-service
      fault:
        delay:
          percentage:
            value: 0.1
          fixedDelay: 5s
```

## 📊 Auto-Scaling Configuration

### Cluster Autoscaler
```yaml
# k8s/autoscaling/cluster-autoscaler.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
  labels:
    app: cluster-autoscaler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
      annotations:
        prometheus.io/scrape: 'true'
        prometheus.io/port: '8085'
    spec:
      serviceAccountName: cluster-autoscaler
      containers:
        - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.28.0
          name: cluster-autoscaler
          resources:
            limits:
              cpu: 100m
              memory: 300Mi
            requests:
              cpu: 100m
              memory: 300Mi
          command:
            - ./cluster-autoscaler
            - --v=4
            - --stderrthreshold=info
            - --cloud-provider=aws
            - --skip-nodes-with-local-storage=false
            - --expander=least-waste
            - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/waardhaven-prod
            - --balance-similar-node-groups
            - --scale-down-enabled=true
            - --scale-down-delay-after-add=10m
            - --scale-down-unneeded-time=10m
            - --scale-down-utilization-threshold=0.5
            - --skip-nodes-with-system-pods=false
          volumeMounts:
            - name: ssl-certs
              mountPath: /etc/ssl/certs/ca-certificates.crt
              readOnly: true
          imagePullPolicy: "Always"
      volumes:
        - name: ssl-certs
          hostPath:
            path: "/etc/ssl/certs/ca-bundle.crt"

---
# Vertical Pod Autoscaler
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: waardhaven-api-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: waardhaven-api
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
      - containerName: api
        minAllowed:
          cpu: 100m
          memory: 128Mi
        maxAllowed:
          cpu: 4000m
          memory: 8Gi
        controlledResources: ["cpu", "memory"]
```

## 📈 Cost Optimization Strategies

```yaml
# Cost optimization configuration
cost_optimization:
  spot_instances:
    # Use spot instances for non-critical workloads
    batch_processing: 80%  # 80% spot, 20% on-demand
    development: 100%      # 100% spot for dev environments
    ml_training: 90%       # 90% spot for training jobs
    
  reserved_instances:
    # Reserved instances for predictable workloads
    database: 100%         # 3-year reserved for stability
    api_baseline: 60%      # Cover baseline capacity
    cache: 100%           # Redis clusters
    
  scheduled_scaling:
    # Scale down during off-hours
    development:
      scale_down: "18:00"  # 6 PM EST
      scale_up: "08:00"    # 8 AM EST
      weekend_scale: 0     # Scale to 0 on weekends
    
    staging:
      scale_down: "20:00"  # 8 PM EST
      scale_up: "07:00"    # 7 AM EST
      
  storage_optimization:
    # Intelligent tiering for S3
    data_lake:
      frequent_access: 30 days    # Keep in S3 Standard
      infrequent_access: 90 days  # Move to S3 IA
      archive: 365 days          # Move to Glacier
      deep_archive: 2555 days    # Move to Deep Archive (7 years)
```

## 🔒 Security & Compliance

### Network Security
```yaml
# k8s/security/network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: waardhaven-api
  policyTypes:
    - Ingress
    - Egress
  
  ingress:
    # Allow traffic from load balancer
    - from:
        - namespaceSelector:
            matchLabels:
              name: kube-system
      ports:
        - protocol: TCP
          port: 8000
    
    # Allow traffic from other API pods
    - from:
        - podSelector:
            matchLabels:
              app: waardhaven-api
      ports:
        - protocol: TCP
          port: 8000
  
  egress:
    # Allow DNS resolution
    - to: []
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
    
    # Allow database access
    - to:
        - namespaceSelector:
            matchLabels:
              name: database
      ports:
        - protocol: TCP
          port: 5432
    
    # Allow cache access
    - to:
        - namespaceSelector:
            matchLabels:
              name: cache
      ports:
        - protocol: TCP
          port: 6379
    
    # Allow external API calls (HTTPS only)
    - to: []
      ports:
        - protocol: TCP
          port: 443

---
# Pod Security Policy
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: waardhaven-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Deployment frequency | Daily | - |
| Service availability | >99.9% | - |
| Auto-scaling response time | <2 minutes | - |
| Container startup time | <30 seconds | - |
| Cost per user per month | <$5 | - |

---

**Next**: Continue with data pipeline infrastructure design.