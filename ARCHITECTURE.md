# ARCHITECTURE — k8s-shopify-chatbot-pocharlies

**Retirado el 03-10-2026**: solo quedan los PVC (`k8s/pvc.yaml`); ver README. Lo de abajo describe cómo era.

### Lo que aún apunta al chatbot retirado (pendiente de limpiar, cada uno en su repo)
- `skirmshopshopifyapp/shopify.app.toml`: el App Proxy `skirmchat` apunta a `skirmshop.e-dani.com/chatbot`.
- `k8s-agentgateway-pocharlies`, `skirmshop-plugins-mcp.js`: la ruta `chatbot` y la tool `chatbot_api`.
- `synapse-adapter-messaging`, `channels/chatbot.py`: cliente de `/api/internal/chatbot/sessions/send`.
- `dgx-infra`, `services/dashboard/routes_autoreply.py`: registro con `status_ref` del chatbot.
- `skirmshop-monitoring`: `scripts/chatbot-sync.py` y los dashboards de Grafana del chatbot.
- `k8s-infra-pocharlies`: la credencial de valkey del chatbot (`shared-valkey.yaml` y su test de contrato).
- `skirmshop-brain-k8s`: una regla de la NetworkPolicy de product-relations (inofensiva; product-relations también está apagado).
- `skirmshop-theme`: el homepage alternativo `index.tactical` (no publicado).
- Secrets fuera de git en `skirmshop`: `chatbot-secrets` (creado a mano) y los que dejaron los ExternalSecrets `chatbot-deterministic-secrets` / `chatbot-report-secrets`; retirarlos o rotar sus claves es de security.

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
`k8s/manifest.yaml` (Deployment, PVCs, Service), `ingressroute.yaml`, `cronjobs.yaml` (sync cada 5 min, informe diario 08:00), `externalsecret-reporting.yaml`, y `k8s/staged/deterministic/` (la variante `deterministic`, que ArgoCD sí sincronizaba bajo `shopify-chatbot` y servía la ruta pública con 2 réplicas).

## Tests y validaciones
`reusable-ci.yml` con `run_docker_build: true` (construye `cron/Dockerfile`).

## CI/CD y despliegue
`ci.yml`, `pr-review.yml`. ArgoCD lee `main`.

## Decisiones y trampas
- `chatbot-secrets` se crea fuera de banda (TODO: migrarlo a ExternalSecret como el resto).
- SQLite en un solo pod: sin réplicas múltiples.
