# TaskTracker Run Modes

This project can be started in two ways:

1. **Docker Compose** for local development.
2. **Kubernetes** for container orchestration.

Both modes include the observability extension with **Prometheus** and **Grafana**.

---

## Option 1: Run with Docker Compose

From the project root:

```bash
docker compose up --build
```

Open these URLs:

- Frontend: http://localhost:8080
- Task service metrics: http://localhost:5001/metrics
- User service metrics: http://localhost:5002/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Grafana login:

- Username: `admin`
- Password: `admin`

Dashboard:

```text
Dashboards -> TaskTracker -> TaskTracker Observability
```

Stop Docker Compose:

```bash
docker compose down
```

To also delete the local database and Grafana data volumes:

```bash
docker compose down -v
```

---

## Option 2: Run with Kubernetes using Minikube

Start Minikube:

```bash
minikube start
```

Build images inside Minikube's Docker environment:

```bash
eval $(minikube docker-env)
docker build -t tasktracker-task-service:latest ./task-service
docker build -t tasktracker-user-service:latest ./user-service
docker build -t tasktracker-frontend:latest ./frontend
```

Deploy everything:

```bash
kubectl apply -f k8s/
```

Check pods:

```bash
kubectl get pods -n task-tracker
```

Access the services with port forwarding.

Frontend:

```bash
kubectl port-forward -n task-tracker svc/frontend 8080:80
```

Prometheus:

```bash
kubectl port-forward -n task-tracker svc/prometheus 9090:9090
```

Grafana:

```bash
kubectl port-forward -n task-tracker svc/grafana 3000:3000
```

Open:

- Frontend: http://localhost:8080
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Grafana login:

- Username: `admin`
- Password: `admin`

Dashboard:

```text
Dashboards -> TaskTracker -> TaskTracker Observability - Kubernetes
```

Delete the Kubernetes deployment:

```bash
kubectl delete -f k8s/
```

---

## Useful Prometheus queries

```promql
up
```

```promql
flask_http_request_total
```

```promql
tasktracker_tasks_created_total
```

```promql
tasktracker_tasks_updated_total
```

```promql
tasktracker_tasks_deleted_total
```

```promql
tasktracker_users_created_total
```

---

## Architecture summary

The application services expose metrics on `/metrics`. Prometheus scrapes those metrics and Grafana visualizes them in dashboards.

```text
Docker Compose mode:
frontend + services + postgres + prometheus + grafana

Kubernetes mode:
namespace task-tracker
  frontend
  task-service
  user-service
  postgres
  prometheus
  grafana
```
