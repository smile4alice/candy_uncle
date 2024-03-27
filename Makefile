.PHONY: down dev drop_db

START_COMMAND := python main.py
DB_CONTAINER := postgres_uncle
DB_VOLUME := $$(basename "$$(pwd)")_postgres_data

down:
	docker compose down

dev: down
	docker compose up postgres -d
	@while true; do \
		sleep 1; \
		result_db=$$(docker inspect -f '{{json .State.Health.Status}}' $(DB_CONTAINER)); \
		if [ "$$result_db" = "\"healthy\"" ]; then \
			echo "Services are healthy"; \
			break; \
		fi; \
	done
	alembic upgrade head
	$(START_COMMAND)

drop_db: down 
	if docker volume ls -q | grep -q $(DB_VOLUME); then \
		docker volume rm $(DB_VOLUME); \
		echo "successfully drop_db 1";\
	fi
