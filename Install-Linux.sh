#!/bin/bash
set -euo pipefail
if [ "$#" -lt 1 ]; then echo 'Usage: bash Install-Linux.sh /authorized/workspace/brand [--source-commit SHA]'; exit 2; fi
package="$(cd "$(dirname "$0")" && pwd -P)"
command -v python3 >/dev/null 2>&1 || { echo 'Python 3.10+ is required for Linux/cloud workspace initialization.'; exit 2; }
exec python3 -B "$package/tools/cloud_workspace.py" init "$@"
