# Quick setup (Tilt)

Bring up the laptop-local DIGIT stack using **Tilt**. Tilt still uses **`docker-compose.yml`** underneath (build, health checks, dependencies).

**Full walkthrough:** satisfy [Prerequisites](#prerequisites), install the Tilt CLI (**[docs/TILT.md](docs/TILT.md)** — single place for install, PATH, and `./bin/tilt`), then follow the numbered steps. When services are healthy in Tilt, open the URLs in [Access after startup](#access-after-startup).

---

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Docker Engine** | Install per the official guide: **[Install Docker Engine](https://docs.docker.com/engine/install/)**. A recent release is best; ~8 GB+ RAM is comfortable for the full stack. |
| **Linux: `docker` group** | **Required** for the flow in this doc: your user must be able to run **`docker`** and **`docker compose`** without typing `sudo` each time (Tilt and helper scripts assume that). Add your user to the **`docker`** group (see below), then **log out and back in** or reboot. Membership in the **`sudo`** / **`wheel`** group is separate—it does **not** grant access to the Docker socket by itself. |
| **Docker Compose v2** | This project uses the **`docker compose`** CLI (plugin), not legacy `docker-compose`. See **[Install Docker Compose](https://docs.docker.com/compose/install/)** (Linux plugin, or use Docker Desktop below). |
| **Git** | To clone the repository. |
| **Tilt CLI** | Install and troubleshoot in **[docs/TILT.md](docs/TILT.md)**; then `tilt version` should work. |

For **macOS and Windows**, **[Docker Desktop](https://docs.docker.com/desktop/)** installs both Docker Engine and Compose v2 together; you normally do not manage a `docker` group by hand.

No Kubernetes or cloud accounts are required.

### Add your user to the `docker` group (Linux)

Run once (you need a session that already has `sudo`, e.g. an admin added you to **`sudo`** first, or you use the root account):

```bash
sudo groupadd docker 2>/dev/null || true
sudo usermod -aG docker "$USER"
```

Then **log out and back in** (or `sudo reboot`). Verify:

```bash
groups | grep -w docker
docker run --rm hello-world
```

You need **`sudo` only for the one-time `usermod` above** (unless your site uses rootless Docker or another socket—then follow that layout instead).

**Not supported in this guide:** running the whole stack by prefixing every command with `sudo docker …`; Tilt and scripts will not behave well with interactive password prompts.

---

## Access after startup

When **`tilt up`** has finished bringing dependencies up (green / healthy in the Tilt UI, or after the first wave of health checks passes—often **several minutes** on a cold start):

| What | URL |
|------|-----|
| **Tilt UI** (resource graph, logs, links) | **http://localhost:10350/** |
| **DIGIT UI** (frontend — **only** via Kong) | **http://localhost:18000/digit-ui/** |

Use **http://localhost:18000/** as the single entry point for the app and APIs in the browser (Kong routes everything, including **`/digit-ui/`**). Do not use the `digit-ui` host port for normal access; this project expects traffic through Kong only.

---

## 1. Project directory

```bash
cd egov-digit-studio
```

---

## 2. (Optional) `.env`

Defaults are fine for local dev. Create a **`.env` file in this folder** (`egov-digit-studio/`) when you want to override anything Compose interpolates from the environment: **Postgres password**, **custom or local image tags**, or other variables referenced in **`docker-compose.yml`**.

- **Where to look:** open **`docker-compose.yml`** — the top comment block lists the `IMAGE_*` variables used for studio/sandbox services; each `image:` line shows the pattern `${VAR:-default-registry/tag}`.
- **Local builds:** if you built an image locally (for example `egov-digit-studio-db-migrations:local` for `db-migrations`), you normally do not need a variable unless you changed the Compose `image:` name. For published services, set the matching `IMAGE_*` to your registry/tag.

Example **`.env`** snippets (adjust tags to your own; lines are optional):

```bash
# Database password (must stay consistent across services that reference it)
POSTGRES_PASSWORD=egov123

# Override published images — names must match variables in docker-compose.yml
IMAGE_EGOV_USER=myregistry.example/egov-user:my-branch-abc123
IMAGE_DIGIT_STUDIO=egovio/digit-studio:studio-other-tag
IMAGE_INBOX=myregistry.example/inbox:local-dev

# Example: point MDMS at a specific tag (see docker-compose.yml for the default)
IMAGE_MDMS_V2=egovio/mdms-v2:master-1e8d2bb
```

```bash
# optional
nano .env
```

Validate interpolation without starting containers:

```bash
docker compose config --quiet
```

---

## 3. Build the DB migrations image (first time, or after changing migrations)

Tilt starts the same `db-migrations` service as Compose; that image is **built locally** with `pull_policy: never`:

```bash
docker compose build db-migrations
```

Skip if you already built it and did not touch `docker/db-migrations/`.

---

## 4. Start with Tilt

```bash
tilt up
```

Optional project-local binary (see **[docs/TILT.md](docs/TILT.md)**):

```bash
./bin/tilt up
```

The first full start can take **several minutes**. Use the Tilt UI to watch resource health.

When things look ready, use **[Access after startup](#access-after-startup)** for the Tilt dashboard and the frontend URLs.

---

## 5. Checks (optional)

From the same folder (works whether Tilt or Compose started the stack):

```bash
./scripts/health-check.sh
./scripts/smoke-tests.sh
```

---

## 6. Stop

```bash
tilt down
```

Or stop from the Tilt UI. Containers started by Tilt are Compose services; you can still run **`docker compose down`** if you need to clean up from a terminal.

**Reset database volumes** (fresh DB next time):

```bash
docker compose down -v
```

---

## 7. Recreate one service (Compose)

Useful after changing an image tag in `.env` or rebuilding one image. These commands assume **`docker compose` works without `sudo`** (see [Prerequisites](#prerequisites)).

Stop and remove **only** the named service containers (Compose v2 accepts optional service names on `down`):

```bash
docker compose down egov-user
```

Bring that service back (fresh container from the current `image:` / `.env`):

```bash
docker compose up -d --force-recreate egov-user
```

Replace `egov-user` with any **service name** from `docker-compose.yml` (the key under `services:`, not the image name).

---

## PgBouncer TLS (`docker/pgbouncer-tls/`)

If you regenerate `server.crt` / `server.key`, keep keys readable for the container user (e.g. `chmod 644` on both for this dev layout). See the comment on the `pgbouncer` volume in `docker-compose.yml`.

---

## Troubleshooting

**Tilt not on PATH, `./bin/tilt`, or multiple `tilt` binaries:** **[docs/TILT.md](docs/TILT.md)**.

```bash
# Compose file sanity check
docker compose config --quiet

# Logs for one service (after stack is up)
docker compose logs -f egov-mdms-service
```

---

## Without Tilt (Compose only)

If you ever need plain Compose without the dashboard:

```bash
docker compose build db-migrations   # first time
docker compose up -d
docker compose ps
docker compose down
```

See also **`Tiltfile`**, **[docs/TILT.md](docs/TILT.md)** (Tilt install and PATH), and **`README.md`**.
