# Deterministic multitenant canary (staged, not reconciled)

This directory is intentionally absent from `k8s/kustomization.yaml`. It is the
complete canary declaration, but it must remain outside the live Argo graph
until all three gates are satisfied:

1. publish and pin an amd64 image containing chatbot commit `c1f7d0d`;
2. populate `secret/skirmshop/chatbot-deterministic` with every property named
   in `external-secret.yaml` (all channel ingress and identity keys distinct);
3. deploy and seed the dedicated `brain-product-relations` API, then pass the
   web and professional-WhatsApp smoke vectors.

After those gates, replace the placeholder image, add this directory to the
root kustomization, keep `replicas: 0` for the first sync, then scale to two only
after the Secret is `Ready` and `/healthz` is green. Public ingress cutover is a
separate, final patch; the legacy service remains untouched here.
