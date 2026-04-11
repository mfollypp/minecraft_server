# Managed Mods

Do not maintain this directory by hand.

The source of truth is `manifests/mods.json`. Rebuild the directory with:

```bash
make sync-mods
```

Each entry pins an exact Modrinth `version_id` so future reinstalls are deterministic.
