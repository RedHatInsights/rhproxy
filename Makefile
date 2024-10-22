
EPEL_SERVERS="env/epel.servers"

all:	help

help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  help                 show this help message"
	@echo "  lint                 run all linters for the rhproxy installer"
	@echo "  check-epel-servers   Check that list of EPEL servers is the latest"
	@echo "  update-epel-servers  Update with the latest list of EPEL servers"

lint: shellcheck

shellcheck:
	@shellcheck ./bin/rhproxy* ./download/bin/*

check-epel-servers:
	@echo "Checking that the list of EPEL servers is the latest ..."
	@CURRENT_EPEL_SERVERS=$$(mktemp); LATEST_EPEL_SERVERS=$$(mktemp); \
	 cat ${EPEL_SERVERS} | sed '/^#/d' > "$${CURRENT_EPEL_SERVERS}"; \
	 bin/get-epel-servers | sed '/^#/d' > "$${LATEST_EPEL_SERVERS}"; \
	 diff "$${CURRENT_EPEL_SERVERS}" "$${LATEST_EPEL_SERVERS}"; \
	 /usr/bin/cmp "$${CURRENT_EPEL_SERVERS}" "$${LATEST_EPEL_SERVERS}" >/dev/null; \
	 if [ $$? -eq 0 ]; then \
	   echo "::notice ::EPEL servers list is up to date"; EC=0; \
	 else \
	   echo "::warning ::EPEL servers list needs to be updated"; EC=1; \
	 fi; \
	 rm -f "$${CURRENT_EPEL_SERVERS}" "$${LATEST_EPEL_SERVERS}"; \
	 exit $${EC}

update-epel-servers:
	@echo "Updating list of EPEL servers in ${EPEL_SERVERS} ..."
	@bin/get-epel-servers > "${EPEL_SERVERS}"

