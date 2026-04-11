#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
    echo "Missing .env. Copy .env.example to .env first."
    exit 1
fi

docker compose pull minecraft
docker compose up -d --force-recreate minecraft
docker compose ps
