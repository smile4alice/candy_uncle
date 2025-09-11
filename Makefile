.PHONY: down run export_secret

down:
	docker compose down

run: down
	docker compose up -d --build

export_env:
	base64 -w 0 .env > env.base64
