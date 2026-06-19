#!/usr/bin/env bash
set -euo pipefail

eval "$(minikube docker-env)"
docker build -t tasktracker-task-service:latest ./task-service
docker build -t tasktracker-user-service:latest ./user-service
docker build -t tasktracker-frontend:latest ./frontend
kubectl apply -f k8s/
kubectl get pods -n task-tracker
