#!/usr/bin/env bash
# Pokretač za Linux

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Greška: Python 3 nije instaliran ili nije dostupan u sustavu."
  read -r -p "Pritisnite Enter za zatvaranje..."
  exit 1
fi

if ! python3 -c "import customtkinter, cryptography" 2>/dev/null; then
  echo "Instaliram potrebne biblioteke..."
  if ! python3 -m pip install -r requirements.txt; then
    echo "Greška: instalacija potrebnih biblioteka nije uspjela."
    read -r -p "Pritisnite Enter za zatvaranje..."
    exit 1
  fi
fi

if ! python3 app.py; then
  echo
  echo "Aplikacija se nije uspjela pokrenuti. Poruka iznad objašnjava razlog."
  read -r -p "Pritisnite Enter za zatvaranje..."
  exit 1
fi
