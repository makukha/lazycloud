SHELL = /usr/bin/env sh -eu
PODMAN = $(shell command -v podman || command -v docker)

FORCE:

.PHONY: help
# List available commands.
help:
	@sed -n '/^\.PHONY: / {N;s/.*: \(\S\+\)\( # \(.*\)\)\?\n# \(.*\)/\1 \3:\4/p}' Makefile | column -ts:


# Manage


.PHONY: init
# Initialize development environment.
init:
	@command -v gh || echo 'Command "gh" not found, see https://cli.github.com'
	@command -v git || echo 'Command "git" not found, see https://git-scm.com'
	@command -v lefthook || echo 'Command "lefthook" not found, see https://lefthook.dev'
	@command -v uv || echo 'Command "uv" not found, see https://docs.astral.sh/uv'
	@command -v yq || echo 'Command "yq" not found, see https://github.com/mikefarah/yq'
	lefthook install
	uv sync
	make -B sync

.PHONY: sync
# Synchronize development environment.
sync: .venv
.venv uv.lock &: pyproject.toml
	uv sync --all-extras --all-groups --all-packages

.PHONY: news
# Add changelog news entry.
news:
	uv run scriv create

.PHONY: changelog
# Collect changelog entries.
changelog:
	uv run scriv collect
	sed -e's/^### \(.*\)$$/***\1***/' -i'' CHANGELOG.md

.PHONY: pre-commit
# Run pre-commit hook.
pre-commit:
	lefthook run pre-commit --all-files

.PHONY: update-dependencies
# Update project dependencies.
update-dependencies:
	uv sync --all-extras --all-groups --all-packages --upgrade
	make build

.PHONY: update-template
# Update project template.
update-template:
	uvx copier update --trust --vcs-ref main
	# todo: add interactive step to merge
	make build

.PHONY: version-bump
# Bump project version.
version-bump:
	@uv run bump-my-version show-bump
	@printf 'Choose version component: '; read V; printf $$V > .tmp/.bump
	uv run bump-my-version bump --tag `cat .tmp/.bump`
	@rm .tmp/.bump
	uv lock

# TODO: Manage

## publish package on PyPI
#[private]
#pypi-publish:
#    make package
#    uv publish dist/pkg/* --token=$(bw get item __token__+makukha@pypi.org | yq .notes)
#
## run pre-merge
#[group('2-manage')]
#pre-merge:
#    just lint
#    just test
#    make docs sources
#
## merge
#[group('2-manage')]
#merge:
#    just pre-merge
#    @echo "Manually>>> Merge pull request ..."
#    just gh::pr-create
#    @printf "Done? " && read _
#    git switch main
#    git fetch
#    git pull
#
## release
#[group('2-manage')]
#release:
#    just version-bump
#    just pre-merge
#    just changelog-collect
#    make sources
#    @echo "Manually>>> Proofread the changelog and commit changes ..."
#    @printf "Done? " && read _
#    git tag "v$(uv run bump-my-version show current_version)"
#    git push --tags
#    just merge
#    just gh::repo-update
#    @echo "Manually>>> Update GitHub release notes and publish release ..."
#    just gh::release-create "v$(uv run bump-my-version show current_version)"
#    @printf "Done? " && read _
#    just pypi-publish


# Develop


.PHONY: lint
# Run project linters.
lint:
	lefthook run pre-commit --jobs lint --all-files

.PHONY: build
# Build project.
build: badges docs package requirements

.PHONY: package
# Build package.
package: .tmp/dist
.tmp/dist: src/**/* README.md pyproject.toml uv.lock .venv
	rm -rf $@
	uv build -o .tmp/dist

.PHONY: docs
# Build documentation.
docs: README.md
README.md: docs/*.md
%.md: FORCE
	uv run docsub sync -i $@

.PHONY: badges
# Build project badges.
badges: docs/img/badge/coverage.svg docs/img/badge/tests.svg
docs/img/badge/%.svg: .tmp/%.xml
	mkdir -p $(@D)
	uv run genbadge $* --local -i $< -o $@

.PHONY: requirements
# Export testing requirements.
requirements: tests/requirements.txt
tests/requirements.txt: pyproject.toml uv.lock
	uv export --frozen --no-emit-project --no-hashes --only-group testing > $@

.PHONY: test # [ TOXARGS="..." ]
# Run tests, optionally pass extra args to tox.
test: package requirements
	mkdir -p .tox
ifdef TOXARGS
	${PODMAN} compose run --rm tox run --installpkg="`find .tmp/dist -name '*.whl'`" ${TOXARGS}
else
	${PODMAN} compose run --rm tox run --notest --skip-pkg-install
	${PODMAN} compose run --rm tox run-parallel --installpkg="`find .tmp/dist -name '*.whl'`"
endif

.PHONY: shell # [ SERVICE=tox ]
# Enter service container, tox by default
shell:
	${PODMAN} compose run --rm --entrypoint bash $(or ${SERVICE},tox)

.PHONY: clean
# Clean up intermediate files.
clean:
	rm -rf .coverage .tmp .tox .venv
	find . -name __pycache__ -exec rm -rf {} \;


# TODO: GitHub helpers


## push all commits after ensuring the clean state
#[no-cd]
#push:
#    git diff --exit-code
#    git diff --cached --exit-code
#    git ls-files --other --exclude-standard --directory
#    git push

## get issue id of current GitHub branch
#[no-cd]
#issue-id:
#    @git branch --show-current | cut -d- -f1
#
## get issue title of current GitHub branch
#[no-cd]
#issue-title:
#    @GH_PAGER=cat gh issue view "$(just gh::issue-id)" --json title -t '\{\{\{\{.title}}'
#
## create GitHub pull request
#[no-cd]
#pr-create:
#    #!/usr/bin/env sh
#    set -eu
#    just git::push
#    TITLE=
#    gh pr create --web -t "$(just gh::issue-title)"
#
## create GitHub release
#[no-cd]
#release-create tag:
#    #!/usr/bin/env sh
#    set -eu
#    if [ "$(git branch --show-current)" != "main" ]; then
#        echo "Can release from main branch only"
#        exit 1
#    fi
#    git push origin tag "\{\{tag}}"
#    gh release create --draft -t "\{\{tag}} — $(date -Idate)" --generate-notes "\{\{tag}}"
#
## get "org/name" of current GitHub repository
#[no-cd]
#repo-name:
#    @git config --get remote.origin.url | sed 's|.*/\(.*/.*\)\.git$|\1|'

.PHONY: github-repo-update
github-repo-update:
	export DESCRIPTION=`yq .project.description pyproject.toml` && \
	  gh repo edit -d "$$DESCRIPTION"
	export HOMEPAGE=`yq .project.urls.Documentation pyproject.toml | sed '/^https:\/\/github.com/d'` && \
	  gh repo edit -h "$$HOMEPAGE" || true
	export REPO=`git config --get remote.origin.url | sed 's|.*/\(.*/.*\)\.git$$|\1|'` && \
	export OLD_TOPICS=`GH_PAGER=cat gh api repos/$$REPO | yq -r '.topics | join(" ")'` && \
	  [ -n "$$OLD_TOPICS" ] && \
	  gh repo edit `echo " $$OLD_TOPICS" | sed 's/ / --remove-topic /g'` || true
	export NEW_TOPICS=`yq -r '.project.keywords | join(" ")' pyproject.toml` && \
	  gh repo edit `echo " $$NEW_TOPICS" | sed 's/ / --add-topic /g'`
	gh label create "code of conduct" --force -c D73A4A -d "Code of Conduct issues"
