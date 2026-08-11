# Deterministic multitenant production runtime

This directory is part of the live Argo graph. The runtime is pinned to the
signed `v3.1.17` image built from audited commit
`2c04092bd1c02edb5567dcd5942037458f3aaf63` and runs with two replicas.

Promotion completed after the ExternalSecret, Brain guide reindex, `/healthz`,
grounded-answer, deterministic-replay, and unsupported-question fail-closed
gates passed. The public IngressRoute targets this service on port `3100`.
The legacy `skirmshop-chatbot` Deployment and Service remain deployed as the
immediate rollback target.
