make run-tests:
	docker-compose down
	docker-compose -f tests/docker-compose.testing.yml up --attach tests --exit-code-from tests


up:
	make build
	make start
	make start-load-data-to-elastic

down:
	docker compose down -v

dev-up:
	make dev-build
	make dev-start

dev-down:
	docker compose -f docker-compose.dev.yml down -v

dev-stop:
	docker compose -f docker-compose.dev.yml stop

build:
	docker-compose build --no-cache

dev-build:
	docker-compose -f docker-compose.dev.yml build --no-cache

start:
	docker-compose up -d

dev-start:
	docker-compose -f docker-compose.dev.yml up -d

start-load-data-to-elastic:
	docker-compose exec -d etl sh -c "python etl.py"

stop:
	docker-compose stop

remove:
	docker-compose down

remove-all:
	docker-compose down -v

force-remove:
	docker-compose down --remove-orphans -v
