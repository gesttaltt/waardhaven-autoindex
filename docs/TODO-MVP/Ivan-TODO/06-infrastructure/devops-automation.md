# ⚙️ DevOps Automation - Streamlined Development & Operations

**Priority**: MEDIUM  
**Complexity**: Medium-High  
**Timeline**: 3-4 days  
**Value**: Accelerated development velocity and operational efficiency

## 🎯 Objective

Implement comprehensive DevOps automation that:
- Enables continuous integration and deployment (CI/CD)
- Automates infrastructure provisioning and management
- Ensures consistent environments across development stages
- Facilitates rapid, reliable software delivery
- Supports infrastructure as code practices

## 🔄 CI/CD Pipeline Architecture

### Pipeline Overview
```
┌────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT WORKFLOW                        │
│              "Code to Production Automation"                   │
└──────────────────────┬─────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────┼────┐   ┌────┼────┐   ┌────┼────┐
    │SOURCE │   │BUILD │   │TEST  │
    │CONTROL│   │COMPILE│   │QUALITY│
    └─────────┘   └─────────┘   └─────────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
┌──────────────────────┼────────────────────────────────────────┐
│                 DEPLOYMENT PIPELINE                           │
│           "Automated Environment Promotion"                   │
└──────────────────────┬────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────┼────┐   ┌────┼────┐   ┌────┼────┐
    │STAGING│   │CANARY │   │PROD  │
    │DEPLOY │   │DEPLOY │   │DEPLOY│
    └─────────┘   └─────────┘   └─────────┘
```

### GitHub Actions Workflows
```yaml
# .github/workflows/ci-cd-pipeline.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  AWS_REGION: us-east-1

jobs:
  # Code Quality and Security Checks
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better analysis

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Code formatting check
        run: |
          black --check --diff .
          isort --check-only --diff .

      - name: Linting
        run: |
          flake8 .
          pylint **/*.py

      - name: Type checking
        run: mypy .

      - name: Security scanning
        uses: PyCQA/bandit-action@v1
        with:
          path: "."

      - name: Dependency vulnerability scan
        run: |
          pip install safety
          safety check -r requirements.txt

      - name: SAST scanning
        uses: github/codeql-action/init@v2
        with:
          languages: python

      - name: Perform CodeQL analysis
        uses: github/codeql-action/analyze@v2

  # Unit and Integration Tests
  test:
    runs-on: ubuntu-latest
    needs: code-quality

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_USER: testuser
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run unit tests
        run: |
          pytest tests/unit/ \
            --cov=app \
            --cov-report=xml \
            --cov-report=html \
            --junitxml=test-results.xml
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379/0

      - name: Run integration tests
        run: |
          pytest tests/integration/ \
            --cov-append \
            --cov=app \
            --cov-report=xml
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379/0

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

      - name: Store test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: |
            test-results.xml
            htmlcov/

  # Container Build and Security Scan
  build:
    runs-on: ubuntu-latest
    needs: test
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
      
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Container vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # Deploy to Staging Environment
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Set up Kubernetes
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'

      - name: Update kubeconfig
        run: aws eks update-kubeconfig --name waardhaven-staging --region ${{ env.AWS_REGION }}

      - name: Deploy to staging
        run: |
          # Update image in deployment
          kubectl set image deployment/waardhaven-api \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            --namespace=staging
          
          # Wait for rollout to complete
          kubectl rollout status deployment/waardhaven-api --namespace=staging --timeout=300s

      - name: Run smoke tests
        run: |
          # Wait for service to be ready
          kubectl wait --for=condition=ready pod \
            -l app=waardhaven-api \
            --namespace=staging \
            --timeout=300s
          
          # Run smoke tests
          python scripts/smoke_tests.py --environment=staging

  # Deploy to Production (Canary)
  deploy-production-canary:
    runs-on: ubuntu-latest
    needs: [build, deploy-staging]
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Set up Kubernetes
        uses: azure/setup-kubectl@v3

      - name: Update kubeconfig
        run: aws eks update-kubeconfig --name waardhaven-prod --region ${{ env.AWS_REGION }}

      - name: Deploy canary version
        run: |
          # Apply canary deployment
          envsubst < k8s/canary-deployment.yaml | kubectl apply -f -
        env:
          IMAGE_TAG: ${{ github.sha }}
          CANARY_PERCENTAGE: 10

      - name: Monitor canary deployment
        run: |
          # Monitor canary for 10 minutes
          python scripts/canary_monitor.py --duration=600 --threshold=0.01

      - name: Promote to full production
        run: |
          # Update main deployment
          kubectl set image deployment/waardhaven-api \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            --namespace=production
          
          # Remove canary deployment
          kubectl delete deployment waardhaven-api-canary --namespace=production

  # Post-deployment verification
  post-deployment:
    runs-on: ubuntu-latest
    needs: deploy-production-canary
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Run production health checks
        run: |
          python scripts/health_checks.py --environment=production

      - name: Update deployment status
        uses: deployments@v1
        with:
          step: finish
          token: ${{ secrets.GITHUB_TOKEN }}
          status: ${{ job.status }}
          deployment-id: ${{ needs.deploy-production-canary.outputs.deployment-id }}

      - name: Notify team
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Infrastructure as Code (Terraform Automation)
```yaml
# .github/workflows/terraform.yml
name: Terraform Infrastructure

