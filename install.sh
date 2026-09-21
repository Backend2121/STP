#!/usr/bin/env bash
set -u

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

echo "STP is installing..."

UNATTENDED=0
[ "${1:-}" = "--unattended" ] && UNATTENDED=1

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

is_ok_python() {
    "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1
}

find_python() {
    local c
    for c in python3.13 python3.12 python3.11 python3.10 python3 python "$@"; do
        if command -v "$c" >/dev/null 2>&1 && is_ok_python "$c"; then
            command -v "$c"
            return 0
        fi
    done
    return 1
}

PY="$(find_python)" || PY=""

if [ -z "$PY" ]; then
    case "$(uname -s)" in
        Darwin)
            if command -v brew >/dev/null 2>&1; then
                brew install python@3.13 || fail "Homebrew could not install Python."
                BREW_BIN="$(brew --prefix)/bin"
                PY="$(find_python "$BREW_BIN/python3.13" "$BREW_BIN/python3")" || PY=""
                [ -n "$PY" ] || fail "Python was installed but could not be located. Open a new terminal and run this installer again."
            else
                open "https://www.python.org/downloads/" >/dev/null 2>&1
                fail "Install Python 3.10 or newer from https://www.python.org/downloads/ then run this installer again."
            fi
            ;;
        *)
            if command -v apt-get >/dev/null 2>&1; then
                hint="sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip"
            elif command -v dnf >/dev/null 2>&1; then
                hint="sudo dnf install -y python3 python3-pip"
            elif command -v pacman >/dev/null 2>&1; then
                hint="sudo pacman -S --needed python python-pip"
            elif command -v zypper >/dev/null 2>&1; then
                hint="sudo zypper install -y python3 python3-pip"
            else
                hint=""
            fi
            if [ -n "$hint" ]; then
                fail "Install Python 3.10 or newer, then run this installer again:
    $hint"
            fi
            fail "Install Python 3.10 or newer from https://www.python.org/downloads/ then run this installer again."
            ;;
    esac
fi

VENV_PY="venv/bin/python"
if [ -d venv ] && ! { [ -x "$VENV_PY" ] && is_ok_python "$VENV_PY"; }; then
    rm -rf venv
fi
if [ ! -d venv ]; then
    if ! "$PY" -m venv venv; then
        rm -rf venv
        fail "Could not create the virtual environment. On Debian/Ubuntu run:
    sudo apt-get install -y python3-venv
then run this installer again."
    fi
fi

"$VENV_PY" -m pip install --upgrade pip >/dev/null 2>&1 || true
"$VENV_PY" -m pip install -r requirements.txt || fail "Installing dependencies failed, check your internet connection and the messages above."

[ -f .env ] || { [ -f .env.example ] && cp .env.example .env; }

chmod +x install.sh install.command start.sh start.command 2>/dev/null || true

if [ "$UNATTENDED" -eq 0 ] && [ -t 0 ]; then
    read -r -p "Start STP now? [Y/n] " ans
    case "$ans" in
        [nN]*) ;;
        *) exec bash ./start.sh ;;
    esac
fi
