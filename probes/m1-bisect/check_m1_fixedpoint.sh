#!/usr/bin/env bash
# check_m1_fixedpoint.sh — THE MILESTONE-1 DONE-WHEN, as one command that can say NO.
# Self-host beauty in BOTH media and require each output to be byte-identical to its own input.
# The oracle is the file itself (Lon s117): beauty self-host is a FIXED POINT, so exp = md5(SRC).
#
# ⛔ CWD MUST BE THE DIRECTORY HOLDING THE .inc SET. The pinned source pulls 17 -INCLUDE files
# that resolve relative to the working directory. Run it anywhere else and every arm emits ZERO bytes with "cannot open
# include 'global.inc'" — a failure that has NOTHING to do with the code under test. That exact
# mistake is baked into the rescued bisect probe's history: seat01 smoke-tested its corrected probe,
# got rc=1 with EMPTY output, and read it as "BAD as expected" — but the real regression symptom is
# 278 bytes with a Parse Error, not 0 bytes. A git-bisect run over that probe marks EVERY commit BAD
# and converges, confidently, on nothing. This script cds for you so that cannot recur.
#
# usage: bash check_m1_fixedpoint.sh [m3|m4|both]      exit 0 = fixed point in every arm requested
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${S4E_HOME:-$(cd "$HERE/../../.." && pwd)}"
SCRIP="${SCRIP_BIN:-$ROOT/SCRIP/scrip}"
RT="${SCRIP_RT:-$ROOT/SCRIP/out}"
SRC="${M1_SRC:-$HERE/beauty_classic_fixedpoint.sno}"
# ⛔ THE INCLUDE DIRECTORY IS DISCOVERED BY THE FILE IT MUST CONTAIN, NEVER BY A HARDCODED PATH.
# The pinned classic source lives under .github/, whose ancestors have no include/ dir, so the driver's
# ancestor-walk (src/driver/scrip.c:938-951, which registers any <ancestor>/include) finds nothing and the
# ONLY resolver left is "." - CWD. So this script must cd somewhere that actually holds the .inc set.
# ⭐ 2026-08-27 hq_C: the previous hardcoded path (corpus/programs/snobol4/demo/beauty) died in the
# 2026-08-24 corpus re-grid and the .inc files moved to corpus/include/. The probe refused honestly
# (rc=2, never a false green) but Milestone 1's stated DONE-WHEN could not say YES on ANY tree for days.
# ⛔ Testing [ -d "$dir" ] is what let a MOVED FILE SET stay invisible: the container can exist while
# the contents re-nest. Probe for global.inc itself.
m1_find_include_dir() {
  local r="$1" c
  for c in "$r/corpus/include" "$r/corpus/probe/fwctx"; do
    [ -f "$c/global.inc" ] && { printf '%s\n' "$c"; return 0; }
  done
  c="$(find "$r/corpus" -name global.inc -printf '%h\n' 2>/dev/null | head -1)"
  [ -n "$c" ] && [ -f "$c/global.inc" ] && { printf '%s\n' "$c"; return 0; }
  return 1
}
BEAUTY="${M1_BEAUTY_DIR:-$(m1_find_include_dir "$ROOT" || true)}"
ARM="${1:-both}"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
[ -x "$SCRIP" ]  || { echo "⛔ no scrip binary at $SCRIP — build first (make -C $ROOT/SCRIP)"; exit 2; }
[ -f "$SRC" ]    || { echo "⛔ pinned source missing: $SRC"; exit 2; }
[ -n "$BEAUTY" ] && [ -f "$BEAUTY/global.inc" ] || { echo "⛔ GATE UNPROVEN(2): no directory holding the .inc set found under $ROOT/corpus (looked for global.inc; set M1_BEAUTY_DIR=). Got: [${BEAUTY:-none}]"; exit 2; }
case "$ARM" in m3|m4|both) ;; *) echo "⛔ GATE UNPROVEN(2): unrecognized ARM '$ARM' — expected m3, m4, or both"; exit 2;; esac
exp="$(md5sum "$SRC" | awk '{print $1}')"; bytes_exp="$(wc -c < "$SRC")"; rc=0
report() { # $1=arm $2=outfile
  local got sz; got="$(md5sum "$2" 2>/dev/null | awk '{print $1}')"; sz="$(wc -c < "$2" 2>/dev/null || echo 0)"
  if [ "$got" = "$exp" ]; then printf '  %-3s FIXED POINT  %s bytes  md5 %s\n' "$1" "$sz" "$got"
  else printf '  %-3s ⛔ NOT THE FIXED POINT  %s bytes (expected %s)  md5 %s (expected %s)\n' "$1" "$sz" "$bytes_exp" "${got:-none}" "$exp"
       [ "$sz" = "0" ] && printf '      ⛔ ZERO BYTES — almost certainly the -INCLUDE path, not the compiler. Check CWD.\n'
       [ "$sz" = "278" ] && printf '      ⭐ 278 bytes is the KNOWN C-0 SIGNATURE (Parse Error on START), cured in cd13321e..457dc5d9.\n'
       rc=1; fi; }
case "$ARM" in m3|both)
  ( cd "$BEAUTY" && timeout 120 "$SCRIP" "$SRC" < "$SRC" > "$T/m3.out" 2>"$T/m3.err" ); report m3 "$T/m3.out";; esac
case "$ARM" in m4|both)
  ( cd "$BEAUTY" && timeout 180 "$SCRIP" --compile -o "$T/m4.s" "$SRC" > "$T/m4c.log" 2>&1 )
  if [ -s "$T/m4.s" ] && gcc -o "$T/m4.bin" "$T/m4.s" -L"$RT" -lscrip_rt -Wl,-rpath,"$RT" 2>"$T/m4l.log"; then
    ( cd "$BEAUTY" && timeout 120 "$T/m4.bin" < "$SRC" > "$T/m4.out" 2>"$T/m4.err" ); report m4 "$T/m4.out"
  else printf '  m4  ⛔ COMPILE/LINK FAILED (see log)\n'; tail -2 "$T/m4c.log" "$T/m4l.log" 2>/dev/null; rc=1; fi;; esac
[ "$rc" = 0 ] && echo "  M1 FIXED POINT HOLDS ($ARM)" || echo "  ⛔ M1 FIXED POINT BROKEN ($ARM)"
exit $rc