on:
  push:
    branches: [main]
    paths: ['infrastructure/**']
  pull_request:
    paths: ['infrastructure/**']

env:
  TF_VERSION: 1.6.0
  TF_IN_AUTOMATION: true
  TF_CLI_ARGS: "-no-color"

jobs:
  terraform-plan:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Terraform Format Check
        id: fmt
        run: terraform fmt -check
        working-directory: ./infrastructure

      - name: Terraform Init
        id: init
        run: terraform init
        working-directory: ./infrastructure

      - name: Terraform Validate
        id: validate
        run: terraform validate
        working-directory: ./infrastructure

      - name: Terraform Plan
        id: plan
        run: |
          terraform plan \
            -var-file="environments/${{ github.event.inputs.environment || 'production' }}.tfvars" \
            -out=tfplan
        working-directory: ./infrastructure

      - name: Security scan (tfsec)
        uses: aquasecurity/tfsec-action@v1.0.3
        with:
          working_directory: ./infrastructure

      - name: Cost estimation
        uses: infracost/infracost-gh-action@v1
        with:
          path: ./infrastructure
          terraform_plan_flags: -var-file="environments/production.tfvars"
        env:
          INFRACOST_API_KEY: ${{ secrets.INFRACOST_API_KEY }}

      - name: Comment PR
        uses: actions/github-script@v6
        if: github.event_name == 'pull_request'
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const output = `
            #### Terraform Format and Style 🖌\`${{ steps.fmt.outcome }}\`
            #### Terraform Initialization ⚙️\`${{ steps.init.outcome }}\`
            #### Terraform Validation 🤖\`${{ steps.validate.outcome }}\`
            #### Terraform Plan 📖\`${{ steps.plan.outcome }}\`
            
            <details><summary>Show Plan</summary>
            
            \`\`\`terraform
            ${{ steps.plan.outputs.stdout }}
            \`\`\`
            
            </details>
            
            *Pusher: @${{ github.actor }}, Action: \`${{ github.event_name }}\`*`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            })

  terraform-apply:
    runs-on: ubuntu-latest
    needs: terraform-plan
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Terraform Init
        run: terraform init
        working-directory: ./infrastructure

      - name: Terraform Apply
        run: |
          terraform apply \
            -var-file="environments/production.tfvars" \
            -auto-approve
        working-directory: ./infrastructure

      - name: Update infrastructure documentation
        run: |
          terraform-docs markdown table ./infrastructure > ./docs/infrastructure.md
          git add ./docs/infrastructure.md
          git commit -m "Update infrastructure documentation" || true
          git push || true
```

## 🐳 Container Orchestration

### Docker Configuration
```dockerfile
# Dockerfile
# Multi-stage build for optimized container images

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application code
COPY . .

# Build stage for static assets (if needed)
RUN python manage.py collectstatic --noinput

# Production stage
FROM python:3.11-slim as production

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --from=builder /app .

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app.wsgi:application"]
```

### Kubernetes Deployment Automation
```yaml
# k8s/deployment-template.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: deployment-config
  namespace: ${NAMESPACE}
