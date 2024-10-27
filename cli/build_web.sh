#!/usr/bin/env sh

set -o errexit
set -o noclobber
set -o nounset
set -o xtrace

flet build web --module-name ./pairing_simulator.py \
	--exclude '
	.git,
	.gitignore,
	.vscode,
	auto_py_to_exe_config.json,
	cli,
	CONTRIBUTING.adoc,
	docs/fletのメモ.asciidoc,
	logs,
	modules/_pychache_,
	modules/.ruff_cache,
	README.md,
	resource,
	tests,
	.venv'
