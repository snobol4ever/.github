#!/usr/bin/env bash
# util_s_md5_sweep.sh — per-program mode-4 .s md5 sweep, for killswitch byte-identity and blast-radius gates.
#   bash scripts/util_s_md5_sweep.sh OUT.md5 [LISTFILE]
# LISTFILE = one .sno path per line; default list = corpus demo (maxdepth 1) + crosscheck + probe/bb.
# Compare arms/builds with:  diff A.md5 B.md5   (or join to list movers).  Landed s145 (HQ) — the gate that
# proved ARBNO-TAIL-BETA byte-identity (529/529) and the SEED-NAMES fix .s-invariance ran exactly this shape.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; SC="$(cd "$HERE/.." && pwd)"
SCRIP="${SCRIP:-$SC/scrip}"; CORPUS="${CORPUS:-/home/claude/corpus}"
OUT="${1:?usage: util_s_md5_sweep.sh OUT.md5 [LISTFILE]}"; LIST="${2:-}"
T="$(mktemp)"; trap 'rm -f "$T"' EXIT
if [ -n "$LIST" ]; then cp "$LIST" "$T"; else
  { find "$CORPUS/programs/snobol4/demo" -maxdepth 1 -name '*.sno'; find "$CORPUS/crosscheck" -name '*.sno'; find "$CORPUS/probe/bb" -name '*.sno'; } | sort > "$T"; fi
gen() { local d n W; d="$(dirname "$1")"; n="$(basename "$1" .sno)"; W=$(mktemp -d)
  (cd "$d" && SNO_LIB="$d" timeout 60 "$SCRIP" --compile "$1" </dev/null >"$W/p.s" 2>/dev/null)
  if [ -s "$W/p.s" ]; then printf '%s\t%s\n' "$(md5sum < "$W/p.s" | cut -d' ' -f1)" "$1"; else printf 'COMPILE_FAIL\t%s\n' "$1"; fi
  rm -rf "$W"; }
export -f gen; export SCRIP
xargs -a "$T" -P "$(nproc)" -I{} bash -c 'gen "$@"' _ {} | sort -k2 > "$OUT"
echo "$(wc -l < "$OUT") programs -> $OUT"
