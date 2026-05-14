# Service startup sequence — egov-digit-studio

This document describes how services in **`docker-compose.yml`** start and depend on each other. **Tilt** (`tilt up`, `Tiltfile`) drives the same Compose project; use **[QUICK-SETUP.md](../QUICK-SETUP.md)** for the minimal command list. **Tilt installation and PATH:** **[TILT.md](TILT.md)**.

**Scope:** Laptop-local DIGIT subset (Postgres, PgBouncer, MDMS v2, core Spring services, Kong, studio services). **PGR / complaint APIs** are not defined in this compose file.

---

## 1. Source of truth

| Artifact | Role |
|----------|------|
| `docker-compose.yml` | Service definitions, `depends_on` with health conditions, healthchecks, env. |
| `Tiltfile` | Tilt UI grouping, `dc_resource` links, nav buttons; **Compose still enforces real startup order**. |
| `docker/db-migrations/` | Batch Flyway (`db-migrations` service) after Postgres is healthy. |

Tilt `resource_deps` are for UI ordering; **containers do not start until Compose `depends_on` conditions are satisfied**.

---

## 2. High-level order

```text
postgres-db (healthy)
    → db-migrations (exit 0)
        → pgbouncer (healthy, network alias `postgres`)
            → redpanda, redis, …
                → mdms-backend (healthy)
                    → egov-mdms-service / nginx (healthy)
                        → enc, idgen, localization, …
                            → user, workflow, studio chain, …
```

---

## 3. Infrastructure

| Service | Waits on | Notes |
|---------|-----------|--------|
| **postgres-db** | — | Init scripts in `db/` (e.g. `full-dump.sql`). Port **15432** → 5432. |
| **db-migrations** | `postgres-db` healthy | One-shot Flyway batch; `pull_policy: never` — build image first: `docker compose build db-migrations`. |
| **pgbouncer** | `postgres-db` + `db-migrations` completed | Pooler; Docker network alias **`postgres`** so apps use hostname `postgres`. Optional **client TLS** (`CLIENT_TLS_SSLMODE=allow`) with certs in `docker/pgbouncer-tls/`. JDBC URLs use `?sslmode=disable` for local dev. |
| **redis** | — | |
| **redpanda** | — | Kafka-compatible broker. |
| **elasticsearch** | — | Used by **inbox** (search). |
| **minio** (+ **minio-init**) | — | **minio-init** creates the bucket after MinIO is healthy. **egov-filestore** `depends_on` lists **`minio`** (not `minio-init`), plus **pgbouncer** and **egov-mdms-service**. |
| **gatus** | — | Optional monitoring (`--profile` / Tilt). |

---

## 4. MDMS path

| Service | Waits on | Notes |
|---------|-----------|--------|
| **mdms-backend** | `pgbouncer`, `redpanda` | Spring MDMS v2; connects via `postgres` (PgBouncer). |
| **egov-mdms-service** | `mdms-backend` healthy | **Nginx** reverse proxy to `mdms-backend:8094`. Healthcheck POSTs to `/mdms-v2/v1/_search`. Proxy sets **`Host: mdms-backend:8094`** so the backend does not see `127.0.0.1` (avoids 502). |

Most Spring services need **`egov-mdms-service` healthy** before they start.

---

## 5. Core Spring services (representative)

Exact `depends_on` blocks live in `docker-compose.yml`; below is the logical chain.

| Service | Typical upstream health gates | Notes |
|---------|----------------------------------|--------|
| **egov-enc-service** | `pgbouncer`, `egov-mdms-service` | Loads encryption policy from MDMS at startup; needs DB + MDMS. Spring Boot 3 actuator health. |
| **egov-idgen** | `pgbouncer`, `redpanda`, `egov-mdms-service` | Uses plain JDBC driver + MDMS. |
| **egov-otp** | `pgbouncer`, `redpanda` | |
| **egov-user** | `pgbouncer`, `redpanda`, `redis`, `egov-otp`, `egov-enc-service` | |
| **egov-workflow-v2** | `pgbouncer`, `redpanda`, `egov-idgen` | Long JVM start — healthcheck `start_period` is extended in compose. |
| **egov-localization** | `pgbouncer`, `redpanda`, `redis`, `egov-mdms-service` | |
| **boundary-service**, **egov-accesscontrol**, **egov-persister** | `pgbouncer` / `redpanda` + MDMS where listed | |
| **egov-filestore** | `pgbouncer`, `egov-mdms-service`, `minio` | Bucket may still be missing until **minio-init** has run; start order is usually fine because other services wait on filestore. |
| **egov-hrms** | user, idgen, mdms, … | |

