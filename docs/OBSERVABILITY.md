# TaskTracker Observability Extension

This extension adds Prometheus and Grafana to the TaskTracker architecture.

## What was added

- `/metrics` endpoint in `task-service`
- `/metrics` endpoint in `user-service`
- Prometheus scraping configuration in `monitoring/prometheus.yml`
- Grafana service in Docker Compose
- Pre-provisioned Prometheus datasource
- Pre-provisioned Grafana dashboard
- Business metrics:
  - `tasktracker_tasks_created_total`
  - `tasktracker_tasks_updated_total`
  - `tasktracker_tasks_deleted_total`
  - `tasktracker_users_created_total`

## Run locally

```bash
docker compose up --build
```

Open:

- Frontend: http://localhost:8080
- Task service metrics: http://localhost:5001/metrics
- User service metrics: http://localhost:5002/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Grafana login:

- Username: `admin`
- Password: `admin`

The dashboard is available under the folder `TaskTracker` with the name `TaskTracker Observability`.

## Prometheus checks

In Prometheus, test these queries:

```promql
up
flask_http_request_total
tasktracker_tasks_created_total
tasktracker_users_created_total
```

## Architecture explanation

The TaskTracker system was extended with an observability layer. Both backend services expose metrics through a `/metrics` endpoint. Prometheus periodically scrapes these endpoints and stores time-series data. Grafana connects to Prometheus and visualizes request traffic, error rates, response times, and business metrics. This improves maintainability because developers and operators can detect failures, analyze service behavior, and understand application usage without manually inspecting containers.
