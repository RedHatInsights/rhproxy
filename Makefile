
MIRROR_SERVERS="env/mirror.servers"

help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  help              Show this help message"
	@echo "  update-mirrors    Update with the latest list of mirror servers"

update-mirrors:
	@echo "Updating list of mirrors in ${MIRROR_SERVERS} ..."
	@bin/get-mirrors > "${MIRROR_SERVERS}"