---

## 6. Studio services (DIGIT-DevOps–aligned)

These depend on core services being healthy.

| Service | Main dependencies (see compose) | Notes |
|---------|-----------------------------------|--------|
| **health-service-request** | `pgbouncer`, `redpanda`, `egov-mdms-service` | |
| **health-individual** | `pgbouncer`, `redpanda`, `redis`, MDMS, **enc**, **idgen**, **user**, **localization** | |
| **public-service-init** | `pgbouncer`, `redpanda`, MDMS, **workflow**, **idgen**, **localization**, **health-individual**, **health-service-request** | **Go** binary: `DB_HOST=postgres` (PgBouncer alias); compose sets **`DB_SSL_MODE=disable`** and **`PGSSLMODE=disable`** with JDBC `?sslmode=disable`. Healthcheck: **TCP** (`nc -z 127.0.0.1 8080`), not actuator. |
| **public-service** | Same gates as **public-service-init**, plus **`public-service-init` healthy** | Go; same **`nc`** healthcheck style. |
| **user-otp** | `egov-otp`, `egov-user`, `egov-localization` | |
| **pdf-service** | MDMS, localization, filestore | Node; PDF config often from `configs/pdf-service/`. |
| **studio-pdf** | `pgbouncer`, `redpanda`, `egov-mdms-service`, `egov-filestore`, `egov-user`, `egov-workflow-v2`, `pdf-service`, `public-service` | Node service; see compose for full list. |
| **inbox** | **elasticsearch**, workflow, user, mdms | |
| **kong** | (see compose) | Gateway; **digit-ui** waits on Kong. |
| **digit-studio** | Kong | |

---

## 7. Tilt (`Tiltfile`)

**Entry:** from repo root:

```bash
cd egov-digit-studio
tilt up
# Or project-local binary: ./bin/tilt up
```

**UI:** http://localhost:10350/

**Labels (grouping):**

| Label | Examples |
|--------|----------|
| `infrastructure` | `postgres-db`, `db-migrations`, `pgbouncer`, `redis`, `redpanda`, `minio`, `minio-init`, `gatus`, … |
| `core-services` | `mdms-backend`, `egov-mdms-service`, `egov-enc-service`, `egov-idgen`, `egov-user`, `egov-workflow-v2`, `egov-localization`, `digit-ui`, … |
| `gateway` | `kong` |
| `frontend` | `digit-studio` |
| `studio` | `elasticsearch`, `health-individual`, `health-service-request`, `public-service-init`, `public-service`, `user-otp`, `pdf-service`, `studio-pdf`, `inbox`, … |
| `hrms` | `egov-hrms` |
| `tools` | `jupyter` |
| `maintenance` | `nuke-db` local resource |

**Nav buttons:** Health check, smoke tests, nuke DB, Kong test, idgen test, re-seed MDMS, Jupyter, Gatus (see `Tiltfile`).

**DIGIT-DevOps:** Optional `DIGIT_DEVOPS_PATH` or `../DIGIT-DevOps` for Helm reference; Tilt prints a hint at startup.

---

## 8. Ports (direct host access)

For **browser access** (DIGIT UI and routed APIs), use **Kong only**: **http://localhost:18000/** (e.g. **`/digit-ui/`**). The table below lists published ports for debugging, health scripts, and Postman-style calls—not an alternate UI entry point.

| Port / range | Service / role |
|--------------|----------------|
| 15432 | Postgres |
| 16379 | Redis |
| 18000–18002 | Kong |
| 18080 | digit-ui (host port exists for Compose; **do not use for browser access** — use Kong) |
| 18081–18120 | Various core + studio services (see `docker-compose.yml` `ports:`) |
| 19200 | Elasticsearch |
| 18888 | Jupyter (`--profile tools`) |
| 18889 | Gatus |

---

## 9. Troubleshooting

### Compose / health

```bash
docker compose ps
docker compose logs -f <service-name>
docker compose up -d --force-recreate <service-name>
docker compose config --quiet
```

### MDMS / nginx 502 from healthcheck

If `egov-mdms-service` fails healthchecks with 502, confirm **`nginx/mdms-proxy.conf`** forwards **`Host: mdms-backend:8094`** to the upstream (not the client `Host`).

### PgBouncer TLS

If PgBouncer exits on TLS load, ensure **`docker/pgbouncer-tls/server.key`** is readable inside the container (e.g. `chmod 644` for local dev keys). See comment on the `pgbouncer` volume in `docker-compose.yml`.

