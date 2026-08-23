#!/usr/bin/env bash
# check_m1_fixedpoint.sh — THE MILESTONE-1 DONE-WHEN, as one command that can say NO.
# Self-host beauty in BOTH media and require each output to be byte-identical to its own input.
# The oracle is the file itself (Lon s117): beauty self-host is a FIXED POINT, so exp = md5(SRC).
#
# ⛔ CWD MUST BE THE BEAUTY DIRECTORY. beauty.sno pulls 16 -INCLUDE files that resolve relative to
# the working directory. Run it anywhere else and every arm emits ZERO bytes with "cannot open
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
BEAUTY="${M1_BEAUTY_DIR:-$ROOT/corpus/programs/snobol4/demo/beauty}"
ARM="${1:-both}"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
[ -x "$SCRIP" ]  || { echo "⛔ no scrip binary at $SCRIP — build first (make -C $ROOT/SCRIP)"; exit 2; }
[ -f "$SRC" ]    || { echo "⛔ pinned source missing: $SRC"; exit 2; }
[ -d "$BEAUTY" ] || { echo "⛔ beauty dir missing: $BEAUTY (the 16 .inc files live there)"; exit 2; }
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
