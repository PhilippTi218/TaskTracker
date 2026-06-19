# TaskTracker Observability Extension — Presentation Guide

## Topic
**Extending TaskTracker with Observability using Prometheus and Grafana**

## Team Presentation Structure
This presentation is divided for **3 people**. Each person has a clear responsibility:

| Person | Main Topic | Focus |
|---|---|---|
| Person 1 | Original System and Problem | Explain the project and why observability is needed |
| Person 2 | Observability Architecture | Explain Prometheus, Grafana, metrics, and dashboards |
| Person 3 | Deployment and Demo | Explain Docker Compose, Kubernetes, and show the live demo |

---

# 1. Short Project Overview

TaskTracker is a containerized task management application. It is built with multiple services instead of one single application.

The system contains:

- **Frontend**: user interface
- **Task Service**: manages task operations
- **User Service**: manages user operations
- **PostgreSQL**: stores users and tasks
- **Prometheus**: collects metrics
- **Grafana**: visualizes metrics in dashboards

The project can be started in two ways:

1. With **Docker Compose** for local development
2. With **Kubernetes** for a more production-like deployment

---

# 2. Architecture Before the Extension

Before the observability extension, the system architecture looked like this:

```text
User
 |
 v
Frontend
 |
 v
Backend Services
 |
 v
PostgreSQL
```

More detailed:

```text
Frontend
   |
   v
Task Service
User Service
   |
   v
PostgreSQL
```

The application could run, but it had limited visibility.

## Problems Before Observability

Without observability, it was difficult to answer questions like:

- Is the task-service healthy?
- Is the user-service healthy?
- How many requests are being handled?
- Are there many errors?
- How fast are the services responding?
- How many tasks were created?
- How many users were created?

The only way to understand problems was mostly by checking logs manually.

---

# 3. Architecture After the Extension

We extended the system with an observability layer.

```text
Frontend
   |
   v
Task Service  ----\
                   \
                    > Prometheus ---> Grafana
                   /
User Service  ----/
   |
   v
PostgreSQL
```

## What Changed?

The backend services now expose a `/metrics` endpoint.

Prometheus collects metrics from these endpoints:

```text
Prometheus ---> task-service /metrics
Prometheus ---> user-service /metrics
```

Grafana connects to Prometheus and displays the metrics in dashboards.

---

# 4. Main Components

## 4.1 Frontend

The frontend is the entry point for the user.

Users interact with it to:

- create users
- create tasks
- update tasks
- delete tasks

Presentation sentence:

> The frontend is the user interface of the TaskTracker system. It communicates with the backend services and allows users to manage tasks.

---

## 4.2 Task Service

The task-service is responsible for task operations.

It handles:

- creating tasks
- reading tasks
- updating tasks
- deleting tasks

It exposes:

```text
/health
/metrics
```

`/health` checks if the service is alive.

`/metrics` exposes Prometheus-compatible metrics.

Presentation sentence:

> The task-service contains the business logic for task management. We extended it with a `/metrics` endpoint so Prometheus can collect service and business metrics.

---

## 4.3 User Service

The user-service is responsible for user operations.

It handles:

- creating users
- reading users

It also exposes:

```text
/health
/metrics
```

Presentation sentence:

> The user-service manages user-related functionality independently from the task-service. This shows a service-oriented architecture with clear separation of responsibilities.

---

## 4.4 PostgreSQL

PostgreSQL is the database layer.

It stores:

- users
- tasks

Presentation sentence:

> PostgreSQL is the persistent data layer of the system. The backend services use it to store and retrieve application data.

---

## 4.5 Prometheus

Prometheus is the monitoring system.

It collects metrics by scraping the backend services.

Scraping means that Prometheus regularly calls the `/metrics` endpoints.

```text
Prometheus ---> task-service:5000/metrics
Prometheus ---> user-service:5000/metrics
```

Prometheus collects metrics such as:

- service availability
- HTTP request count
- response time
- error count
- created tasks
- updated tasks
- deleted tasks
- created users

Presentation sentence:

> Prometheus is responsible for collecting metrics from the backend services. It periodically scrapes the `/metrics` endpoints and stores the data as time-series metrics.

---

## 4.6 Grafana

Grafana is the visualization layer.

