.PHONY: init down dev pre_commit tests drop_db

START_COMMAND := python main.py
DB_CONTAINER := postgres_uncle
DB_VOLUME := $$(basename "$$(pwd)")_postgres_data
TESTS_DB_CONTAINER := postgres_tests_uncle
TESTS_DB_VOLUME := $$(basename "$$(pwd)")_postgres_tests_data

define docker_start_lock
	@while true; do \
		sleep 1; \
		result_db=$$(docker inspect -f '{{json .State.Health.Status}}' $(1)); \
		if [ "$$result_db" = "\"healthy\"" ]; then \
			echo "$(1) are healthy"; \
			break; \
		fi; \
	done
endef

init:
	pip install -r requirements.txt
	pre-commit install

down:
	docker compose down

dev: down
	docker compose up postgres redis -d
	$(call docker_start_lock,$(DB_CONTAINER))
	alembic upgrade head
	$(START_COMMAND)

pre_commit:
	sh pre_commit/pre_commit.sh

tests:
	docker compose up postgres_tests -d
	$(call docker_start_lock,$(TESTS_DB_CONTAINER))
	pytest -s
	docker rm -f $(TESTS_DB_CONTAINER)
	docker volume rm $(TESTS_DB_VOLUME)

drop_db: down 
	if docker volume ls -q | grep -q $(DB_VOLUME); then \
		docker volume rm $(DB_VOLUME); \
		echo "successfully drop_db 1";\
	fi
