# Minecraft Server

This repository contains a Docker-based Minecraft Java server setup.

The plan for this repo is simple:

- keep this repository as the base server setup
- maintain future Minecraft server versions in separate branches
- use each branch as the source of truth for that specific server version

## Branch Strategy

Each Minecraft version should live in its own branch.

Examples:

- `master`: shared base or latest active setup
- `1.21.11`
- `1.22.x`
- `26.1.2`

When a new server version is needed:

1. Create a new branch from the closest existing version.
2. Update the server version, mods, and config in that branch (compose.yaml image version and environments).
3. Keep fixes for that version on the same branch.

This makes it easier to preserve working setups for older servers without mixing changes between versions.

## What Is In This Repo

- `compose.yaml`: Docker Compose setup for the server

## Basic Workflow

0. Set system environment variable `MINESERVER_RCON_PASSWORD` for any value you want
1. Switch to the branch for the Minecraft version you want to run.
2. Start the server by running:
    ```powershell
    docker compose up -d
    ```
3. Stop the server by running
    ```powershell
    docker compose stop minecraft
    ```
4. Update the server by running
    ```powershell
    docker compose pull minecraft
    docker compose up -d --force-recreate minecraft
    ```