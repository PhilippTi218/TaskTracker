# TaskTracker - Run Modes with Observability

This project can be run in two ways:

1. Docker Compose for local development and demos
2. Kubernetes for a production-like deployment with autoscaling and Kubernetes monitoring

Both modes run the same application architecture:

```text
Frontend -> Task Service / User Service -> PostgreSQL
```

Both backend services expose:

```text
/health
/metrics
```

Prometheus scrapes the metrics and Grafana visualizes them.

---

## Option 1: Run with Docker Compose

Use this mode for a quick local demo.

```bash
docker compose up --build
```

Open:

```text
Frontend:    http://localhost:8080
Prometheus:  http://localhost:9090
Grafana:     http://localhost:3000
```

Grafana login:

```text
admin / admin
```

The Docker Compose dashboard focuses on application metrics:

- services up
- request rate
- error rate
- average response time
- tasks created / updated / deleted
- users created

---

## Option 2: Run with Kubernetes on Minikube

Use this mode to show a production-like architecture.

```bash
minikube start
minikube addons enable metrics-server
eval $(minikube docker-env)

docker build -t tasktracker-task-service:latest ./task-service
docker build -t tasktracker-user-service:latest ./user-service
docker build -t tasktracker-frontend:latest ./frontend

kubectl apply -f k8s/
```

Check the pods:

```bash
kubectl get pods -n task-tracker
```

Access the services locally:

```bash
kubectl port-forward -n task-tracker svc/frontend 8080:80
kubectl port-forward -n task-tracker svc/prometheus 9090:9090
kubectl port-forward -n task-tracker svc/grafana 3000:3000
```

Open:

```text
Frontend:    http://localhost:8080
Prometheus:  http://localhost:9090
Grafana:     http://localhost:3000
```

Grafana login:

```text
admin / admin
```

---

## Kubernetes monitoring scope

To keep the dashboard simple, the Kubernetes dashboard monitors only the most meaningful runtime metrics:

- pod status
- pod restarts
- HPA current replicas
- HPA desired replicas

This is intentionally not a full Kubernetes operations dashboard. The goal is to show the most important architectural idea: the system is observable at both application level and Kubernetes deployment level.

---

## Important Prometheus queries

Application metrics:

```promql
up
sum by (job) (rate(flask_http_request_total[1m]))
sum by (job) (rate(flask_http_request_total{status=~"5.."}[1m]))
sum(tasktracker_tasks_created_total)
sum(tasktracker_users_created_total)
```

Kubernetes metrics:

```promql
sum by (phase) (kube_pod_status_phase{namespace="task-tracker"})
sum by (pod) (kube_pod_container_status_restarts_total{namespace="task-tracker"})
kube_horizontalpodautoscaler_status_current_replicas{namespace="task-tracker", horizontalpodautoscaler="task-service-hpa"}
kube_horizontalpodautoscaler_status_desired_replicas{namespace="task-tracker", horizontalpodautoscaler="task-service-hpa"}
```

---

## Architecture summary

Docker Compose gives us a simple local development environment. Kubernetes gives us a production-like deployment environment with pods, services, HPA, and kube-state-metrics. Prometheus collects application and Kubernetes metrics. Grafana displays the most important information in one dashboard.
