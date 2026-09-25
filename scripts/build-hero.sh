#!/usr/bin/env bash
# Render assets/hero.svg.tmpl into light and dark variants.
set -euo pipefail
cd "$(dirname "$0")/.."

render() {
  out=$1; shift
  sed "$@" assets/hero.svg.tmpl > "$out"
}

render assets/hero-light.svg \
  -e 's/{{BG}}/#fbf8f3/g' -e 's/{{FG}}/#1c1a17/g' -e 's/{{MUTED}}/#6f675c/g' \
  -e 's/{{BORDER}}/#ebe4d8/g' -e 's/{{BORDER_STRONG}}/#cfc5b5/g' \
  -e 's/{{ACCENT}}/#d9622b/g' -e 's/{{MESA}}/#2b2621/g' -e 's/{{STARS}}/0/g'

render assets/hero-dark.svg \
  -e 's/{{BG}}/#0f0e0d/g' -e 's/{{FG}}/#f3eee6/g' -e 's/{{MUTED}}/#9c9387/g' \
  -e 's/{{BORDER}}/#2a2622/g' -e 's/{{BORDER_STRONG}}/#4a433b/g' \
  -e 's/{{ACCENT}}/#f08a4b/g' -e 's/{{MESA}}/#2f2a24/g' -e 's/{{STARS}}/.8/g'

echo "wrote assets/hero-light.svg assets/hero-dark.svg"
