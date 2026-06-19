# Kubernetes Observability

This Kubernetes deployment includes Prometheus, Grafana, and kube-state-metrics.

## Components

- `task-service` exposes application metrics at `/metrics`
- `user-service` exposes application metrics at `/metrics`
- `prometheus` scrapes the backend services and kube-state-metrics
- `grafana` visualizes application and Kubernetes metrics
- `kube-state-metrics` exposes Kubernetes object state such as pods and HPA

## Simple dashboard scope

The Grafana dashboard intentionally focuses only on the most meaningful metrics:

### Application metrics

- services up
- request rate
- error rate
- average response time
- task counters
- user counters

### Kubernetes metrics

- pod status
- pod restarts
- HPA current replicas
- HPA desired replicas

## Run

```bash
minikube start
minikube addons enable metrics-server
eval $(minikube docker-env)

docker build -t tasktracker-task-service:latest ./task-service
docker build -t tasktracker-user-service:latest ./user-service
docker build -t tasktracker-frontend:latest ./frontend

kubectl apply -f k8s/
```

## Access

```bash
kubectl port-forward -n task-tracker svc/frontend 8080:80
kubectl port-forward -n task-tracker svc/prometheus 9090:9090
kubectl port-forward -n task-tracker svc/grafana 3000:3000
```

Grafana:

```text
http://localhost:3000
admin / admin
```

## Explanation

Prometheus collects two kinds of metrics. First, it scrapes application metrics from the task-service and user-service. Second, it scrapes Kubernetes state metrics from kube-state-metrics. Grafana displays only the most important indicators so the dashboard stays easy to understand during the presentation.