Prometheus stores the metrics.

Grafana displays the metrics in dashboards.

```text
Prometheus stores data
Grafana visualizes data
```

Grafana can show:

- request rate
- error rate
- average response time
- service health
- number of created tasks
- number of created users

Presentation sentence:

> Grafana connects to Prometheus and visualizes the metrics in dashboards. This makes it easier to understand the behavior and health of the system.

---

# 5. Metrics Used in the Project

The project collects both technical metrics and business metrics.

## 5.1 Technical Metrics

Technical metrics show how the system behaves internally.

Examples:

```promql
up
flask_http_request_total
flask_http_request_duration_seconds
```

These metrics can show:

- whether a service is up or down
- how many requests were made
- how long requests take
- how many errors happened

## 5.2 Business Metrics

Business metrics show how the application is used.

Examples:

```promql
tasktracker_tasks_created_total
tasktracker_tasks_updated_total
tasktracker_tasks_deleted_total
tasktracker_users_created_total
```

These metrics can show:

- how many tasks were created
- how many tasks were updated
- how many tasks were deleted
- how many users were created

Presentation sentence:

> We collect both technical and business metrics. Technical metrics help us understand system health and performance, while business metrics help us understand how users interact with the application.

---

# 6. Docker Compose Infrastructure

Docker Compose is used for local development and simple testing.

With one command, it starts the full system:

```bash
docker compose up --build
```

Docker Compose starts:

- frontend
- task-service
- user-service
- postgres
- prometheus
- grafana

## Docker Compose Architecture

```text
Docker Compose Network
|
|-- frontend
|-- task-service
|-- user-service
|-- postgres
|-- prometheus
|-- grafana
```

## Local URLs

```text
Frontend:    http://localhost:8080
Prometheus:  http://localhost:9090
Grafana:     http://localhost:3000
```

Grafana login:

```text
Username: admin
Password: admin
```

Presentation sentence:

> Docker Compose is our local development environment. It allows us to start the complete system, including monitoring, with one command.

---

# 7. Kubernetes Infrastructure

Kubernetes is used as a more production-like deployment environment.

Instead of one `docker-compose.yml` file, Kubernetes uses manifests inside the `k8s` folder.

The Kubernetes setup contains resources such as:

- Namespace
- ConfigMap
- Secret
- Deployment
- Service
- HPA
- Prometheus Deployment
- Grafana Deployment

In Kubernetes, every component runs as a Pod.

```text
frontend pod
task-service pod
user-service pod
postgres pod
prometheus pod
grafana pod
```

Services provide stable internal names:

```text
task-service
user-service
postgres
prometheus
grafana
```

Prometheus scrapes the services inside the Kubernetes cluster:

```text
task-service.task-tracker.svc.cluster.local:5000/metrics
user-service.task-tracker.svc.cluster.local:5000/metrics
```

Presentation sentence:

> Kubernetes is our production-like environment. It manages the containers as Pods and connects them through Services. This makes the system more scalable and closer to a real cloud-native deployment.

---

# 8. Why Supporting Both Docker Compose and Kubernetes Is Useful

The project supports two deployment modes:

| Deployment Mode | Purpose |
|---|---|
| Docker Compose | Local development and simple testing |
| Kubernetes | Production-like deployment and scalability |

This shows that the architecture is:

- containerized
- portable
- environment-independent
- observable
- cloud-ready

Presentation sentence:

> Supporting both Docker Compose and Kubernetes shows deployment flexibility. Developers can run the system locally, while the same architecture can also be deployed in a production-like Kubernetes environment.

---

# 9. Presentation Plan for 3 People

## Person 1 — Project, Problem, and Original Architecture

### Main responsibility
Explain what the project is and why observability was needed.

### Suggested slides

1. Project overview
2. Original architecture
3. Problem before observability

### What Person 1 should say

> Our project is called TaskTracker. It is a containerized application with a frontend, two backend services, and a PostgreSQL database. The task-service manages tasks, and the user-service manages users.

> Before our extension, the system could run, but it was difficult to monitor. If one service became slow or failed, we had to manually inspect logs. We could not easily see request counts, error rates, response times, or business activity.

> Because of this, we decided to improve the architecture by adding observability with Prometheus and Grafana.

