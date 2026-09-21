#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
bash ./start.sh
status=$?
if [ "$status" -ne 0 ]; then
    echo
    read -n 1 -s -r -p "STP exited with an error. Press any key to close this window..."
    echo
fi
exit "$status"
