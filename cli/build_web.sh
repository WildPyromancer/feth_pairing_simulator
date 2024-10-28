#!/usr/bin/env sh

set -o errexit
set -o noclobber
set -o nounset
# set -o xtrace

script_dir="$(dirname "${0}")"

cd "$(readlink -f "$script_dir/../")"
flet build web --module-name ./pairing_simulator.py \
	--exclude '
	.git,
	.gitignore,
	.ruff_cache,
	.venv,
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

path_of_web_dir=./build/web
path_of_app_zip="$path_of_web_dir/assets/app/app.zip"
# CloudFlare Pages の1ファイル辺りのサイズ上限が25mb。
echo "===== 24MB over files list ====="
files_that_25mb_over="$(find "$path_of_web_dir" -size +24M)"
echo "$files_that_25mb_over" | while read -r LINE; do
	echo "$LINE"
	if [ "$LINE" = $path_of_app_zip ]; then
		zipinfo -l "$path_of_app_zip" |
			sed '$d' |
			awk 'NR>1{print $6,$10}' |
			sort --numeric-sort --reverse |
			head --lines=20 |
			awk '{printf "%10s | %s\n", $1, $2}'
	fi
done

test "$files_that_25mb_over" = ''
