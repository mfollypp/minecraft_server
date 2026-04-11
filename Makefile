.PHONY: start stop restart logs backup validate sync-mods

start:
	./scripts/start_server.sh

stop:
	./scripts/stop_server.sh

restart:
	./scripts/update_server.sh

logs:
	docker compose logs -f minecraft

backup:
	./scripts/backup_server.sh

validate:
	docker compose config

sync-mods:
	./scripts/sync_mods.sh
