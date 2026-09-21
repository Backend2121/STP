#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

if [ ! -x venv/bin/python ]; then
    echo "STP is not installed yet. Run ./install.sh first."
    exit 1
fi

exec venv/bin/python main.py
