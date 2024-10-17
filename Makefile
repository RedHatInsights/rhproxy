
all:	help

help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  help      show this help message"
	@echo "  lint      run all linters for the rhproxy installer"

lint: shellcheck

shellcheck:
	@shellcheck ./bin/* ./download/bin/*

