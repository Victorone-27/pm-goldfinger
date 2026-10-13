#!/bin/bash
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${PM_GOLDFINGER_PYTHON:-python3}" "$script_dir/manage_skills.py" "$@"
