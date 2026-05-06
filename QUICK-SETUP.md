# Quick setup (Tilt)

Bring up the laptop-local DIGIT stack using **Tilt**. Tilt still uses **`docker-compose.yml`** underneath (build, health checks, dependencies).

**Full walkthrough:** satisfy [Prerequisites](#prerequisites), install Tilt ([Install Tilt](#install-tilt)), then follow the numbered steps. When services are healthy in Tilt, open the URLs in [Access after startup](#access-after-startup).

---

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Docker** | Recent Engine; ~8 GB+ RAM comfortable for the full stack. |
| **Docker Compose v2** | Required (`docker compose`); Tilt invokes it for this project. |
| **Git** | To clone the repository. |
| **Tilt CLI** | Install in the next section; verify with `tilt version`. |

**Optional:** If you use a project-local binary, put it at **`./bin/tilt`** and run **`./bin/tilt up`** instead of `tilt up` — see [README.md — Optional local Tilt binary](README.md#optional-local-tilt-binary).

No Kubernetes or cloud accounts are required.

---

## Install Tilt

Install the **Tilt CLI** so `tilt` is on your `PATH`. This repo uses Tilt with **Docker Compose only** (you do **not** need a local Kubernetes cluster for `egov-digit-studio`).

Official page (all options): **[https://docs.tilt.dev/install.html](https://docs.tilt.dev/install.html)**.

### Linux

Recommended: official install script (uses a package manager when available, otherwise installs the binary to a directory on your `PATH`; you may need `sudo`):

```bash
curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash
tilt version
```

Or with [Homebrew](https://brew.sh/) on Linux:

```bash
brew install tilt
tilt version
```

### macOS

Same install script as Linux (often picks up Homebrew automatically):

```bash
curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash
tilt version
```

Or install only via Homebrew:

```bash
brew install tilt
tilt version
```

### Windows

In **PowerShell**:

```powershell
iex ((new-object net.webclient).DownloadString('https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.ps1'))
```

Then open a new terminal and run `tilt version`. [Scoop](https://scoop.sh/) and other options are listed on the [install page](https://docs.tilt.dev/install.html).

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

Defaults are fine for local dev. To change Postgres password or image tags, add a `.env` in this folder (variables match `docker-compose.yml` header comments, e.g. `POSTGRES_PASSWORD`, `IMAGE_*`).

```bash
# optional
nano .env
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

If you use **`./bin/tilt`** (optional local binary):

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

## PgBouncer TLS (`docker/pgbouncer-tls/`)

If you regenerate `server.crt` / `server.key`, keep keys readable for the container user (e.g. `chmod 644` on both for this dev layout). See the comment on the `pgbouncer` volume in `docker-compose.yml`.

---

## Troubleshooting

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

See also **`Tiltfile`** (grouped resources, links, nav buttons) and **`README.md`** for layout and optional **`./bin/tilt`**.
