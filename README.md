# k8s-shopify-chatbot-pocharlies

GitOps manifests for **skirmshop-chatbot** (NestJS storefront chat) deployed to the
`skirmshop` namespace on the k3s cluster, managed by ArgoCD.

## Layout
- `k8s/manifest.yaml` — Deployment (`skirmshop-chatbot`) + `local-path` PVCs + Service
- `k8s/ingressroute.yaml` — public route `skirmshop.e-dani.com/chatbot` (traefik-edge, `strip-chatbot` middleware)
- `k8s/kustomization.yaml`

## Wiring
- Runs on the **edge node (`sauvage`)** → reaches the brain via the in-cluster service.
- `POCHARLIES_URL` → `http://skirmshop-brain.skirmshop-brain-prod.svc.cluster.local` (brain v2)
- `LLM_BASE_URL` → `http://litellm.litellm.svc.cluster.local:4000/v1`
- SQLite on a `local-path` PVC (longhorn isn't on the edge node); app self-migrates (`prisma migrate deploy`).

## Secrets
`chatbot-secrets` (created out-of-band from the app env; TODO: migrate to Vault/ExternalSecret like the sibling apps).

## Image
`harbor.e-dani.com/homelab/skirmshop-chatbot` — built from `pocharlies/skirmshop-chatbot`.
