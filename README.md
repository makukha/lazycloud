# lazycloud
<!-- docsub: begin -->
<!-- docsub: exec yq '"> " + .project.description' pyproject.toml -->
> Cloud operations helper with easy terminal interface
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: include docs/badges.md -->
[![license](https://img.shields.io/github/license/makukha/lazycloud.svg)](https://github.com/makukha/lazycloud/blob/main/LICENSE)
[![pypi](https://img.shields.io/pypi/v/lazycloud.svg#v0.0.0)](https://pypi.org/project/lazycloud)
[![python versions](https://img.shields.io/pypi/pyversions/lazycloud.svg)](https://pypi.org/project/lazycloud)
[![tests](https://raw.githubusercontent.com/makukha/lazycloud/v0.0.0/docs/img/badge/tests.svg)](https://github.com/makukha/lazycloud)
[![coverage](https://raw.githubusercontent.com/makukha/lazycloud/v0.0.0/docs/img/badge/coverage.svg)](https://github.com/makukha/lazycloud)
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)
[![uses docsub](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/makukha/docsub/refs/heads/main/docs/badge/v1.json)](https://github.com/makukha/docsub)
[![mypy](https://img.shields.io/badge/type_checked-mypy-%231674b1)](http://mypy.readthedocs.io)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/ruff)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![openssf best practices](https://www.bestpractices.dev/projects/11073/badge)](https://www.bestpractices.dev/projects/)
<!-- docsub: end -->


# Features

<!-- docsub: begin -->
<!-- docsub: include docs/features.md -->
- Simple terminal-based user interface with prompts and defaults
- Cloud providers supported: AWS
<!-- docsub: end -->

## Supported Operations

- `aws`
  - `tag`
    - `--iam-roles`
    - `--iam-users`


# Installation

```shell
$ uv tool install lazycloud
```


# Usage

<!-- docsub: begin #usage.md -->
<!-- docsub: include docs/usage.md -->
<!-- docsub: end #usage.md -->


# CLI Reference

<!-- docsub: begin #cli.md -->
<!-- docsub: include docs/cli.md -->
<!-- docsub: end #cli.md -->


# Contributing

Pull requests, feature requests, and bug reports are welcome!

* [Contribution guidelines](https://github.com/makukha/lazycloud/blob/main/.github/CONTRIBUTING.md)


# Authors

* Michael Makukha


# See also

* [Documentation](https://github.com/makukha/lazycloud#readme)
* [Issues](https://github.com/makukha/lazycloud/issues)
* [Changelog](https://github.com/makukha/lazycloud/blob/main/CHANGELOG.md)
* [Security Policy](https://github.com/makukha/lazycloud/blob/main/.github/SECURITY.md)
* [Contribution Guidelines](https://github.com/makukha/lazycloud/blob/main/.github/CONTRIBUTING.md)
* [Code of Conduct](https://github.com/makukha/lazycloud/blob/main/.github/CODE_OF_CONDUCT.md)
* [License](https://github.com/makukha/lazycloud/blob/main/LICENSE)