data:
  deploy.sh: |
    #!/bin/bash
    set -e
    
    # Colors for output
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m' # No Color
    
    echo -e "${GREEN}Starting deployment of ${IMAGE_NAME}:${IMAGE_TAG}${NC}"
    
    # Pre-deployment checks
    echo -e "${YELLOW}Running pre-deployment checks...${NC}"
    
    # Check if namespace exists
    if ! kubectl get namespace ${NAMESPACE} >/dev/null 2>&1; then
        echo -e "${RED}Namespace ${NAMESPACE} does not exist${NC}"
        exit 1
    fi
    
    # Check if deployment exists
    if ! kubectl get deployment ${DEPLOYMENT_NAME} -n ${NAMESPACE} >/dev/null 2>&1; then
        echo -e "${YELLOW}Deployment ${DEPLOYMENT_NAME} does not exist, creating...${NC}"
        kubectl apply -f deployment.yaml
    fi
    
    # Rolling update
    echo -e "${YELLOW}Updating deployment...${NC}"
    kubectl set image deployment/${DEPLOYMENT_NAME} \
        ${CONTAINER_NAME}=${IMAGE_NAME}:${IMAGE_TAG} \
        -n ${NAMESPACE}
    
    # Wait for rollout
    echo -e "${YELLOW}Waiting for rollout to complete...${NC}"
    kubectl rollout status deployment/${DEPLOYMENT_NAME} -n ${NAMESPACE} --timeout=600s
    
    # Post-deployment verification
    echo -e "${YELLOW}Running post-deployment verification...${NC}"
    
    # Wait for pods to be ready
    kubectl wait --for=condition=ready pod \
        -l app=${DEPLOYMENT_NAME} \
        -n ${NAMESPACE} \
        --timeout=300s
    
    # Run health check
    echo -e "${YELLOW}Running health check...${NC}"
    
    # Get service endpoint
    SERVICE_IP=$(kubectl get svc ${SERVICE_NAME} -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -z "$SERVICE_IP" ]; then
        SERVICE_IP=$(kubectl get svc ${SERVICE_NAME} -n ${NAMESPACE} -o jsonpath='{.spec.clusterIP}')
    fi
    
    # Health check with retries
    for i in {1..10}; do
        if curl -f http://${SERVICE_IP}:${SERVICE_PORT}/health; then
            echo -e "${GREEN}Health check passed${NC}"
            break
        else
            echo -e "${YELLOW}Health check failed, retrying in 30s...${NC}"
            sleep 30
        fi
        
        if [ $i -eq 10 ]; then
            echo -e "${RED}Health check failed after 10 attempts${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}Deployment completed successfully${NC}"

---
apiVersion: batch/v1
kind: Job
metadata:
  name: deployment-job-${BUILD_NUMBER}
  namespace: ${NAMESPACE}
spec:
  template:
    spec:
      serviceAccountName: deployment-service-account
      containers:
      - name: deployer
        image: kubectl:latest
        command: ["/bin/bash"]
        args: ["/scripts/deploy.sh"]
        env:
        - name: NAMESPACE
          value: "${NAMESPACE}"
        - name: DEPLOYMENT_NAME
          value: "${DEPLOYMENT_NAME}"
        - name: CONTAINER_NAME
          value: "${CONTAINER_NAME}"
        - name: IMAGE_NAME
          value: "${IMAGE_NAME}"
        - name: IMAGE_TAG
          value: "${IMAGE_TAG}"
        - name: SERVICE_NAME
          value: "${SERVICE_NAME}"
        - name: SERVICE_PORT
          value: "${SERVICE_PORT}"
        volumeMounts:
        - name: scripts
          mountPath: /scripts
      volumes:
      - name: scripts
        configMap:
          name: deployment-config
          defaultMode: 0755
      restartPolicy: Never
  backoffLimit: 3
```

## 🔄 GitOps with ArgoCD

### ArgoCD Application Configuration
```yaml
# argocd/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: waardhaven-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  
  source:
    repoURL: https://github.com/waardhaven/k8s-manifests
    targetRevision: main
    path: apps/waardhaven
    
    # Helm configuration
    helm:
      valueFiles:
        - values-production.yaml
      parameters:
        - name: image.tag
          value: "latest"
        - name: replicaCount
          value: "3"
  
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

  # Health checks
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas

---
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: waardhaven
  namespace: argocd
