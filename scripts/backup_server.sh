#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
archive="backups/world-${timestamp}.tar.gz"

mkdir -p backups

if docker compose ps --status running --services | grep -qx minecraft; then
    docker compose exec -T minecraft rcon-cli save-off >/dev/null 2>&1 || true
    docker compose exec -T minecraft rcon-cli save-all flush >/dev/null 2>&1 || true
fi

tar -czf "${archive}" data

if docker compose ps --status running --services | grep -qx minecraft; then
    docker compose exec -T minecraft rcon-cli save-on >/dev/null 2>&1 || true
fi

echo "Backup written to ${archive}"
