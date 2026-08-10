# Deterministic multitenant production runtime

This directory is part of the live Argo graph. The runtime is pinned to the
signed `v3.1.15` image built from audited commit
`f5e5b20b9c40a4a94bcc41e46c4755e1d0a03e90` and runs with two replicas.

Promotion completed after the ExternalSecret, Brain guide reindex, `/healthz`,
grounded-answer, deterministic-replay, and unsupported-question fail-closed
gates passed. The public IngressRoute targets this service on port `3100`.
The legacy `skirmshop-chatbot` Deployment and Service remain deployed as the
immediate rollback target.
