# Task Tracker Microservices

Mini-Projekt für eine einfache Task-Tracker-App mit drei Services und PostgreSQL.

## Architektur

- `frontend`: Statische Weboberfläche mit Nginx-Reverse-Proxy
- `task-service`: Flask REST API für Tasks
- `user-service`: Flask REST API für einfache User
- `postgres`: Datenbank für Users und Tasks

## Lokaler Start mit Docker Compose

```bash
docker compose up --build
```

Danach ist die App erreichbar unter:

```text
http://localhost:8080
```

API-Endpunkte:

- `GET /api/tasks` (optionale Filter, siehe unten)
- `POST /api/tasks`
- `PATCH /api/tasks/<id>`
- `DELETE /api/tasks/<id>`
- `GET /api/users`
- `POST /api/users`

### Task-Filter

Die Task-Liste lässt sich über Query-Parameter filtern (einzeln oder kombiniert):

- `GET /api/tasks?done=true` – nur erledigte Tasks (`done=false` für offene)
- `GET /api/tasks?user_id=1` – nur Tasks eines bestimmten Users
- `GET /api/tasks?user_id=1&done=true` – beide Filter kombiniert

`done` akzeptiert `true`/`false` (auch `1`/`0`), `user_id` muss eine ganze Zahl sein. Ungültige
Werte werden mit `400 Bad Request` abgelehnt. Ohne Parameter werden alle Tasks zurückgegeben.

### Validierung

Beim Anlegen (`POST`) und Ändern (`PATCH`) von Tasks gelten folgende Regeln (sonst `400`):

- `title` darf nicht leer sein (auch bei `PATCH`, wenn er mitgeschickt wird)
- `done` muss `true` oder `false` sein
- `user_id` muss eine Zahl oder `null` sein

### Healthcheck

`GET /health` des Task-Service prüft nicht nur Flask, sondern auch die Datenbankverbindung
(`SELECT 1`). Ist PostgreSQL erreichbar, kommt `200` mit `{"status":"ok","database":"ok"}`,
andernfalls `503` mit `{"status":"error","database":"unavailable"}`. Dadurch erkennt Kubernetes
über die Probes zuverlässiger, ob der Service wirklich arbeitsfähig ist.

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

Nur die gemeinsame Basis für die Services anwenden:

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secret.yaml
kubectl apply -f k8s/03-postgres.yaml
```

PostgreSQL-Basis prüfen:

```bash
kubectl get pvc,pods,svc -n task-tracker
kubectl wait --for=condition=ready pod -l app=postgres -n task-tracker --timeout=120s
```

Die Datenbank ist danach intern unter `postgres:5432` erreichbar.

User-Service Image bauen und in Kubernetes starten:

```bash
docker build -t task-tracker-user-service:latest ./user-service
kubectl apply -f k8s/05-user-service.yaml
kubectl wait --for=condition=ready pod -l app=user-service -n task-tracker --timeout=120s
```

User-Service lokal testen:

```bash
kubectl port-forward -n task-tracker svc/user-service 5002:5000
curl http://localhost:5002/health
curl http://localhost:5002/users
curl -X POST http://localhost:5002/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User"}'
```

Task-Service Image bauen und in Kubernetes starten:

```bash
docker build -t task-tracker-task-service:latest ./task-service
kubectl apply -f k8s/04-task-service.yaml
kubectl wait --for=condition=ready pod -l app=task-service -n task-tracker --timeout=120s
```

Task-Service lokal testen:

```bash
kubectl port-forward -n task-tracker svc/task-service 5001:5000
curl http://localhost:5001/health
curl http://localhost:5001/tasks
curl -X POST http://localhost:5001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","description":"erste Aufgabe"}'
```

Status prüfen:

```bash
kubectl get pods,svc,ingress -n task-tracker
```

Wenn kein Ingress Controller aktiv ist, kann das Frontend per Port-Forward geöffnet werden:

```bash
kubectl port-forward -n task-tracker svc/frontend 8080:80
```

Dann im Browser öffnen:

```text
http://localhost:8080
```

## Autoscaling mit HPA (Horizontal Pod Autoscaler)

Der Horizontal Pod Autoscaler (HPA) ist ein Kubernetes-Objekt, das die Anzahl der Pods
eines Deployments automatisch an die aktuelle Last anpasst. Statt einen einzelnen Pod größer zu
machen (vertikal), startet der HPA bei Bedarf weitere Kopien des Pods (horizontal) und entfernt sie
wieder, wenn die Last sinkt. In diesem Projekt skaliert der HPA den `task-service`.

Die Konfiguration liegt in `k8s/08-hpa.yaml`:

```yaml
spec:
  scaleTargetRef:
    name: task-service        # auf welches Deployment der HPA wirkt
  minReplicas: 2              # nie weniger als 2 Pods
  maxReplicas: 5              # nie mehr als 5 Pods
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70   # Zielwert: 70 % CPU-Auslastung
```

Bedeutung: Steigt die durchschnittliche CPU-Auslastung der `task-service`-Pods über 70 %,
startet Kubernetes automatisch zusätzliche Pods (bis maximal 5). Sinkt die Auslastung wieder,
werden überzählige Pods entfernt, bis wieder das Minimum von 2 erreicht ist.

### Voraussetzung: Metrics Server

Der HPA kann nur skalieren, wenn er die aktuelle CPU-Auslastung messen kann. Diese Messwerte
liefert der Metrics Server. Ohne ihn wird der HPA zwar angelegt, zeigt bei den Metriken aber
`<unknown>` und skaliert nie.

Bei Minikube ist der Metrics Server als Addon verfügbar und mit einem Befehl aktiviert:

```bash
minikube addons enable metrics-server
```

### HPA anwenden und beobachten

```bash
kubectl apply -f k8s/08-hpa.yaml
kubectl get hpa -n task-tracker -w
```

In der Spalte `TARGETS` sollte ein Wert wie `cpu: 1%/70%` stehen.
Das `-w` (watch) verfolgt Änderungen live.

### Autoscaling testen (optional)

Um zu sehen, wie der HPA hochskaliert, kann man künstlich Last erzeugen. In einem Terminal den
Service per Port-Forward erreichbar machen und Last gegen ihn fahren:

```bash
kubectl port-forward -n task-tracker svc/task-service 5001:5000
# in einem zweiten Terminal:
while true; do curl -s http://localhost:5001/tasks > /dev/null; done
```

Parallel in einem weiteren Terminal den HPA beobachten:

```bash
kubectl get hpa -n task-tracker -w
```

## Projektaufteilung

- Edwin Caballero: `frontend`, `frontend.Dockerfile`, Kubernetes Ingress/Frontend-Service
- Nadine Schmid: `task-service`, Task API, Task Deployment
- Philipp Tichy: `user-service`, PostgreSQL, Secret, PVC

## Kubernetes Themen im Projekt

- Deployments: Frontend, Task-Service, User-Service, PostgreSQL
- Services: interne Kommunikation zwischen Services
- Ingress: Zugriff von außen auf das Frontend
- ConfigMap: Datenbank- und App-Konfiguration
- Secret: Datenbankpasswort
- PVC: persistente PostgreSQL-Daten
- HPA: optionales Autoscaling für den Task-Service
