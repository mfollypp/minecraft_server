# Minecraft Server

This repository runs a private Minecraft Java server on a Windows notebook with:

- Fabric mods
- Docker Compose for reproducible server setup
- a pinned Modrinth manifest for mod sync
- two remote access options: Tailscale or `playit.gg`

The runtime model on Windows is simple:

- Docker runs the Minecraft server container
- Docker publishes port `25565` on the Windows host
- you expose that host port either through Tailscale or through `playit.gg`

## Exposure Options

You have two supported ways to let other people join:

### Option 1: Tailscale

Use this when you want a private network and do not mind requiring players to install Tailscale.

- you run Tailscale on the Windows host
- players also install Tailscale
- players connect to your notebook's Tailscale IP on port `25565`

### Option 2: playit.gg

Use this when you want players to join without installing Tailscale.

- you run the `playit.gg` agent on the Windows host
- players do not need Tailscale
- players join using the public `playit.gg` address assigned to your tunnel

According to playit.gg's current docs, only the host runs the agent and players just connect. Sources:

- https://playit.gg/download/windows
- https://playit.gg/support/how-to-setup-a-mc-server/

## Repository Layout

The README matches the current repository contents relevant to running the server:

- `compose.yaml`: starts the Minecraft server container
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
- `data/`: world and generated server data
- `backups/`: backup output

There is also a `.devcontainer/` directory for the development environment. The `tailscale/state/` directory is left over from the earlier Linux-sidecar approach and is not used on Windows.

## Platform Assumption

This setup is for Windows with Docker Desktop. Remote access should run on the Windows host, not in Docker.

## Prerequisites

On the notebook:

- Docker Desktop with Compose support
- Minecraft Java Edition if you also want to play from the notebook
- one remote access option:
  - Tailscale for Windows, or
  - `playit.gg` for Windows

For players using Tailscale:

- Minecraft Java Edition
- Tailscale installed and signed in
- access to your tailnet, or access to the shared device
- the same Minecraft version as the server
- the same Fabric loader major version as the server
- the same required client mods as the server modpack

For players using `playit.gg`:

- Minecraft Java Edition
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

- `TZ`
- `VERSION`
- `MEMORY`
- `SERVER_PORT`
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
docker compose logs -f minecraft
```

7. Choose one remote access option below.

### Option A: Tailscale Setup On Windows Host

1. Install and sign in to Tailscale on Windows.
2. Get your notebook's Tailscale IPv4 address in PowerShell:

```powershell
tailscale ip -4
```

3. Share this address with players:

```text
<tailscale-ip>:25565
```

### Option B: playit.gg Setup On Windows Host

1. Download the Windows agent from:

```text
https://playit.gg/download/windows
```

2. Run the `playit.gg` Windows agent on the notebook.
3. Follow the browser-based setup or claim flow shown by the agent.
4. Create a Minecraft Java tunnel that forwards to your local server on:

```text
127.0.0.1:25565
```

5. Copy the public `playit.gg` address that gets assigned to the tunnel.
6. Share that address with players.

## Players: Join The Server

### Join Through Tailscale

1. Install Tailscale and sign in.
2. Join the same tailnet, or accept access to the shared device.
3. Install Minecraft Java Edition.
4. Install the same Minecraft version as the server.
5. Install Fabric Loader matching the server's major Fabric version.
6. Install the same required client mods.
7. Open Minecraft Multiplayer.
8. Add the server address:

```text
<tailscale-ip>:25565
```

If MagicDNS is enabled in your tailnet, players can also try the Windows notebook's Tailscale DNS name instead of the IP.

### Join Through playit.gg

1. Install Minecraft Java Edition.
2. Install the same Minecraft version as the server.
3. Install Fabric Loader matching the server's major Fabric version.
4. Install the same required client mods.
5. Open Minecraft Multiplayer.
6. Add the public `playit.gg` address provided by the host.

No Tailscale install is required for players in this option.

## Networking Model

The Minecraft container publishes a normal host port:

```yaml
ports:
  - "${SERVER_PORT:-25565}:25565"
```

That means:

- Docker exposes Minecraft on the Windows host
- Tailscale can expose that host to your friends privately
- `playit.gg` can expose that host to your friends publicly without port forwarding

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
docker compose logs -f minecraft
```

Show the Windows host Tailscale IP:

```powershell
tailscale ip -4
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
- unmanaged downloaded mod jars

## Troubleshooting

### Players Cannot Connect Through Tailscale

Check:

- Tailscale is running on the Windows notebook
- the notebook has a Tailscale IP
- Docker Desktop is running
- the Minecraft server finished starting
- Windows Firewall is not blocking the service on the Tailscale interface
- all players are using Minecraft Java Edition
- all players match the server's Minecraft version, Fabric version, and required mods

### Players Cannot Connect Through playit.gg

Check:

- the `playit.gg` agent is running on the Windows notebook
- the tunnel targets `127.0.0.1:25565`
- Docker Desktop is running
- the Minecraft server finished starting
- you shared the exact public `playit.gg` address assigned to the tunnel
- all players are using Minecraft Java Edition
- all players match the server's Minecraft version, Fabric version, and required mods

### The Server Crashes After Mod Changes

Usually one of these is wrong:

- a mod targets a different Minecraft version
- a dependency is missing
- a mod is client-only and should not be on the server
- the world or config is incompatible with the update
