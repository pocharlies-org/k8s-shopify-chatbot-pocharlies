# Deterministic multitenant canary (staged, not reconciled)

This directory is intentionally absent from `k8s/kustomization.yaml`. It is the
complete canary declaration, but it must remain outside the live Argo graph
until all three gates are satisfied:

1. publish, verify, and pin by digest an amd64 image containing the exact
   audited chatbot release commit (`938f8960b93a457d12371e336e2691c4f939b756`);
2. populate `secret/skirmshop/chatbot-deterministic` with every property named
   in `external-secret.yaml` (all channel ingress and identity keys distinct);
3. deploy and seed the dedicated `brain-product-relations` API, then pass the
   web and professional-WhatsApp smoke vectors.

The first two gates are complete: the manifest is pinned to the signed release
digest and the ExternalSecret is Ready. Keep this directory outside the root
kustomization, with `replicas: 0`, until the relation projection and the direct
core API acceptance suite pass. Then add it to the root kustomization and scale
to two only after `/healthz` is green. The release image starts through its
package-manager-free entrypoint; the manifest must not override it with `npm`
or `npx`. Public ingress cutover is a separate, final patch; the legacy service
remains untouched here.
