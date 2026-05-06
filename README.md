# egov-digit-studio — laptop-local DIGIT (Tilt + Compose)

Run a **DIGIT core** stack on your laptop with **Tilt** (dashboard, grouped resources, nav buttons). Tilt drives **`docker-compose.yml`**; you still use **`docker compose`** for one-off builds (e.g. `db-migrations`) and cleanup. **Step-by-step setup, first-time DB migration build, and where to open the Tilt UI vs the frontend after startup:** **[QUICK-SETUP.md](QUICK-SETUP.md)**.

Configuration and service wiring are informed by **[DIGIT-DevOps](https://github.com/egovernments/DIGIT-DevOps)** (`unified-demo` branch) for Helm values and platform layout. This repo is **not** a full copy of the cloud `unified-demo` footprint (that would require Kubernetes and shared RDS/Kafka/ES).

## What you get locally

- Postgres (seeded), Redis, Redpanda (Kafka-compatible), MinIO, Elasticsearch 7.x (for inbox)  
- Core services: MDMS v2, ENC, IDGEN, User, Workflow v2, Localization, Boundary v2, Access Control, Persister, Filestore, HRMS, URL shortening, boundary management (Node)  
- **Studio** (Helm-aligned envs): health-individual, health-service-request, public-service-init, public-service, egov-otp, user-otp, egov-notification-sms, pdf-service, studio-pdf, digit-studio, inbox — plus Kong routes under the same path prefixes. Service maps for inbox live in `configs/studio/inbox.env` (search URLs rewritten to `http://kong:8000/...` so you can add matching routes later).  
- Kong on **http://localhost:18000** — **browser and frontend access only through Kong**, e.g. DIGIT UI at **http://localhost:18000/digit-ui/**

Override images via `.env` or the shell using variables listed in the header comment of `docker-compose.yml` (e.g. `IMAGE_DIGIT_STUDIO`, `IMAGE_PUBLIC_SERVICE`, …).

PGR / complaint APIs are **not** included in this compose file (add a service + Kong routes if you need them).

## Prerequisites

1. Docker with Compose v2  
2. **[Tilt](https://tilt.dev/)** — install the CLI on your PATH (see **[QUICK-SETUP.md — Install Tilt](QUICK-SETUP.md#install-tilt)**).  
3. **Optional:** a `tilt` binary at **`./bin/tilt`** if your team pins a known-good version — run **`./bin/tilt up`** instead of `tilt up` (see [Optional local Tilt binary](#optional-local-tilt-binary)).

## Quick start

Use **[QUICK-SETUP.md](QUICK-SETUP.md)** for the full sequence (prerequisites, [Install Tilt](QUICK-SETUP.md#install-tilt), `docker compose build db-migrations`, `tilt up`, stop/reset, and **Tilt UI + frontend URLs once the stack is ready**).

```bash
cd egov-digit-studio

# First time only: local Flyway image (see QUICK-SETUP.md)
# docker compose build db-migrations

# Optional: clone DIGIT-DevOps next to this repo for reference (Helm env: unified-demo)
# git clone -b unified-demo https://github.com/egovernments/DIGIT-DevOps.git ../DIGIT-DevOps

tilt up
# Or, if you use ./bin/tilt: ./bin/tilt up
```

After startup, open the **Tilt UI** and the **DIGIT UI** (Kong only) as in **QUICK-SETUP → [Access after startup](QUICK-SETUP.md#access-after-startup)** — Tilt: **http://localhost:10350/**, UI: **http://localhost:18000/digit-ui/**.

### Verify

```bash
./scripts/health-check.sh
./scripts/smoke-tests.sh
```

Postman: `scripts/run-postman.sh core` runs `digit-core-validation` against direct service ports. The `complaints` collection expects PGR on Kong and will not pass unless you add `pgr-services` back.

## DIGIT-DevOps (`unified-demo`)

- **Helm / env files**: `deploy-as-code/helm/environments/unified-demo.yaml` (and related) describe how DIGIT is wired in Kubernetes (image overrides, configmaps, ingress).  
- **This repo** runs a **curated subset** with **localhost** URLs and container names; image tags in `docker-compose.yml` are pinned for a stable laptop experience. When you change versions in DevOps, update the corresponding `image:` lines here (or add a small script later to sync tags from chart defaults).

Set `DIGIT_DEVOPS_PATH` if your clone is not at `../DIGIT-DevOps` — Tilt prints a hint when the directory exists.

## API examples (via Kong)

```bash
curl -X POST "http://localhost:18000/mdms-v2/v1/_search" \
  -H "Content-Type: application/json" \
  -d '{"MdmsCriteria":{"tenantId":"pg","moduleDetails":[{"moduleName":"tenant","masterDetails":[{"name":"tenants"}]}]},"RequestInfo":{"apiId":"Rainmaker"}}'
```

## Database

```bash
docker exec -it docker-postgres psql -U egov -d egov
```

## Tilt notes

- Nav buttons: Health Check, Smoke Tests, Nuke DB, Kong test, Re-seed MDMS, etc.  
- Stop the dev session: **`tilt down`** (or stop from the Tilt UI).  
- Tear down containers: **`docker compose down`**. Reset DB volumes: **`docker compose down -v`**.

## Optional local Tilt binary

Some Tilt releases may mark Docker Compose resources as ready before every container health check has passed. If that causes confusion in the UI, try another Tilt version from the [official install docs](https://docs.tilt.dev/install.html), or place a `tilt` executable your team trusts at **`./bin/tilt`** and run **`./bin/tilt up`** so this directory stays self-contained.

## Alternative: Compose only (no Tilt)

```bash
docker compose build db-migrations   # first time
docker compose up -d
docker compose logs -f
docker compose down
```

## Project layout

```
egov-digit-studio/
├── docker-compose.yml   # Service definitions
├── Tiltfile              # Tilt wiring (Compose only, no app hot-reload)
├── kong/kong.yml
├── nginx/               # digit-ui proxy + globalConfigs.js
├── db/                  # init SQL (e.g. full-dump.sql)
├── configs/persister/
└── scripts/             # health-check.sh, smoke-tests.sh, …
```

## Resource usage

Roughly **~4 GB RAM** for Docker for a comfortable full stack. Adjust `deploy.resources` in `docker-compose.yml` if your machine is constrained.
