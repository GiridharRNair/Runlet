<p align="center">
  <img src="assets/Runlet.png" alt="Runlet" width="640">
</p>

Lightweight REST API for executing single-file code in a sandboxed environment. Supports Python, JavaScript (Node.js), C++, and Java.

## Features

- Sandboxed execution via [isolate](https://github.com/ioi/isolate) (the IOI contest sandbox) — per-run process, filesystem, and cgroup memory isolation
- Configurable time and memory limits, with `TLE` / `MLE` / `RE` / `CE` status reporting
- A small pool of reusable sandboxes (`MAX_BOXES`) so requests queue instead of spawning unbounded processes
- Per-IP rate limiting on execution requests
- Runs behind Caddy in production for automatic HTTPS

## API

| Method | Path        | Description                             |
| ------ | ----------- | ---------------------------------------- |
| POST   | `/execute`  | Run a single file of code                |
| GET    | `/runtimes` | List supported languages and versions    |
| GET    | `/health`   | Health check                             |

### `POST /execute`

Request:

```json
{
  "language": "python",
  "code": "print('hi')",
  "stdin": ""
}
```

`language` is one of `python`, `javascript`, `cpp`, `java`.

Response:

```json
{
  "status": "OK",
  "stdout": "hi\n",
  "stderr": "",
  "time": 0.031,
  "memory": 8192
}
```

`status` is one of:

- `OK` — ran successfully
- `TLE` — time limit exceeded
- `MLE` — memory limit exceeded (only enforced when `USE_CGROUPS=true`)
- `RE` — runtime error (non-zero exit, signal, etc.)
- `CE` — compile error (C++ and Java only)

## Running locally

Requires [uv](https://docs.astral.sh/uv/) and Docker.

```bash
uv sync
uv run ruff check .
uv run ruff format .
```

**Dev** (hot reload, memory limits disabled, mounts source into the container):

```bash
docker compose -f docker-compose.dev.yml up
```

**Prod-like** (runs a built image behind Caddy; requires an image pushed to GHCR):

```bash
IMAGE=ghcr.io/giridharrnair/code-execution-engine-api:latest docker compose up
```

## Configuration

Set via environment variables — see [`app/config.py`](app/config.py):

| Variable                    | Default | Description                                                          |
| ---------------------------- | ------- | ---------------------------------------------------------------------- |
| `TIME_LIMIT`                 | `5.0`   | Execution wall time limit (seconds)                                   |
| `MEMORY_LIMIT`                | `256`   | Execution memory limit (MB)                                           |
| `COMPILE_TIME_LIMIT`          | `30.0`  | Compile step time limit (seconds), C++/Java                           |
| `COMPILE_MEMORY_LIMIT`        | `512`   | Compile step memory limit (MB), C++/Java                              |
| `MAX_BOXES`                   | `3`     | Number of concurrent isolate sandboxes                                |
| `USE_CGROUPS`                 | `true`  | Enforce memory limits via cgroups (disabled in `docker-compose.dev.yml`) |
| `CODE_EXECUTION_RATE_LIMIT`   | `10`    | Requests per minute allowed to `/execute` per IP                      |

## Testing

Integration tests hit a running instance of the API over HTTP:

```bash
API_URL=http://localhost:8000 uv run pytest
```

Set `USE_CGROUPS` to match whatever server you're testing against — the memory-limit tests assert different behavior depending on whether cgroup enforcement is on.

## Deployment

On every push to `main`:

1. [`docker-publish.yaml`](.github/workflows/docker-publish.yaml) builds the image and pushes it to GHCR.
2. [`deploy.yaml`](.github/workflows/deploy.yaml) copies `docker-compose.yml` and `Caddyfile` to a DigitalOcean droplet over SSH, pulls the new image, and recreates the containers. Caddy handles automatic HTTPS in front of the app.

Required repo secrets: `DO_HOST`, `DO_USERNAME`, `DO_SSH_KEY`, and optionally `DO_PORT`.
