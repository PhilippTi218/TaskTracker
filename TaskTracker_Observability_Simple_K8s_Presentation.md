# TaskTracker Observability Presentation

## Topic

**Extension of the TaskTracker architecture with Prometheus, Grafana, Docker Compose, Kubernetes, and simple Kubernetes monitoring.**

The goal of this extension is not to add another normal application feature. The goal is to show that we can manage and improve a software architecture by making the system observable and deployable in different environments.

---

# 1. Short project overview

TaskTracker is a small distributed application with separate services.

```text
User / Browser
      |
      v
Frontend
      |
      v
Task Service       User Service
      \             /
       \           /
        v         v
      PostgreSQL Database
```

The application contains:

- a frontend for the user interface
- a task-service for task operations
- a user-service for user operations
- a PostgreSQL database for persistence
- Docker Compose deployment
- Kubernetes deployment

---

# 2. Problem before the extension

Before the observability extension, the application could run, but the system behavior was difficult to see.

Important questions were hard to answer:

- Are the backend services running?
- How many requests are sent to each service?
- Are there errors?
- How fast are the services responding?
- How many tasks or users were created?
- In Kubernetes, are the pods healthy?
- Is the HPA scaling the task-service correctly?

The architecture had services, containers, and Kubernetes manifests, but it did not have a clear monitoring layer.

---

# 3. Architecture after the extension

We added an observability layer using Prometheus and Grafana.

```text
Task Service /metrics ----                           User Service /metrics ------> Prometheus ---> Grafana Dashboard
                           /
kube-state-metrics --------/
        ^
        |
Kubernetes Pods + HPA
```

The backend services expose metrics through `/metrics` endpoints. Prometheus collects these metrics. Grafana visualizes them in dashboards.

In Kubernetes, we also added kube-state-metrics. This exposes important Kubernetes state information, such as pod status, pod restarts, and HPA replicas.

---

# 4. What we monitor

We intentionally keep the dashboard simple. We do not monitor every Kubernetes object because that would make the presentation too complex.

## Application metrics

These metrics come from the task-service and user-service:

- services up
- request rate
- error rate
- average response time
- tasks created
- tasks updated
- tasks deleted
- users created

## Kubernetes metrics

These metrics come from kube-state-metrics:

- pod status
- pod restarts
- HPA current replicas
- HPA desired replicas

This is enough to answer the most important operational questions:

- Is the application running?
- Are the services stable?
- Is Kubernetes autoscaling working?

---

# 5. Docker Compose deployment

Docker Compose is used for local development and simple demos.

Command:

```bash
docker compose up --build
```

Services started by Docker Compose:

- frontend
- task-service
- user-service
- postgres
- prometheus
- grafana

URLs:

```text
Frontend:    http://localhost:8080
Prometheus:  http://localhost:9090
Grafana:     http://localhost:3000
```

Grafana login:

```text
admin / admin
```

Explanation:

> Docker Compose gives us a simple way to run the complete distributed system on one machine. It is useful for development, testing, and quick demonstrations.

---

# 6. Kubernetes deployment

Kubernetes is used as the production-like deployment mode.

Main Kubernetes resources:

- Namespace
- ConfigMap
- Secret
- Deployments
- Services
- HPA
- Prometheus
- Grafana
- kube-state-metrics

Minikube commands:

```bash
minikube start
minikube addons enable metrics-server
eval $(minikube docker-env)

docker build -t tasktracker-task-service:latest ./task-service
docker build -t tasktracker-user-service:latest ./user-service
docker build -t tasktracker-frontend:latest ./frontend

kubectl apply -f k8s/
```

Check the deployment:

```bash
kubectl get pods -n task-tracker
kubectl get hpa -n task-tracker
```

Port forwarding:

```bash
kubectl port-forward -n task-tracker svc/frontend 8080:80
kubectl port-forward -n task-tracker svc/prometheus 9090:9090
kubectl port-forward -n task-tracker svc/grafana 3000:3000
```

Explanation:

> Kubernetes runs each component as a pod and exposes them through services. The HPA can scale the task-service depending on load. Prometheus and Grafana run inside the same namespace and monitor both the application and selected Kubernetes runtime metrics.

---

# 7. HPA monitoring

The HPA is a Kubernetes object, not part of the Flask application. Therefore, the application `/metrics` endpoint cannot expose HPA information.

For this reason, we added kube-state-metrics.

```text
HPA -> kube-state-metrics -> Prometheus -> Grafana
```

Important HPA queries:

```promql
kube_horizontalpodautoscaler_status_current_replicas{namespace="task-tracker", horizontalpodautoscaler="task-service-hpa"}
```

```promql
kube_horizontalpodautoscaler_status_desired_replicas{namespace="task-tracker", horizontalpodautoscaler="task-service-hpa"}
```

Presentation explanation:

> We monitor only the most meaningful HPA information: the current number of replicas and the desired number of replicas. This shows whether Kubernetes wants to scale the task-service and whether the current deployment matches the desired state.

