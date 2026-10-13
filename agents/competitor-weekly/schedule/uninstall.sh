#!/bin/bash
set -euo pipefail
task_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
task_python="${PM_GOLDFINGER_PYTHON:-$task_dir/.venv/bin/python}"
if [[ ! -x "$task_python" ]]; then
  printf '请先恢复项目虚拟环境，或设置 PM_GOLDFINGER_PYTHON。\n' >&2
  exit 1
fi
exec "$task_python" "$task_dir/schedule/manage.py" uninstall "$@"
