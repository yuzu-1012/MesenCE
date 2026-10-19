#!/usr/bin/env bash
# Build the current checkout without needing the GitHub tag.
# The checkout is exported to a temporary directory so the repository stays
# clean; the resulting AOT binary is copied to packaging/arch/build-output/.
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
out_dir="$root/packaging/arch/build-output"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

git -C "$root" archive HEAD | tar -x -C "$tmp_dir"
cd "$tmp_dir"

export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_NOLOGO=1
export DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1
export DOTNET_CLI_HOME="$tmp_dir/.dotnet"
export NUGET_PACKAGES="$tmp_dir/.nuget"
export NUGET_HTTP_CACHE_PATH="$tmp_dir/.nuget-http-cache"

make USE_AOT=true LTO=true STATICLINK=false SYSTEM_LIBEVDEV=true

install -Dm755 "bin/linux-x64/Release/linux-x64/publish/Mesen" \
  "$out_dir/mesen-ce-zh"

echo "Built: $out_dir/mesen-ce-zh"