### Public-service (Go) DB / SSL

Compose pins **`DB_SSL_MODE=disable`** and **`PGSSLMODE=disable`** for **public-service-init** / **public-service** so the Go DB ping uses plain TLS-off mode to **`postgres`** (PgBouncer). PgBouncer may still expose **client TLS** with **`CLIENT_TLS_SSLMODE=allow`** for other clients; see `docker-compose.yml` **pgbouncer** service.

### MDMS data / idgen

```bash
docker exec docker-postgres psql -U egov -d egov -c "SELECT schemacode FROM eg_mdms_data LIMIT 20;"
```

### idgen sequence / format errors

See historical notes in older DIGIT docs; this stack seeds from **`db/`** and Flyway skips documented in `docker/db-migrations/migrate-all.sh` where they collide with the dump.

### digit-studio via Kong (blank UI or redirect to `http://digit-studio/...`)

1. **Host header:** Kong normally forwards **`Host: digit-studio`** to the container. Nginx may use that for redirects or absolute links. **`kong/kong.yml`** sets **`preserve_host: true`** on the **digit-studio** route so the browser’s host (**`localhost:18000`**) is passed through—reload Kong after edits: `docker compose exec kong kong reload` (or recreate the **kong** container).

2. **Trailing slash:** If **`http://localhost:18000/digit-studio`** (no slash) sent you to **`http://digit-studio/...`**, update **`nginx/digit-studio.conf`** ( **`absolute_redirect off`**, explicit **`location = /digit-studio`**) and recreate **digit-studio**: `docker compose up -d --force-recreate digit-studio`.

3. **Debugging:** Open DevTools → **Network** on **`http://localhost:18000/digit-studio/`** and confirm **`index.html`**, **`*.bundle.js`**, and **`globalConfigs.js`** all return **200** (not blocked or redirected).

### Inbox flapping or unhealthy

**inbox** depends on **Elasticsearch**, **Redpanda**, **MDMS**, **user**, and **workflow** — it starts late and is sensitive to **memory** and **ES readiness**.

1. **Elasticsearch on Linux:** if ES exits or logs `max virtual memory areas`, raise **`vm.max_map_count`** on the host (e.g. `sudo sysctl -w vm.max_map_count=262144`) and see [Elasticsearch VM settings](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#_set_vm_max_map_count_to_at_least_262144).
2. **RAM:** **digit-elasticsearch** is capped around **1.5 GB** JVM heap + overhead; **inbox** up to **768 MB**. On an 8 GB laptop, start the stack when little else is running, or raise `deploy.resources.limits.memory` in `docker-compose.yml` if you can spare RAM.
3. **Order:** inbox only starts after **`elasticsearch`** is healthy; the ES healthcheck waits for cluster status **green or yellow** (single-node clusters are often **yellow**, which is normal).
4. **Logs:** `docker compose logs -f elasticsearch` then `docker compose logs -f inbox` — look for OOM, connection refused to `elasticsearch:9200`, or long Spring startup before actuator is up.
5. **SERVICE_SEARCH_MAPPING** in **`configs/studio/inbox.env`** points many modules at **Kong** URLs that are **not** in this compose file; some code paths may error when those upstreams are missing (expected for a trimmed laptop stack).

---

## 10. Jupyter (optional)

```bash
docker compose --profile tools up -d jupyter
```

**URL:** http://localhost:18888  

Compose sets (among others): `DIGIT_URL=http://kong:8000`, `DIGIT_DIRECT_MDMS`, `DIGIT_DIRECT_USER`, `DIGIT_TENANT` — see `docker-compose.yml` **jupyter** service. Notebooks under `jupyter/` on the host are mounted into the container.

---

## 11. Gatus (optional)

```bash
docker compose --profile tools up -d gatus
```

**URL:** http://localhost:18889 — config in `gatus/config.yaml`.

---

## 12. CI

This repo path may not ship `.github/workflows/ci.yaml`. If you add CI, mirror **`./scripts/health-check.sh`** and **`./scripts/smoke-tests.sh`** after the stack is up, consistent with **QUICK-SETUP** / **README**.

---

## Related

- **[QUICK-SETUP.md](../QUICK-SETUP.md)** — prerequisites and `tilt up` / `docker compose build db-migrations`.
- **[TILT.md](TILT.md)** — Tilt CLI install, PATH, optional `./bin/tilt`.
- **[README.md](../README.md)** — overview and layout.
