#!/usr/bin/env bash
# DONE-WHEN probe for row tdump-driver-r12-cas-mark-sigsegv (hq_C s271).
# Replaces the row's original PROSE DONE-WHEN, which (a) was not a command and exited 2, and
# (b) named corpus/programs/snobol4/beauty_suite -- a path DELETED by 94dd91ba's corpus flatten.
# ⛔ It asserts the SHAPE of the failure it guards, not merely a polarity: the historical symptom
# was rc=139 (SIGSEGV), so a bare "did it match the ref" check would also pass on an empty file
# or a compile failure. Both are distinguished and reported separately.
# Negative-tested s271 against a build at 822bc8a1: exits 1 and names TDUMP-M3 rc=139.
# override the binary under test:  SCRIP_BIN=/path/to/scrip bash check_tdump_and_364.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
SCRIP_BIN="${SCRIP_BIN:-$ROOT/SCRIP/scrip}"
BS="$ROOT/corpus/snobol4/beauty_suite"
rc=0
[ -x "$SCRIP_BIN" ] || { echo "⛔ no scrip binary at $SCRIP_BIN"; exit 2; }
[ -d "$BS" ] || { echo "⛔ beauty_suite not found at $BS (corpus layout changed again?)"; exit 2; }
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
# --- 1. TDump_driver, mode 3 -----------------------------------------------------------------
( cd "$BS" && timeout 60s "$SCRIP_BIN" TDump_driver.sno < /dev/null > "$tmp/m3.out" 2>&1 ); m3rc=$?
if [ "$m3rc" -ne 0 ]; then echo "⛔ TDUMP-M3 rc=$m3rc$([ "$m3rc" = 139 ] && echo '  (SIGSEGV -- the historical r12=0 symptom)')"; rc=1
elif ! diff -q "$tmp/m3.out" "$BS/TDump_driver.ref" > /dev/null; then echo "⛔ TDUMP-M3 rc=0 but output differs from TDump_driver.ref"; rc=1
else echo "✅ TDUMP-M3 rc=0, byte-equal to ref"; fi
# --- 2. TDump_driver, mode 4 (m3 == m4 is a design invariant) ---------------------------------
( cd "$BS" && timeout 120s "$SCRIP_BIN" --compile -o "$tmp/td.s" TDump_driver.sno < /dev/null > /dev/null 2>&1 ) \
  && gcc -m64 -no-pie "$tmp/td.s" -o "$tmp/td.bin" -L"$ROOT/SCRIP/out" -lscrip_rt -Wl,-rpath,"$ROOT/SCRIP/out" -lm -lpthread > /dev/null 2>&1
if [ -x "$tmp/td.bin" ]; then
  ( cd "$BS" && timeout 60s "$tmp/td.bin" < /dev/null > "$tmp/m4.out" 2>&1 ); m4rc=$?
  if [ "$m4rc" -ne 0 ]; then echo "⛔ TDUMP-M4 rc=$m4rc$([ "$m4rc" = 139 ] && echo '  (SIGSEGV)')"; rc=1
  elif ! diff -q "$tmp/m4.out" "$BS/TDump_driver.ref" > /dev/null; then echo "⛔ TDUMP-M4 rc=0 but output differs from ref"; rc=1
  else echo "✅ TDUMP-M4 rc=0, byte-equal to ref"; fi
else echo "⛔ TDUMP-M4 failed to compile/link"; rc=1; fi
# --- 3. the whole SNOBOL4 corpus, both modes --------------------------------------------------
# ⛔ test_corpus_snobol4.sh takes its binary from $SCRIP (scripts/test_corpus_snobol4.sh:11), NOT $SCRIP_BIN.
# Caught during this probe's own negative test: section 3 printed 364/364 while sections 1-2 were
# SIGSEGVing, because the corpus runner silently measured the TREE's build instead of the binary under
# test. Threading it through is what makes the override honest -- a probe whose sections disagree about
# what they are measuring reports a green that belongs to a different program.
( cd "$ROOT/SCRIP" && SCRIP="$SCRIP_BIN" timeout 3000s bash scripts/test_corpus_snobol4.sh > "$tmp/corpus.log" 2>&1 )
m3line="$(grep -aE 'mode-3' "$tmp/corpus.log" | tail -1)"; m4line="$(grep -aE 'mode-4' "$tmp/corpus.log" | tail -1)"
echo "   $m3line"; echo "   $m4line"
# ⛔⛔ s272 hq_C — THE PINNED-DENOMINATOR DISEASE, CAUGHT BY CEO'S AUDIT AND FIXED HERE.
# This probe asserted 'PASS=364 FAIL=0' and so went RED at HEAD for a reason that has nothing to do with
# what it exists to watch: TDump_driver is GREEN in both modes, but the corpus's legitimate denominator
# moved 364 -> 362 and the probe was still demanding the old one. A probe that pins a TOTAL reports a
# regression every time the corpus legitimately changes size, and that is the false-RED twin of the
# false-GREEN we spend all day hunting -- both are the instrument lying about the program.
# ⭐ THE RULE, and it now binds every probe in this tree: ASSERT FAIL=0 AND SKIP=0 AND THE NAMED WITNESS.
# NEVER ASSERT A DENOMINATOR. The witness is what the row is about; the total is bookkeeping that
# belongs to whoever owns the corpus, not to this probe.
for _m in 3 4; do
    eval "_line=\"\$m${_m}line\""
    [ -n "$_line" ] || { echo "⛔ CORPUS-M$_m: no mode-$_m summary line in the runner output -- refusing to grade"; rc=1; continue; }
    printf '%s' "$_line" | grep -qE 'FAIL=0( |$)'  || { echo "⛔ CORPUS-M$_m has FAILures: $_line"; rc=1; }
    printf '%s' "$_line" | grep -qE 'SKIP=[1-9]'   && { echo "⛔ CORPUS-M$_m has SKIPs (a skip is not a pass): $_line"; rc=1; }
    printf '%s' "$_line" | grep -qE 'PASS=[1-9]'   || { echo "⛔ CORPUS-M$_m PASS=0 -- an empty corpus is not a green board: $_line"; rc=1; }
done
[ "$rc" = 0 ] && echo "✅ DONE-WHEN MET — TDump_driver clean in both modes AND corpus FAIL=0/SKIP=0 both modes (denominator deliberately NOT asserted)" \
              || echo "⛔ DONE-WHEN NOT MET"
exit "$rc"
