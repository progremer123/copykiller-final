#!/usr/bin/env bash
set -euo pipefail

# import_schema.sh
# Imports SQL schema and initialization files into plagiarism_db.
# Usage: sudo ./scripts/import_schema.sh

SCHEMA_DIR="$(dirname "$0")/.."/database

SQL1="$SCHEMA_DIR/01_schema.sql"
SQL2="$SCHEMA_DIR/02_init.sql"

if [ ! -f "$SQL1" ]; then
  echo "Schema file not found: $SQL1"
  exit 1
fi

echo "Importing schema: $SQL1"
sudo -u postgres psql -d plagiarism_db -f "$SQL1"

if [ -f "$SQL2" ]; then
  echo "Importing initial data: $SQL2"
  sudo -u postgres psql -d plagiarism_db -f "$SQL2"
else
  echo "No init file found ($SQL2), skipping."
fi

echo "Database schema and initial data imported."
