#!/usr/bin/env bash
# Put the Skyworth SRT412 back the way it was before the cleanup: re-enable every package the debloat
# list turned off, give Home back to the stock Android TV launcher, and remove the theme. The CleanYourTV
# launcher, Nuvio and the weather add-on stay installed; uninstall them from Settings > Apps if you want
# them gone.
#
# Needs network debugging on (Settings > Device Preferences > Developer options > USB debugging).
# Usage: TV_HOST=<tv ip> setups/skyworth-srt412/restore.sh
set -euo pipefail
: "${TV_HOST:?set TV_HOST to the box's IP address}"
export TV_HOST
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
cd "$REPO"
if [ ! -x tools/venv/bin/python ]; then
  python3 -m venv tools/venv && tools/venv/bin/pip install -q -r tools/requirements.txt
fi
# Re-enables the list and the stock launcher, from the record disable.sh wrote.
tools/restore.sh "$HERE/debloat.txt" com.google.android.tvlauncher
tools/theme.sh --reset || true
echo "Restored. Press Home on the remote."
