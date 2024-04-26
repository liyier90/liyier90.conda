#!/usr/bin/env bash

set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
tmp_dir=${TMPDIR:-/tmp}
ansible_collections_dir="${tmp_dir}/ansible_collections"
collection_dir="${tmp_dir}/ansible_collections/liyier90/conda"

[[ -d ${ansible_collections_dir} ]] && rm -rf "${ansible_collections_dir}"

mkdir -p "${collection_dir}"
cp -r "$(dirname -- "${script_dir}")/"* "${collection_dir}"

cd "${collection_dir}"
ansible-test sanity
ansible-test integration --docker ubuntu2204
