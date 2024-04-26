#!/usr/bin/env bash

set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
collection_dir=$(dirname -- "${script_dir}")

ansible-galaxy collection build \
    --output-path "${collection_dir}/dist" \
    --force \
    "${collection_dir}"
