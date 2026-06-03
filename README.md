# Task Tracker Microservices

Mini-Projekt fuer eine einfache Task-Tracker-App mit drei Services und PostgreSQL.

## Architektur

- `frontend`: Statische Weboberflaeche mit Nginx-Reverse-Proxy
- `task-service`: Flask REST API fuer Tasks
- `user-service`: Flask REST API fuer einfache User
- `postgres`: Datenbank fuer Users und Tasks

## Lokaler Start mit Docker Compose

```bash
docker compose up --build
```

Danach ist die App erreichbar unter:

```text
http://localhost:8080
```

API-Endpunkte:

- `GET /api/tasks`
- `POST /api/tasks`
- `PATCH /api/tasks/<id>`
- `DELETE /api/tasks/<id>`
- `GET /api/users`
- `POST /api/users`

## Kubernetes Start

Voraussetzung: ein laufendes Kubernetes-Cluster, z. B. Minikube, Kind oder Docker Desktop Kubernetes.

Images bauen:

```bash
docker build -t task-tracker-frontend:latest ./frontend
docker build -t task-tracker-task-service:latest ./task-service
docker build -t task-tracker-user-service:latest ./user-service
```

Bei Minikube vorher die Docker-Umgebung aktivieren:

```bash
eval $(minikube docker-env)
```

Manifeste anwenden:

```bash
kubectl apply -f k8s/
```

Status pruefen:

```bash
kubectl get pods,svc,ingress -n task-tracker
```

Wenn kein Ingress Controller aktiv ist, kann das Frontend per Port-Forward geoeffnet werden:

```bash
kubectl port-forward -n task-tracker svc/frontend 8080:80
```

Dann im Browser oeffnen:

```text
http://localhost:8080
```

## Projektaufteilung

- Person 1: `frontend`, `frontend.Dockerfile`, Kubernetes Ingress/Frontend-Service
- Person 2: `task-service`, Task API, Task Deployment
- Person 3: `user-service`, PostgreSQL, Secret, PVC

## Kubernetes Themen im Projekt

- Deployments: Frontend, Task-Service, User-Service, PostgreSQL
- Services: interne Kommunikation zwischen Services
- Ingress: Zugriff von aussen auf das Frontend
- ConfigMap: Datenbank- und App-Konfiguration
- Secret: Datenbankpasswort
- PVC: persistente PostgreSQL-Daten
- HPA: optionales Autoscaling fuer den Task-Service

