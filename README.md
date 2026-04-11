# Niraj Byanjankar — Portfolio Website

A professional portfolio built with **Flask**, featuring a dark tech theme, Gmail contact form, Docker containerization, Jenkins CI/CD pipeline, Kubernetes scalable deployment with load balancing, and Prometheus + Grafana monitoring.

---

## Table of Contents
1. [Project Structure](#project-structure)
2. [Gmail Setup (Contact Form)](#gmail-setup)
3. [Option A — Run Locally](#option-a--run-locally)
4. [Option B — Docker](#option-b--docker)
5. [Option C — Docker Compose](#option-c--docker-compose)
6. [Option D — Jenkins CI/CD Pipeline](#option-d--jenkins-cicd-pipeline)
7. [Option E — Kubernetes (Scalable + Load Balanced)](#option-e--kubernetes)
8. [Option F — Monitoring (Prometheus + Grafana)](#option-f--monitoring)
9. [Full CI/CD + K8s Flow](#full-cicd--k8s-flow)
10. [Environment Variables](#environment-variables)

---

## Project Structure

```
portfolio/
├── app.py                    <- Flask app + Gmail contact form + /metrics endpoint
├── requirements.txt          <- Python dependencies (incl. Gunicorn, prometheus-flask-exporter)
├── Dockerfile                <- Multi-stage Docker build
├── docker-compose.yml        <- Local Docker Compose (app + Prometheus + Grafana)
├── Jenkinsfile               <- Jenkins CI/CD pipeline definition
├── .dockerignore             <- Files excluded from Docker image
├── .gitignore                <- Files excluded from Git
├── .env.example              <- Environment variable template
├── monitoring/
│   ├── prometheus.yml        <- Prometheus scrape config for Docker Compose
│   └── grafana/
│       └── provisioning/
│           ├── datasources/
│           │   └── prometheus.yml    <- Auto-wires Prometheus as Grafana datasource
│           └── dashboards/
│               ├── dashboard.yml     <- Dashboard provider config
│               └── portfolio.json    <- Pre-built Flask metrics dashboard
├── k8s/
│   ├── namespace.yaml        <- K8s namespace (apply first)
│   ├── configmap.yaml        <- Non-sensitive config (GMAIL_USER etc.)
│   ├── secret.yaml           <- Secret template (do not commit real values)
│   ├── deployment.yaml       <- 3-replica deployment with Prometheus annotations
│   ├── service.yaml          <- LoadBalancer service (distributes traffic)
│   ├── hpa.yaml              <- Auto-scales pods 2-10 based on CPU/RAM
│   ├── ingress.yaml          <- Domain + HTTPS routing (optional)
│   └── monitoring/
│       ├── namespace.yaml          <- monitoring namespace
│       ├── prometheus-rbac.yaml    <- ServiceAccount + ClusterRole for pod discovery
│       ├── prometheus-configmap.yaml <- Prometheus scrape config
│       ├── prometheus-deployment.yaml <- Prometheus pod + ClusterIP service
│       ├── grafana-configmap.yaml  <- Grafana datasource + dashboard provisioning
│       └── grafana-deployment.yaml <- Grafana pod + NodePort service (port 32000)
├── templates/
│   ├── base.html             <- Navbar, footer, layout
│   └── index.html            <- All portfolio sections
└── static/
    ├── css/style.css         <- Dark tech theme
    └── js/main.js            <- Animations, contact form
```

---

## Gmail Setup

The contact form sends messages to your Gmail inbox via App Password (no OAuth needed).

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Search for **"App Passwords"** and open it
4. Select **Mail** -> **Other** -> name it `Portfolio` -> click **Generate**
5. Copy the 16-character password (remove spaces)
6. Use it as `GMAIL_APP_PASSWORD` in your `.env` file

---

## Option A — Run Locally

**Requirements:** Python 3.9+

```bash
# 1. Clone the repo
git clone https://github.com/imlearningai25/portfolio.git
cd portfolio

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and fill in GMAIL_USER, GMAIL_APP_PASSWORD, SECRET_KEY

# 5. Run
python app.py
```

Open **http://localhost:5000**

---

## Option B — Docker

**Requirements:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
# Build the image
docker build -t imlearningai25/portfolio:latest .

# Run the container
docker run -d \
  --name portfolio \
  --restart unless-stopped \
  -p 5000:5000 \
  -e GMAIL_USER=nirajbjk@gmail.com \
  -e GMAIL_APP_PASSWORD=your_app_password \
  -e SECRET_KEY=your_secret_key \
  imlearningai25/portfolio:latest
```

Open **http://localhost:5000**

**Useful commands:**
```bash
docker logs -f portfolio       # view logs
docker stop portfolio          # stop
docker rm portfolio            # remove
docker build -t imlearningai25/portfolio:latest . && docker restart portfolio  # rebuild
```

---

## Option C — Docker Compose

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env with your Gmail credentials

# 2. Start
docker compose up -d --build

# 3. Stop
docker compose down

# 4. View logs
docker compose logs -f
```

Open **http://localhost:5000**

---

## Option D — Jenkins CI/CD Pipeline

Jenkins automates the full build -> test -> push -> deploy cycle every time you push code to GitHub.

### Step 1 — Install Jenkins

```bash
# Run Jenkins in Docker (easiest approach)
docker run -d \
  --name jenkins \
  --restart unless-stopped \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts

# Get the initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open **http://localhost:8080**, paste the password, and install suggested plugins.

### Step 2 — Install Required Jenkins Plugins

Go to **Manage Jenkins -> Plugins -> Available** and install:

| Plugin | Purpose |
|--------|---------|
| Git Plugin | Clone from GitHub |
| Docker Pipeline | Build and push Docker images |
| Kubernetes CLI | Run kubectl commands |
| Credentials Binding | Inject secrets safely into pipeline |
| Pipeline | Declarative pipeline support |

### Step 3 — Add Jenkins Credentials

Go to **Manage Jenkins -> Credentials -> Global -> Add Credential** and create these three:

| Credential ID | Type | What to enter |
|---|---|---|
| `dockerhub-credentials` | Username with password | Your Docker Hub username and password |
| `kubeconfig` | Secret file | Upload your `~/.kube/config` file |
| `gmail-app-password` | Secret text | Your 16-char Gmail App Password |

### Step 4 — Create the Pipeline Job

1. Click **New Item** -> name it `portfolio` -> choose **Pipeline** -> click OK
2. Under **Pipeline**, select **Pipeline script from SCM**
3. Set SCM to **Git** and enter your repo URL:
   `https://github.com/imlearningai25/portfolio.git`
4. Set **Script Path** to `Jenkinsfile`
5. Click **Save**

### Step 5 — Push Your Image to Docker Hub

Make sure you have a Docker Hub account. The pipeline uses the `dockerhub-credentials` you added in Step 3 to push automatically.

### Step 6 — Trigger a Build

**Manual:** Click **Build Now** inside the pipeline job.

**Automatic (recommended):** Add a GitHub webhook so every push triggers Jenkins automatically:

1. In your GitHub repo: **Settings -> Webhooks -> Add webhook**
2. Payload URL: `http://YOUR_JENKINS_SERVER_IP:8080/github-webhook/`
3. Content type: `application/json`
4. Event: **Just the push event**
5. Click **Add webhook**

### What Each Pipeline Stage Does

```
git push to GitHub
       |
       v
Jenkins picks up the push (webhook)
       |
       v
Stage 1: Checkout    -- pulls the latest code
Stage 2: Lint        -- checks Python syntax + validates YAML files
Stage 3: Build Image -- docker build, tagged with build number (e.g. :42)
Stage 4: Push Image  -- docker push to Docker Hub (:42 and :latest)
Stage 5: Deploy K8s  -- kubectl apply all manifests to the cluster
Stage 6: Verify      -- waits for rollout to complete, shows pod status
```

---

## Option E — Kubernetes

Kubernetes runs multiple copies (pods) of the app across nodes and automatically balances traffic between them.

### Prerequisites

Choose a cluster (pick one):

| Option | Command to install |
|--------|-------------------|
| **minikube** (local) | [minikube.sigs.k8s.io/docs/start](https://minikube.sigs.k8s.io/docs/start/) |
| **kind** (local) | `brew install kind` or see [kind.sigs.k8s.io](https://kind.sigs.k8s.io) |
| **GKE** (Google Cloud) | `gcloud container clusters create portfolio-cluster` |
| **EKS** (AWS) | `eksctl create cluster --name portfolio` |
| **AKS** (Azure) | `az aks create --name portfolio` |

You also need `kubectl` installed: [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/)

### Step 1 — Install Metrics Server (required for HPA auto-scaling)

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify it started
kubectl get pods -n kube-system | grep metrics-server
```

### Step 2 — Push Your Docker Image

```bash
docker build -t imlearningai25/portfolio:latest .
docker login
docker push imlearningai25/portfolio:latest
```

### Step 3 — Create the Secret (sensitive credentials)

```bash
kubectl create secret generic portfolio-secret \
  --from-literal=GMAIL_APP_PASSWORD='your_16_char_app_password' \
  --from-literal=SECRET_KEY='your_long_random_secret_key' \
  --namespace=portfolio
```

> Never commit real values to Git. The `k8s/secret.yaml` file in this repo is a template only. Always use the kubectl command above for real deployments.

### Step 4 — Set Your Image in deployment.yaml

Open `k8s/deployment.yaml` and replace `IMAGE_PLACEHOLDER` with your image tag:

```yaml
image: imlearningai25/portfolio:latest
```

### Step 5 — Apply All Manifests

```bash
# Apply in this exact order:
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml     # Optional — needs Ingress controller
```

### Step 6 — Check Everything Is Running

```bash
# Watch pods come up (Ctrl+C to stop watching)
kubectl get pods -n portfolio -w

# Get the external IP for the LoadBalancer
kubectl get svc -n portfolio

# Check auto-scaler status
kubectl get hpa -n portfolio

# View logs across all pods
kubectl logs -l app=portfolio -n portfolio --tail=50
```

### Step 7 — Open the App

**Cloud (GKE / EKS / AKS):**
```bash
kubectl get svc portfolio-service -n portfolio
# Copy the EXTERNAL-IP value and open http://EXTERNAL-IP in your browser
```

**minikube (local):**
```bash
minikube service portfolio-service -n portfolio
# minikube opens the URL in your browser automatically
```

### Step 8 — Optional: Enable HTTPS with Ingress

Install the NGINX Ingress controller:
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/cloud/deploy.yaml
```

Install cert-manager for free SSL certificates:
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
```

Edit `k8s/ingress.yaml` and replace `your-domain.com` with your actual domain, then apply it:
```bash
kubectl apply -f k8s/ingress.yaml
```

### How Load Balancing Works

```
All internet traffic hits one entry point
              |
              v
  Kubernetes LoadBalancer Service
              |
    __________|___________
   |           |          |
   v           v          v
 Pod 1       Pod 2      Pod 3     <- Identical copies of the Flask app
(Node A)    (Node B)   (Node C)   <- Spread across different machines
```

Kubernetes automatically routes each request to whichever pod is least busy. If a pod crashes, traffic is rerouted to the remaining pods instantly.

### How Auto-Scaling Works

```
Low traffic:   2 pods running  (minimum)
Traffic spike: CPU goes above 70%
               HPA adds 2 pods -> now 4 pods
               CPU goes above 70% again
               HPA adds 2 more pods -> now 6 pods  (max 10)

Traffic drops: CPU falls below 70% for 5 minutes
               HPA removes 1 pod at a time -> back to 2 pods
```

---

## Option F — Monitoring

The portfolio app exposes Prometheus metrics at `/metrics` (via `prometheus-flask-exporter`). Prometheus scrapes those metrics and Grafana visualises them in a pre-built dashboard.

### What is monitored

| Metric | Description |
| ------ | ----------- |
| `flask_http_request_total` | Total HTTP requests by method, path, status code |
| `flask_http_request_duration_seconds` | Request latency histogram (p50 / p95 / p99) |
| `flask_http_request_exceptions_total` | Unhandled exceptions by endpoint |
| `app_info` | Static label with app version |

### Option F1 — Docker Compose (local)

The `docker-compose.yml` already includes Prometheus and Grafana alongside the app. No extra steps are needed.

```bash
# Start the full stack (app + Prometheus + Grafana)
docker compose up -d --build

# Verify all three services are running
docker compose ps
```

| Service | URL | Credentials |
| ------- | --- | ----------- |
| Portfolio app | <http://localhost:5000> | — |
| Prometheus | <http://localhost:9090> | — |
| Grafana | <http://localhost:3000> | admin / admin |

**Verify metrics are flowing:**

```bash
# Check the /metrics endpoint directly
curl http://localhost:5000/metrics

# In Prometheus UI → Status → Targets
# The "portfolio" target should show State: UP
```

**Open the dashboard:**

1. Open <http://localhost:3000> and log in with `admin / admin`
2. Go to **Dashboards → Portfolio → Portfolio App Metrics**
3. The dashboard auto-loads with four panels: Request Rate, Error Rate, p99 Latency, Total Requests — plus time-series graphs for status codes, latency percentiles, and per-endpoint traffic.

---

### Option F2 — Kubernetes

#### Step 1 — Deploy the monitoring namespace and RBAC

```bash
kubectl apply -f k8s/monitoring/namespace.yaml
kubectl apply -f k8s/monitoring/prometheus-rbac.yaml
```

The ClusterRole grants Prometheus read access to pods/endpoints/services across all namespaces so it can auto-discover scrape targets.

#### Step 2 — Deploy Prometheus

```bash
kubectl apply -f k8s/monitoring/prometheus-configmap.yaml
kubectl apply -f k8s/monitoring/prometheus-deployment.yaml
```

Prometheus uses Kubernetes pod-annotation discovery. Any pod with these annotations is automatically scraped (the portfolio deployment already has them):

```yaml
prometheus.io/scrape: "true"
prometheus.io/port:   "5000"
prometheus.io/path:   "/metrics"
```

#### Step 3 — Deploy Grafana

```bash
kubectl apply -f k8s/monitoring/grafana-configmap.yaml
kubectl apply -f k8s/monitoring/grafana-deployment.yaml
```

Grafana starts with the Prometheus datasource and the Portfolio dashboard pre-loaded via provisioning ConfigMaps.

#### Step 4 — Verify everything is running

```bash
# Check all monitoring pods are Running
kubectl get pods -n monitoring

# Check services
kubectl get svc -n monitoring
```

Expected output:

```
NAME                 TYPE        CLUSTER-IP    PORT(S)
prometheus-service   ClusterIP   10.x.x.x      9090/TCP
grafana-service      NodePort    10.x.x.x      3000:32000/TCP
```

#### Step 5 — Access the UIs

**Grafana (NodePort 32000):**

```bash
# minikube
minikube service grafana-service -n monitoring

# Cloud / bare-metal — use the node IP
kubectl get nodes -o wide
# Open http://NODE_IP:32000  →  admin / admin
```

**Prometheus (port-forward for internal access):**

```bash
kubectl port-forward svc/prometheus-service 9090:9090 -n monitoring
# Open http://localhost:9090
```

Confirm portfolio targets are UP: **Prometheus UI → Status → Targets → kubernetes-pods**

#### Step 6 — Open the dashboard

1. Log in to Grafana at the NodePort URL with `admin / admin`
2. Navigate to **Dashboards → Portfolio → Portfolio App Metrics**

### Monitoring architecture

```
Portfolio pods (3 replicas)
  │  expose /metrics on port 5000
  │
  ▼
Prometheus (monitoring namespace)
  │  scrapes every 15 s via pod-annotation discovery
  │  stores 15 days of TSDB data
  │
  ▼
Grafana (monitoring namespace)
  │  auto-provisioned datasource + dashboard
  │  NodePort 32000
  ▼
Browser → Dashboard showing RPS, latency, errors, per-endpoint traffic
```

---

## Full CI/CD + K8s Flow

```
You write code and push to GitHub
              |
              v
GitHub sends webhook to Jenkins
              |
              v
Jenkins pipeline runs automatically:
  1. Pull latest code
  2. Check syntax and validate YAML
  3. Build Docker image  (tagged :build-number)
  4. Push image to Docker Hub
  5. Update Kubernetes deployment
              |
              v
Kubernetes performs rolling update (zero downtime):
  - Starts new pods with new image
  - Only removes old pods once new ones are healthy
              |
              v
HPA monitors CPU/RAM and scales pods 2-10 automatically
              |
              v
LoadBalancer distributes traffic across all healthy pods
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GMAIL_USER` | Yes | Your Gmail address |
| `GMAIL_APP_PASSWORD` | Yes | 16-char Gmail App Password (no spaces) |
| `SECRET_KEY` | Yes | Long random string for Flask session signing |

Copy `.env.example` to `.env` and fill these in. Never commit `.env` to Git.

---

## Tech Stack

| Layer | Technology |
| ----- | ---------- |
| Backend | Python 3.11, Flask 3.0 |
| WSGI Server | Gunicorn |
| Email | Flask-Mail + Gmail SMTP |
| Frontend | HTML5, CSS3, Vanilla JS |
| Container | Docker (multi-stage build) |
| Orchestration | Docker Compose / Kubernetes |
| CI/CD | Jenkins (declarative pipeline) |
| Load Balancing | Kubernetes LoadBalancer Service |
| Auto-scaling | Kubernetes HPA (2-10 pods) |
| Ingress / SSL | NGINX Ingress + cert-manager |
| Metrics collection | Prometheus v2.51 |
| Metrics visualisation | Grafana v10.4 |