spec:
  description: Waardhaven Investment Platform
  
  sourceRepos:
    - 'https://github.com/waardhaven/*'
    - 'https://helm.releases.hashicorp.com'
    - 'https://charts.bitnami.com/bitnami'
  
  destinations:
    - namespace: 'production'
      server: https://kubernetes.default.svc
    - namespace: 'staging'
      server: https://kubernetes.default.svc
    - namespace: 'development'
      server: https://kubernetes.default.svc
  
  clusterResourceWhitelist:
    - group: ''
      kind: Namespace
    - group: rbac.authorization.k8s.io
      kind: ClusterRole
    - group: rbac.authorization.k8s.io
      kind: ClusterRoleBinding
  
  namespaceResourceWhitelist:
    - group: ''
      kind: Service
    - group: apps
      kind: Deployment
    - group: networking.k8s.io
      kind: Ingress
```

## 🛠️ Development Environment Automation

### Development Setup Script
```bash
#!/bin/bash
# scripts/setup-dev-environment.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Setting up Waardhaven development environment...${NC}"

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3.11 &> /dev/null; then
        echo -e "${RED}Python 3.11 is not installed. Please install Python 3.11 first.${NC}"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Node.js is not installed. Please install Node.js first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites found${NC}"
}

# Setup Python virtual environment
setup_python_env() {
    echo -e "${YELLOW}Setting up Python environment...${NC}"
    
    if [ ! -d "venv" ]; then
        python3.11 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    
    echo -e "${GREEN}✅ Python environment ready${NC}"
}

# Setup Node.js environment
setup_node_env() {
    echo -e "${YELLOW}Setting up Node.js environment...${NC}"
    
    # Install dependencies for frontend
    cd apps/web
    npm install
    cd ../..
    
    echo -e "${GREEN}✅ Node.js environment ready${NC}"
}

# Setup pre-commit hooks
setup_pre_commit() {
    echo -e "${YELLOW}Setting up pre-commit hooks...${NC}"
    
    source venv/bin/activate
    pre-commit install
    pre-commit install --hook-type commit-msg
    
    echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
}

# Setup development services
setup_dev_services() {
    echo -e "${YELLOW}Setting up development services...${NC}"
    
    # Create .env file from template if it doesn't exist
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Created .env file from template. Please update with your settings.${NC}"
    fi
    
    # Start development services
    docker-compose -f docker-compose.dev.yml up -d
    
    # Wait for services to be ready
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    sleep 10
    
    # Run database migrations
    source venv/bin/activate
    python manage.py migrate
    
    # Create superuser if it doesn't exist
    python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Created admin user')
else:
    print('Admin user already exists')
"
    
    echo -e "${GREEN}✅ Development services ready${NC}"
}

# Setup IDE configuration
setup_ide_config() {
    echo -e "${YELLOW}Setting up IDE configuration...${NC}"
    
    # VS Code settings
    mkdir -p .vscode
    
    cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/node_modules": true,
        "**/.git": true
    }
}
EOF
    
    # VS Code extensions recommendations
    cat > .vscode/extensions.json << EOF
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "ms-python.isort",
        "ms-python.pylint",
        "bradlc.vscode-tailwindcss",
        "esbenp.prettier-vscode",
        "ms-vscode.vscode-typescript-next",
        "ms-kubernetes-tools.vscode-kubernetes-tools",
        "redhat.vscode-yaml",
        "hashicorp.terraform"
    ]
}
EOF
    
    echo -e "${GREEN}✅ IDE configuration ready${NC}"
}

# Main setup function
main() {
    check_prerequisites
    setup_python_env
    setup_node_env
    setup_pre_commit
    setup_dev_services
    setup_ide_config
    
    echo -e "${GREEN}🎉 Development environment setup complete!${NC}"
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  1. Update .env file with your configuration"
    echo -e "  2. Activate Python environment: ${YELLOW}source venv/bin/activate${NC}"
    echo -e "  3. Start development server: ${YELLOW}python manage.py runserver${NC}"
    echo -e "  4. Start frontend: ${YELLOW}cd apps/web && npm run dev${NC}"
    echo -e "  5. Access the application at: ${YELLOW}http://localhost:3000${NC}"
    echo -e "  6. Access admin panel at: ${YELLOW}http://localhost:8000/admin${NC}"
    echo -e "     Username: admin, Password: admin123"
}

