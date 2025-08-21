SHELL = /usr/bin/env sh -eu

FORCE:

.PHONY: help
# list available commands
help:
	@sed -n 's/^\.PHONY: \(\S\+\)\( #\)\?/\1/p' Makefile


# Environment

.PHONY: init
# initialize development environment
init:
	@command -v gh || echo 'Command "gh" not found, see https://cli.github.com'
	@command -v git || echo 'Command "git" not found, see https://git-scm.com'
	@command -v uv || echo 'Command "uv" not found, see https://docs.astral.sh/uv/getting-started/installation'
	@command -v yq || echo 'Command "yq" not found, see https://github.com/mikefarah/yq'
	printf "#!/usr/bin/env sh\njust pre-commit" > .git/hooks/pre-commit
	chmod ug+x .git/hooks/*
	make sync

.PHONY: sync
# synchronize development environment
sync: .venv
.venv: pyproject.toml uv.lock
	uv lock --refresh
	uv sync --all-extras --all-groups --all-packages --frozen
uv.lock: pyproject.toml
	uv lock --refresh

.PHONY: upgrade
# upgrade development environment
upgrade:
	uv sync --all-extras --all-groups --upgrade
	uvx copier update --trust --vcs-ref main


# Development

.PHONY: news
# add changelog news entry
news:
	uv run scriv create

# requirements ======= (TO BE REMOVED) =======
.PHONY: requirements
requirements: tests/requirements.txt
tests/requirements.txt: pyproject.toml uv.lock
	uv export --frozen --no-emit-project --no-hashes --only-group testing > $@

.PHONY: package
package: dist/pkg
dist/pkg: src/**/* README.md pyproject.toml uv.lock .venv
	rm -rf $@
	uv build -o dist/pkg


# Docs

.PHONY: docs
docs: README.md
README.md: docs/*.md
%.md: FORCE
	uv run docsub sync -i $@


# Sources

.PHONY: sources
sources: badges requirements README.md

.PHONY: badges
badges: docs/img/badge/coverage.svg docs/img/badge/tests.svg
docs/img/badge/%.svg: .tmp/%.xml
	mkdir -p $(@D)
	uv run genbadge $* --local -i $< -o $@