---

# 8. Pod monitoring

We also monitor two simple pod-level indicators.

## Pod status

```promql
sum by (phase) (kube_pod_status_phase{namespace="task-tracker"})
```

This shows whether pods are running, pending, failed, or succeeded.

## Pod restarts

```promql
sum by (pod) (kube_pod_container_status_restarts_total{namespace="task-tracker"})
```

This shows whether a service is crashing and being restarted by Kubernetes.

Presentation explanation:

> We selected pod status and pod restarts because they are easy to understand and highly meaningful. They show whether the system is running and whether the services are stable.

---

# 9. Grafana dashboard structure

The dashboard is split into three simple parts.

```text
Grafana Dashboard
|
|-- Application Metrics
|   |-- Services up
|   |-- Request rate
|   |-- Error rate
|   |-- Average response time
|   |-- Task/user counters
|
|-- Kubernetes Health
|   |-- Pod status
|   |-- Pod restarts
|
|-- Autoscaling
    |-- HPA current replicas
    |-- HPA desired replicas
```

This keeps the dashboard understandable during the presentation.

---

# 10. Presentation split for 3 people

## Person 1: Application architecture and problem

Responsible for explaining:

- what TaskTracker is
- frontend, task-service, user-service, PostgreSQL
- problem before the extension
- why observability is useful

Suggested speaking text:

> TaskTracker is a distributed application with a frontend, two backend services, and a PostgreSQL database. The original architecture already separated responsibilities, but it was difficult to observe the system. We could not easily see request traffic, errors, response times, or whether the system was healthy. Therefore, we extended the architecture with observability.

Slides:

- title
- project overview
- architecture before
- problem statement

---

## Person 2: Prometheus, Grafana, and Docker Compose

Responsible for explaining:

- `/metrics` endpoints
- Prometheus scraping
- Grafana dashboards
- Docker Compose run mode
- application metrics

Suggested speaking text:

> We added metrics endpoints to the backend services. Prometheus scrapes these endpoints and stores the values as time-series data. Grafana connects to Prometheus and visualizes the most important application metrics, such as request rate, error rate, response time, and business counters. With Docker Compose, all components can be started locally with one command.

Slides:

- observability architecture
- Prometheus and Grafana
- Docker Compose deployment
- application metrics

---

## Person 3: Kubernetes, HPA, and Kubernetes monitoring

Responsible for explaining:

- Kubernetes deployment mode
- pods and services
- HPA
- kube-state-metrics
- simple Kubernetes metrics in Grafana

Suggested speaking text:

> The same application can also run in Kubernetes. Kubernetes gives us a production-like environment with pods, services, and autoscaling. Because the HPA and pod states are Kubernetes objects, we added kube-state-metrics. Prometheus scrapes kube-state-metrics, and Grafana shows only the most meaningful Kubernetes metrics: pod status, pod restarts, and HPA current versus desired replicas.

Slides:

- Kubernetes deployment
- HPA monitoring
- pod monitoring
- final architecture benefits

---

# 11. Live demo plan

## Docker Compose demo

1. Run:

```bash
docker compose up --build
```

2. Open the frontend:

```text
http://localhost:8080
```

3. Create a user and some tasks.
4. Open Prometheus:

```text
http://localhost:9090
```

5. Query:

```promql
up
```

6. Open Grafana:

```text
http://localhost:3000
```

7. Show request rate, response time, tasks created, and users created.

## Kubernetes demo

1. Run Minikube and deploy:

```bash
minikube start
minikube addons enable metrics-server
eval $(minikube docker-env)

kubectl apply -f k8s/
```

2. Check pods:

```bash
kubectl get pods -n task-tracker
```

3. Check HPA:

```bash
kubectl get hpa -n task-tracker
```

4. Open Grafana and show:

- pod status
- pod restarts
- HPA current replicas
- HPA desired replicas

---

# 12. Final summary

Use this as the closing explanation:

> We extended TaskTracker with an observability architecture. The system can now run locally with Docker Compose or in a production-like Kubernetes environment. Prometheus collects application metrics from the backend services and Kubernetes metrics from kube-state-metrics. Grafana visualizes only the most meaningful information: application health, request behavior, pod status, pod restarts, and HPA scaling. This improves maintainability, debugging, and operational visibility while keeping the architecture understandable.

---

# 13. Key architecture benefits

- better system visibility
- easier debugging
- clear separation of concerns
- local and Kubernetes deployment options
- basic cloud-native monitoring
- HPA visibility without overcomplicating the dashboard

---

# 14. Files to mention

Important project files:

```text
docker-compose.yml
monitoring/prometheus.yml
grafana/provisioning/
grafana/dashboards/
k8s/09-prometheus.yaml
k8s/10-grafana.yaml
k8s/11-kube-state-metrics.yaml
README-RUN-MODES.md
```
