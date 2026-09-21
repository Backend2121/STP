#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
bash ./install.sh "$@"
status=$?
read -n 1 -s -r -p "Press any key to close this window..."
exit "$status"
