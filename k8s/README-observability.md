# TaskTracker Kubernetes Observability

This Kubernetes extension runs Prometheus and Grafana inside the `task-tracker` namespace.

Prometheus scrapes:

- `task-service:5000/metrics`
- `user-service:5000/metrics`

Grafana is preconfigured with:

- Prometheus datasource
- TaskTracker Observability dashboard

## Apply

```bash
kubectl apply -f k8s/
```

## Check pods

```bash
kubectl get pods -n task-tracker
kubectl get svc -n task-tracker
```

## Port forward

```bash
kubectl port-forward -n task-tracker svc/frontend 8080:80
kubectl port-forward -n task-tracker svc/prometheus 9090:9090
kubectl port-forward -n task-tracker svc/grafana 3000:3000
```

Open:

- Frontend: http://localhost:8080
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Grafana login:

- username: `admin`
- password: `admin`

Dashboard:

- Dashboards -> TaskTracker -> TaskTracker Observability - Kubernetes

## Prometheus test queries

```promql
up
flask_http_request_total
tasktracker_tasks_created_total
tasktracker_users_created_total
```