### Diagram for Person 1

```text
Frontend
   |
   v
Task Service
User Service
   |
   v
PostgreSQL
```

### Key terms Person 1 should mention

- service-oriented architecture
- frontend
- backend services
- PostgreSQL
- lack of visibility
- need for observability

---

## Person 2 — Observability Architecture

### Main responsibility
Explain Prometheus, Grafana, metrics, and how the observability extension works.

### Suggested slides

4. New architecture with observability
5. Prometheus and Grafana
6. Metrics collected

### What Person 2 should say

> We extended the backend services with `/metrics` endpoints. These endpoints expose Prometheus-compatible metrics.

> Prometheus periodically scrapes these endpoints from the task-service and user-service. It stores the collected data as time-series metrics.

> Grafana connects to Prometheus and visualizes the data in dashboards. This allows us to monitor service health, request rate, error rate, response time, and business metrics.

> We collect technical metrics such as HTTP request count and response time. We also collect business metrics such as created tasks, updated tasks, deleted tasks, and created users.

### Diagram for Person 2

```text
Task Service  ----\
                   \
                    > Prometheus ---> Grafana
                   /
User Service  ----/
```

### Example metrics to show

```promql
up
flask_http_request_total
flask_http_request_duration_seconds
tasktracker_tasks_created_total
tasktracker_users_created_total
```

### Key terms Person 2 should mention

- observability
- metrics
- scraping
- time-series data
- dashboard
- technical metrics
- business metrics

---

## Person 3 — Deployment Options and Live Demo

### Main responsibility
Explain how the system can run with Docker Compose and Kubernetes, then perform the live demo.

### Suggested slides

7. Docker Compose deployment
8. Kubernetes deployment
9. Live demo
10. Benefits and conclusion

### What Person 3 should say

> The project supports two deployment modes. Docker Compose is used for local development, while Kubernetes is used as a production-like environment.

> With Docker Compose, we can start the complete system with one command. This includes the frontend, backend services, database, Prometheus, and Grafana.

> With Kubernetes, each component runs as a Pod and is exposed through a Kubernetes Service. Prometheus and Grafana also run inside the cluster.

> This demonstrates that the system is portable, containerized, observable, and ready for cloud-native deployment.

### Docker Compose commands

```bash
docker compose up --build
```

Open:

```text
Frontend:    http://localhost:8080
Prometheus:  http://localhost:9090
Grafana:     http://localhost:3000
```

### Kubernetes commands

```bash
minikube start
eval $(minikube docker-env)

docker build -t tasktracker-task-service:latest ./task-service
docker build -t tasktracker-user-service:latest ./user-service
docker build -t tasktracker-frontend:latest ./frontend

kubectl apply -f k8s/
```

Check pods:

```bash
kubectl get pods -n task-tracker
```

Port forwarding:

```bash
kubectl port-forward -n task-tracker svc/frontend 8080:80
kubectl port-forward -n task-tracker svc/prometheus 9090:9090
kubectl port-forward -n task-tracker svc/grafana 3000:3000
```

### Key terms Person 3 should mention

- Docker Compose
- Kubernetes
- Pods
- Services
- ConfigMaps
- deployment flexibility
- cloud-native deployment

---

# 10. Live Demo Script

## Demo Option A — Docker Compose

1. Start the system:

```bash
docker compose up --build
```

2. Open the frontend:

```text
http://localhost:8080
```

3. Create a user.

4. Create, update, and delete a task.

5. Open Prometheus:

```text
http://localhost:9090
```

6. Query:

```promql
up
```

Explain:

> The `up` metric shows whether Prometheus can reach the services. A value of 1 means the service is available.

7. Query:

```promql
tasktracker_tasks_created_total
```

Explain:

> This metric increases when a task is created. It is an example of a business metric.

8. Open Grafana:

```text
http://localhost:3000
```

Login:

```text
admin / admin
```

9. Show the TaskTracker dashboard.

Explain:

> The dashboard visualizes the collected metrics, such as request rate, error rate, response time, and business events.

---

## Demo Option B — Kubernetes

1. Start Minikube:

```bash
minikube start
```

2. Use Minikube Docker environment:

```bash
eval $(minikube docker-env)
```

