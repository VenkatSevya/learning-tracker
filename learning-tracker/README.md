# learning-tracker

A modern 3-tier web application, **containerised and shipped with a CI/CD pipeline**.
You log what you learned each day (topic, notes, hours) and see simple statistics.
The app is small on purpose; the point is the delivery system around it.

```
 Browser ──► Nginx :80 ──┬─► /      React app (static files)
              public     └─► /api/  ──► FastAPI :8000 ──► PostgreSQL
                                          private          private

 git push ──► GitHub Actions ──► 1. backend tests (Python 3.12 + 3.13) and React build
                                 2. start the real stack with Docker Compose
                                    and smoke-test it through Nginx
                                 3. publish both images to GHCR
```

## Stack

| Piece | Tool |
|---|---|
| Front end | React 19, built with Vite, served by Nginx |
| API | Python, FastAPI, Pydantic, SQLAlchemy 2 |
| Database | PostgreSQL 16 (SQLite in unit tests) |
| Packaging | Docker multi-stage builds (Node is not in the final front-end image), non-root user, health checks |
| Run | Docker Compose, database health-gated start-up, only Nginx is public |
| CI/CD | GitHub Actions: tests, build check, integration test, publish to GHCR |

## Run it (needs Docker)

```bash
git clone https://github.com/<your-user>/learning-tracker.git
cd learning-tracker
cp .env.example .env            # then edit .env and choose a password
docker compose up -d --build
docker compose ps
bash scripts/smoke_test.sh
```

Open `http://localhost/`. Interactive API documentation is at `http://localhost/api/docs`.

Stop: `docker compose down` (keep data) or `docker compose down -v` (delete data).

## Develop without Docker

```bash
# API  (terminal 1)
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -v
uvicorn app.main:app --reload          # http://localhost:8000/api/docs

# React (terminal 2)
cd frontend
npm install
npm run dev                            # http://localhost:5173 (proxies /api to port 8000)
```

## Design decisions (good interview material)

- **Multi-stage builds**: the React app is compiled in a Node image; the final image is just Nginx plus static files.
- **Config from environment variables**: the same image runs in CI, on a laptop and on a server.
- **Only Nginx is public**: the API and the database are not exposed.
- **`/api/health` checks the database**: used by Docker HEALTHCHECK, CI and the smoke test.
- **Input validation with Pydantic**: bad data returns a clear 422 error, not a crash.
- **CI runs the real stack**, not just unit tests.

## Roadmap

- Terraform: create the EC2 server and security group as code
- Deploy job over SSH on every push to main
- HTTPS with Let's Encrypt
- Prometheus and Grafana monitoring
- Database migrations with Alembic
- Kubernetes and Argo CD
