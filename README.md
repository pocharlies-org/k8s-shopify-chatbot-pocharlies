# k8s-shopify-chatbot-pocharlies

**Retirado el 03-10-2026** (decisión de Dani; uso real nulo: el informe del 02-10 daba 0 sesiones).

`skirmshop-chatbot` era el chat de la tienda (NestJS) en el namespace `skirmshop`: la variante
`deterministic` servía `skirmshop.e-dani.com/chatbot` y la `skirmshop-chatbot` original quedaba de
rollback, con los CronJobs `chatbot-sync` y `chatbot-daily-report`. El tema de la tienda dejó de
cargarlo en `6.0.0-pocharlies.21` (widget flotante, página `/pages/ai` despublicada y caja de
preguntas de las guías).

Lo único que queda es `k8s/pvc.yaml`: los PVC `chatbot-data` (SQLite de conversaciones) y
`openclaw-state`, con su histórico. Para volver a encenderlo: recuperar del historial de git los
manifiestos (`k8s/manifest.yaml`, `k8s/staged/deterministic/`, `k8s/ingressroute.yaml`,
`k8s/cronjobs.yaml`, `k8s/externalsecret-reporting.yaml`) y `cron/`, y volver a meter el widget en
el tema.
