
MIRROR_SERVERS="env/mirror.servers"

all:	help

help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  help            show this help message"
	@echo "  lint            run all linters for the rhproxy installer"
	@echo "  check-mirrors   Check that list of mirror servers is the latest"
	@echo "  update-mirrors  Update with the latest list of mirror servers"

lint: shellcheck

shellcheck:
	@shellcheck ./bin/* ./download/bin/*

check-mirrors:
	@echo "Checking the list of mirror servers is the latest ..."
	@CURRENT_MIRRORS=$$(mktemp); LATEST_MIRRORS=$$(mktemp); \
	 cat ${MIRROR_SERVERS} | sed '/^#/d' > "$${CURRENT_MIRRORS}";  \
	 bin/get-mirrors | sed '/^#/d' > "$${LATEST_MIRRORS}"; \
	 diff "$${CURRENT_MIRRORS}" "$${LATEST_MIRRORS}"; \
	 /usr/bin/cmp "$${CURRENT_MIRRORS}" "$${LATEST_MIRRORS}" >/dev/null; \
	 if [ $$? -eq 0 ]; then \
	   echo "Mirror servers list is up to date"; EC=0; \
	 else \
	   echo "Mirror servers list needs to be updated"; EC=1; \
	 fi; \
	 rm -f "$${CURRENT_MIRRORS}" "$${LATEST_MIRRORS}"; \
	 exit $${EC}

update-mirrors:
	@echo "Updating list of mirrors in ${MIRROR_SERVERS} ..."
	@bin/get-mirrors > "${MIRROR_SERVERS}"

