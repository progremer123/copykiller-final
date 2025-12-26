# Deployment notes for Ubuntu server

Files created in `scripts/` and `deploy/` are helpers to set up PostgreSQL and the backend service.

1) Install PostgreSQL and create DB/user

```bash
# on Ubuntu server, as root or sudo
sudo bash ./scripts/install_postgres.sh "your_db_password"
```

2) Import schema and initial data

```bash
sudo bash ./scripts/import_schema.sh
```

3) (Optional) Create systemd service for backend

Copy `deploy/plagiarism_backend.service` to `/etc/systemd/system/` and adjust paths/env.

```bash
sudo cp deploy/plagiarism_backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now plagiarism_backend
```

4) Nginx

Use the existing `nginx/nginx.conf` in repo or the example provided earlier. Restart nginx:

```bash
sudo systemctl restart nginx
```

5) Notes

- Scripts assume files are placed under `/home/ubuntu/copykiller-final/gpt-guarded-scribe-main` on the server.
- Adjust `plagiarism_backend.service` environment lines if you run Postgres/Redis in Docker.
