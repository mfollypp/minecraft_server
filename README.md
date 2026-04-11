# Minecraft Server

This repository runs a private Minecraft Java server on a Linux notebook with:

- Fabric mods
- Tailscale for remote access
- Docker Compose for reproducible setup
- a pinned Modrinth manifest for mod sync

The Minecraft container shares the Tailscale container's network namespace, so players join through the Tailscale node instead of your notebook's normal LAN address.

## Repository Layout

The README now matches the current repository contents relevant to running the server:

- `compose.yaml`: starts `tailscale` and `minecraft`
- `.env.example`: local configuration template
- `config/server.properties`: tracked Minecraft server settings
- `config/ops.json`: operator list
- `config/whitelist.json`: whitelist data
- `manifests/mods.json`: pinned Modrinth mod manifest
- `mods/`: generated mod jars plus `mods/README.md`
- `scripts/start_server.sh`: start the stack
- `scripts/stop_server.sh`: stop the stack
- `scripts/update_server.sh`: recreate the Minecraft container after config or version changes
- `scripts/backup_server.sh`: create a world backup archive
- `scripts/sync_mods.py`: sync pinned mods from Modrinth
- `scripts/sync_mods.sh`: shell wrapper for mod sync
- `tailscale/state/`: persistent Tailscale state
- `data/`: world and generated server data
- `backups/`: backup output

There is also a `.devcontainer/` directory for the development environment, but it is not part of the runtime setup.

## Platform Assumption

This Compose setup is intended for a Linux notebook because it mounts `/dev/net/tun` and gives the Tailscale container the capabilities it needs.

If you are on macOS or Windows with Docker Desktop, run Tailscale on the host instead of in Compose.

## Prerequisites

On the notebook:

- Docker Engine with Compose support
- a Tailscale account
- Minecraft Java Edition if you also want to play from the notebook

For players:

- Minecraft Java Edition
- Tailscale installed and signed in
- the same Minecraft version as the server
- the same Fabric loader major version as the server
- the same required client mods as the server modpack

## Minimal Setup Guide

### Host: Set Up The Server

1. Copy the local environment template:

```bash
cp .env.example .env
```

2. Edit `.env` and set these values:

- `TS_AUTHKEY`
- `TS_HOSTNAME`
- `TZ`
- `VERSION`
- `MEMORY`
- optionally `FABRIC_LOADER_VERSION`
- optionally `FABRIC_INSTALLER_VERSION`

3. Edit the pinned mod manifest:

```bash
sed -n '1,200p' manifests/mods.json
```

Replace `replace-with-modrinth-version-id` with real Modrinth version IDs for the mods you want.

4. Sync the mod directory from the manifest:

```bash
make sync-mods
```

5. Start the server stack:

```bash
./scripts/start_server.sh
```

6. Follow startup logs:

```bash
docker compose logs -f tailscale minecraft
```

7. Get the Tailscale IP of the notebook node:

```bash
docker compose exec tailscale tailscale ip -4
```

8. Share that IP with players as:

```text
<tailscale-ip>:25565
```

### Players: Join The Server

1. Install Tailscale and sign in.
2. Join the same tailnet, or accept access to the shared node.
3. Install Minecraft Java Edition.
4. Install the same Minecraft version as the server.
5. Install Fabric Loader matching the server's major Fabric version.
6. Install the same required client mods.
7. Open Minecraft Multiplayer.
8. Add the server address:

```text
<tailscale-ip>:25565
```

If MagicDNS is enabled, players can also try:

```text
<ts-hostname>:25565
```

## Networking Model

The Minecraft container uses:

```yaml
network_mode: service:tailscale
```

That means:

- the Minecraft server does not publish a normal Docker `ports:` mapping
- inbound traffic reaches Minecraft through the Tailscale container's network stack
- players connect using the Tailscale IP or MagicDNS name

## Mod Manifest

The source of truth for mods is [manifests/mods.json](/workspaces/minecraft_server/manifests/mods.json:1).

Example entry:

```json
{
  "slug": "fabric-api",
  "version_id": "replace-with-modrinth-version-id",
  "required_on_client": true
}
```

Run this after changing the manifest:

```bash
make sync-mods
```

The sync script downloads the primary file for each pinned Modrinth version, verifies its SHA-1 checksum, writes the jar into `mods/`, and removes stale managed jars.

## Common Commands

Start:

```bash
./scripts/start_server.sh
```

Stop:

```bash
./scripts/stop_server.sh
```

Restart after config, version, or mod changes:

```bash
./scripts/update_server.sh
```

Sync mods:

```bash
make sync-mods
```

Backup the world:

```bash
./scripts/backup_server.sh
```

Show logs:

```bash
docker compose logs -f tailscale minecraft
```

Show the Tailscale IP:

```bash
docker compose exec tailscale tailscale ip -4
```

## Updating Later

When you come back to the game later:

1. Back up the world:

```bash
./scripts/backup_server.sh
```

2. Update `.env` if you want a new Minecraft or Fabric version.
3. Update pinned mod `version_id` values in `manifests/mods.json`.
4. Re-sync the mods:

```bash
make sync-mods
```

5. Recreate the Minecraft container:

```bash
./scripts/update_server.sh
```

## Tracked vs Local State

Commit:

- `compose.yaml`
- `.env.example`
- `config/server.properties`
- `config/ops.json`
- `config/whitelist.json`
- `manifests/mods.json`
- `scripts/`

Do not commit:

- `.env`
- `data/`
- `backups/`
- `tailscale/state/`
- unmanaged downloaded mod jars

## Troubleshooting

### The Tailscale Container Does Not Come Online

Check:

- the notebook is Linux and has `/dev/net/tun`
- `TS_AUTHKEY` is valid
- the container has `NET_ADMIN` and `NET_RAW`
- your environment allows TUN devices inside containers

### Players Cannot Connect

Check:

- both sides are logged in to Tailscale
- the notebook has a Tailscale IP
- the Minecraft server finished starting
- all players are using Minecraft Java Edition
- all players match the server's Minecraft version, Fabric version, and required mods

### The Server Crashes After Mod Changes

Usually one of these is wrong:

- a mod targets a different Minecraft version
- a dependency is missing
- a mod is client-only and should not be on the server
- the world or config is incompatible with the update