# Run main function
main "$@"
```

### Development Docker Compose
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: waardhaven_dev
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dev_user -d waardhaven_dev"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # Kafka for development
  kafka:
    image: confluentinc/cp-kafka:7.4.0
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper

  # Zookeeper for Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  # Elasticsearch for logging
  elasticsearch:
    image: elasticsearch:8.9.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  # MailHog for email testing
  mailhog:
    image: mailhog/mailhog:latest
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI

  # Prometheus for metrics (development)
  prometheus:
    image: prom/prometheus:latest
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus-dev.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
  prometheus_data:
```

## 📊 DevOps Metrics & KPIs

### Pipeline Performance Metrics
```python
# monitoring/devops_metrics.py
from prometheus_client import Counter, Histogram, Gauge
from datetime import datetime

# CI/CD Pipeline Metrics
PIPELINE_RUNS = Counter(
    'pipeline_runs_total',
    'Total number of pipeline runs',
    ['pipeline', 'branch', 'result']
)

PIPELINE_DURATION = Histogram(
    'pipeline_duration_seconds',
    'Pipeline execution duration',
    ['pipeline', 'stage']
)

DEPLOYMENT_FREQUENCY = Counter(
    'deployments_total',
    'Total number of deployments',
    ['environment', 'application']
)

LEAD_TIME = Histogram(
    'lead_time_seconds',
    'Lead time from commit to production',
    ['application']
)

MTTR = Histogram(
    'mean_time_to_recovery_seconds',
    'Mean time to recovery from incidents',
    ['severity']
)

CHANGE_FAILURE_RATE = Gauge(
    'change_failure_rate',
    'Percentage of deployments that cause failures',
    ['environment']
)

class DevOpsMetrics:
    """Track DevOps performance metrics"""
    
    def record_pipeline_run(self, pipeline: str, branch: str, result: str, duration: float):
        """Record pipeline execution"""
        PIPELINE_RUNS.labels(
            pipeline=pipeline,
            branch=branch,
            result=result
        ).inc()
        
        PIPELINE_DURATION.labels(
            pipeline=pipeline,
            stage='total'
        ).observe(duration)
    
    def record_deployment(self, environment: str, application: str, lead_time: float):
        """Record deployment event"""
        DEPLOYMENT_FREQUENCY.labels(
            environment=environment,
            application=application
        ).inc()
        
        LEAD_TIME.labels(
            application=application
        ).observe(lead_time)
    
    def record_incident_recovery(self, severity: str, recovery_time: float):
        """Record incident recovery time"""
        MTTR.labels(
            severity=severity
        ).observe(recovery_time)
    
    def update_change_failure_rate(self, environment: str, failure_rate: float):
        """Update change failure rate"""
        CHANGE_FAILURE_RATE.labels(
            environment=environment
        ).set(failure_rate)

# DORA Metrics Calculator
class DORAMetrics:
    """Calculate DORA (DevOps Research and Assessment) metrics"""
    
    def __init__(self):
        self.metrics = DevOpsMetrics()
    
    def calculate_deployment_frequency(self, timeframe_days: int = 30) -> dict:
        """Calculate deployment frequency"""
        # Implementation would query metrics backend
        return {
            'daily_average': 2.3,
            'weekly_average': 16.1,
            'trend': 'increasing'
        }
    
    def calculate_lead_time(self, timeframe_days: int = 30) -> dict:
        """Calculate lead time for changes"""
        return {
            'median_hours': 4.2,
            'p95_hours': 12.5,
            'trend': 'decreasing'
        }
    
    def calculate_mttr(self, timeframe_days: int = 30) -> dict:
        """Calculate mean time to recovery"""
        return {
            'median_minutes': 25,
            'p95_minutes': 120,
            'trend': 'stable'
        }
    
    def calculate_change_failure_rate(self, timeframe_days: int = 30) -> dict:
        """Calculate change failure rate"""
        return {
            'percentage': 2.1,
            'trend': 'decreasing',
            'target': 5.0
        }
```

## 📈 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Deployment frequency | Daily | - |
| Lead time for changes | <4 hours | - |
| Mean time to recovery | <30 minutes | - |
| Change failure rate | <5% | - |
| Pipeline success rate | >95% | - |

---

**Complete**: 06-infrastructure section finished. Moving to 07-implementation-plan section.