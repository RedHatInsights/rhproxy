
MIRROR_SERVERS="env/mirror.servers"

all:	help

help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  help            show this help message"
	@echo "  lint            run all linters for the rhproxy installer"
	@echo "  update-mirrors  Update with the latest list of mirror servers"

lint: shellcheck

shellcheck:
	@shellcheck ./bin/* ./download/bin/*

update-mirrors:
	@echo "Updating list of mirrors in ${MIRROR_SERVERS} ..."
	@bin/get-mirrors > "${MIRROR_SERVERS}"

