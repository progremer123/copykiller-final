#!/usr/bin/env bash
set -euo pipefail

# install_postgres.sh
# Installs PostgreSQL on Ubuntu, sets postgres password, and creates plagiarism_db.
# Usage: sudo ./install_postgres.sh <POSTGRES_PASSWORD>

if [ "$#" -ne 1 ]; then
  echo "Usage: sudo $0 <POSTGRES_PASSWORD>"
  exit 1
fi

PG_PASS="$1"

echo "Updating apt and installing PostgreSQL..."
apt update
DEBIAN_FRONTEND=noninteractive apt install -y postgresql postgresql-contrib

echo "Starting and enabling postgresql service..."
systemctl enable --now postgresql

echo "Setting postgres user password..."
sudo -u postgres psql -v ON_ERROR_STOP=1 -c "ALTER USER postgres WITH PASSWORD '${PG_PASS}';"

echo "Creating database 'plagiarism_db' if not exists..."
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='plagiarism_db'" | grep -q 1; then
  echo "Database already exists."
else
  sudo -u postgres psql -c "CREATE DATABASE plagiarism_db;"
  sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE plagiarism_db TO postgres;"
fi

echo "PostgreSQL installed and database 'plagiarism_db' ready."
echo "Next: run 'sudo ./scripts/import_schema.sh' to load schema and initial data."