3. Build images:

```bash
docker build -t tasktracker-task-service:latest ./task-service
docker build -t tasktracker-user-service:latest ./user-service
docker build -t tasktracker-frontend:latest ./frontend
```

4. Deploy Kubernetes resources:

```bash
kubectl apply -f k8s/
```

5. Check running pods:

```bash
kubectl get pods -n task-tracker
```

6. Start port forwarding:

```bash
kubectl port-forward -n task-tracker svc/frontend 8080:80
kubectl port-forward -n task-tracker svc/prometheus 9090:9090
kubectl port-forward -n task-tracker svc/grafana 3000:3000
```

7. Open the same URLs:

```text
Frontend:    http://localhost:8080
Prometheus:  http://localhost:9090
Grafana:     http://localhost:3000
```

8. Repeat the same demo:

- create a user
- create a task
- check Prometheus
- show Grafana dashboard

---

# 11. Suggested Slide Structure

## Slide 1 — Title

**TaskTracker Observability Extension**

Subtitle:

**Monitoring a Microservice-Based Application with Prometheus and Grafana**

Speaker: Person 1

---

## Slide 2 — Original System

Content:

- frontend
- task-service
- user-service
- PostgreSQL
- Docker/Kubernetes support

Speaker: Person 1

---

## Slide 3 — Problem

Content:

- no central monitoring
- hard to detect service failures
- hard to measure errors
- hard to measure response time
- hard to understand application usage

Speaker: Person 1

---

## Slide 4 — New Observability Architecture

Content:

```text
Task Service  ----\
                   \
                    > Prometheus ---> Grafana
                   /
User Service  ----/
```

Speaker: Person 2

---

## Slide 5 — Prometheus

Content:

- scrapes `/metrics`
- stores time-series data
- monitors service availability
- collects HTTP and business metrics

Speaker: Person 2

---

## Slide 6 — Grafana

Content:

- connects to Prometheus
- visualizes metrics
- dashboard for request rate, errors, response time, and business metrics

Speaker: Person 2

---

## Slide 7 — Deployment Options

Content:

| Mode | Purpose |
|---|---|
| Docker Compose | Local development |
| Kubernetes | Production-like deployment |

Speaker: Person 3

---

## Slide 8 — Live Demo

Content:

- start system
- create user
- create task
- check Prometheus
- show Grafana dashboard

Speaker: Person 3

---

## Slide 9 — Benefits

Content:

- better visibility
- faster debugging
- performance monitoring
- business monitoring
- deployment flexibility
- cloud-native architecture

Speaker: Person 3

---

## Slide 10 — Conclusion

Content:

> We extended TaskTracker with an observability layer using Prometheus and Grafana. The system can run locally with Docker Compose or in a production-like Kubernetes environment. This improves maintainability, monitoring, and operational control.

All speakers

---

# 12. Final Explanation for the Teacher

You can use this as your final spoken summary:

> We extended the TaskTracker application with an observability architecture using Prometheus and Grafana. The backend services expose metrics through `/metrics` endpoints. Prometheus scrapes these endpoints and stores the metrics, while Grafana visualizes them in dashboards. The system can be deployed either locally with Docker Compose or in a production-like Kubernetes environment. This demonstrates containerization, service separation, monitoring, deployment flexibility, and cloud-native architecture principles.

---

# 13. Important Keywords to Use

During the presentation, try to use these terms:

- observability
- metrics
- monitoring
- Prometheus
- Grafana
- dashboard
- scraping
- service health
- request rate
- response time
- error rate
- business metrics
- Docker Compose
- Kubernetes
- Pods
- Services
- containerization
- cloud-native architecture
- deployment flexibility
- maintainability

---

# 14. Simple One-Minute Version

If you need a very short explanation, use this:

> Our TaskTracker project is a service-based application with a frontend, task-service, user-service, and PostgreSQL database. We extended the architecture by adding Prometheus and Grafana. The backend services expose metrics through `/metrics` endpoints. Prometheus collects these metrics, and Grafana visualizes them in dashboards. This allows us to monitor service health, request rate, errors, response time, and business events like created tasks and users. The system can run locally with Docker Compose or in a production-like Kubernetes environment, which shows deployment flexibility and cloud-native architecture.

