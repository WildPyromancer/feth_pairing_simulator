#!/usr/bin/env sh

set -o errexit
set -o noclobber
set -o nounset
set -o xtrace

flet build web --module-name ./pairing_simulator.py \
	--exclude '
	.git,
	.gitignore,
	.ruff_cache,
	.venv
	.vscode,
	auto_py_to_exe_config.json,
	cli,
	CONTRIBUTING.adoc,
	docs/fletのメモ.asciidoc,
	logs,
	modules/.ruff_cache,
	output,
	README.md,
	resource,
	tests,
'
