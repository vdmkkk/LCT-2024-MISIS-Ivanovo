DC = docker-compose
DOC = docker
GIT = git

default: start

start:
	$(DC) --env-file .env up

# Target to perform a soft restart (without removing source images)
soft-restart:
	$(DC) stop
	$(DC) --env-file .env up

# Target to perform a hard restart (with removal of source images)
hard-restart: update
	$(DC) down
	$(DOC) rmi deploy-app
	$(DOC) rmi deploy-ml-app
	$(DC) --env-file .env up --build

# Target to perform a hard restart (with removal of source images, but without git pull)
restart:
	$(DC) down
	$(DOC) rmi deploy-app
	$(DOC) rmi deploy-ml-app
	$(DC) --env-file .env up --build

stop:
	$(DC) stop

clean:
	$(DC) down --rmi all

logs:
	$(DC) logs -f

update:
	$(GIT) pull

.PHONY: default start soft-restart hard-restart stop clean logs update