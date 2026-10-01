# ARCHITECTURE — k8s-shopify-chatbot-pocharlies

Despliegue de `skirmshop-chatbot` (chat de tienda en NestJS) en ns `skirmshop`. Código en `pocharlies-org/skirmshop-chatbot` (fuera de la tanda).

## Clientes y versiones
- Un servicio web (`skirmshop.e-dani.com/chatbot`, `traefik-edge`, middleware `strip-chatbot`) + CronJobs. Corre en el nodo de borde `sauvage`. Tronco: `main` (Application `shopify-chatbot`, path `k8s`).

## Dependencias (ambos sentidos)
- Depende de: Brain v2 (`POCHARLIES_URL=http://skirmshop-brain.skirmshop-brain-prod.svc.cluster.local`), LiteLLM (`http://litellm.litellm.svc.cluster.local:4000/v1`), PVC `local-path` con SQLite (Longhorn no está en el borde; la app migra sola con `prisma migrate deploy`).
- Imágenes `harbor.e-dani.com/homelab/skirmshop-chatbot` y `skirmshop-chatbot-monitoring`.

## Stack
Kustomize + manifests planos; scripts Python en `cron/` (`chatbot_sync.py`, `chatbot_daily_report.py`, con `requirements.txt` y `Dockerfile`).

## Componentes compartidos
Ninguno de la base del framework.

## Cómo se construye
`k8s/manifest.yaml` (Deployment, PVCs, Service), `ingressroute.yaml`, `cronjobs.yaml` (sync cada 5 min, informe diario 08:00), `externalsecret-reporting.yaml`, y `k8s/staged/deterministic/` (variante runtime en preparación, con su README; no la sincroniza ArgoCD).

## Tests y validaciones
`reusable-ci.yml` con `run_docker_build: true` (construye `cron/Dockerfile`).

## CI/CD y despliegue
`ci.yml`, `pr-review.yml`. ArgoCD lee `main`.

## Decisiones y trampas
- `chatbot-secrets` se crea fuera de banda (TODO: migrarlo a ExternalSecret como el resto).
- SQLite en un solo pod: sin réplicas múltiples.
