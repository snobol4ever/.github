#!/usr/bin/env bash
# bisect_probe_m1.sh — the RUNG C-0 bisect probe for the Milestone-1 mode-3 self-host regression.
#
# ⭐ PROVENANCE: authored by seat01 (2026-08-22) as bisect_probe_v2.sh, correcting an HQ-spec probe that
# would have CORRUPTED the bisect; RESCUED into version control by hq_C the same day because it existed
# only in seat01's /tmp scratchpad, which dies with the session. Made root-portable in the move (the
# original hardcoded /home/claude01 three times, so no other seat could run it).
#
# ⛔ WHY THE PINNED SOURCE EXISTS — THIS IS THE WHOLE POINT OF THE PROBE (LAW 0, species "EXPIRY"):
# the original probe read beauty.sno from the LIVE corpus checkout. That file was the CLASSIC text when
# the probe was written (~16:40), but corpus 53dd9ac0 (~17:21) promoted it to the &-constant grammar,
# which needs SCRIP pattern_match.c fix dac65d47 — a commit that POSTDATES EVERY COMMIT IN THIS BISECT
# RANGE. Pointed at the live file, every pre-dac65d47 commit reads BAD for a reason that has nothing to
# do with the regression, and the bisect converges confidently on the wrong commit. So SRC is PINNED to
# a frozen classic beauty.sno (40,971 bytes, md5 6f1671c0757729992ae01a6bdf16f081) extracted from
# corpus 53dd9ac0^. Measured 2026-08-22: live corpus beauty.sno is 41,492 bytes, md5 006850eb... — i.e.
# ALREADY DIVERGED. Do not "helpfully" repoint SRC at the corpus.
#
# THE ORACLE IS THE FILE ITSELF (Lon s117): beauty self-host is a FIXED POINT — output must be
# byte-identical to the input. That is why exp is md5(SRC) and not a pinned constant.
#
# usage:  git bisect start <BAD> <GOOD> && git bisect run /path/to/bisect_probe_m1.sh
#   known bounds, both MEASURED: GOOD=1f6cea4d (seat01, pristine, reproduces the fixed point)
#                                BAD =457dc5d9 (main HEAD 2026-08-22) ... BAD=ef553d3a (seat01)
#   seat04 bisected independently to 62017f8a (descr-stamp-fields), inside seat01's GOOD..BAD range.
#
# exit 0 = fixed point (GOOD) · exit 1 = not the fixed point (BAD) · exit 125 = build failed (SKIP)
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIP_DIR="${SCRIP_DIR:-$(cd "$HERE/../../../SCRIP" 2>/dev/null && pwd)}"     # sibling-root (D-17 PORTABLE-HOME)
SRC="${M1_SRC:-$HERE/beauty_classic_fixedpoint.sno}"
LOGDIR="${M1_LOGDIR:-${TMPDIR:-/tmp}/m1_bisect_logs}"
[ -d "$SCRIP_DIR" ] || { echo "⛔ no SCRIP tree at $SCRIP_DIR — set SCRIP_DIR=" >&2; exit 125; }
[ -f "$SRC" ]       || { echo "⛔ pinned source missing: $SRC" >&2; exit 125; }
mkdir -p "$LOGDIR"; cd "$SCRIP_DIR" || exit 125
SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
make pristine > "$LOGDIR/pristine.$SHA.log" 2>&1
[ -x ./scrip ] || { echo "[$SHA] BUILD FAIL — see $LOGDIR/pristine.$SHA.log"; exit 125; }
# ⛔ MUST RUN FROM THE DIRECTORY HOLDING THE .inc SET. The source pulls 17 -INCLUDE files via CWD;
# run it anywhere else and EVERY commit emits 0 bytes ("cannot open include 'global.inc'") and reads BAD,
# so the bisect converges confidently on nothing. This is the SECOND door onto the same defect seat01
# caught in the first probe — measured by hq_C 2026-08-22, after the rescue, on this very file.
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
BEAUTY="${M1_BEAUTY_DIR:-$(m1_find_include_dir "$(cd "$HERE/../../.." && pwd)" || true)}"
[ -n "$BEAUTY" ] && [ -f "$BEAUTY/global.inc" ] || { echo "⛔ .inc set not found (looked for global.inc under corpus/); set M1_BEAUTY_DIR=" >&2; exit 125; }
OUT="$LOGDIR/out.$SHA"
( cd "$BEAUTY" && timeout 60 "$SCRIP_DIR/scrip" "$SRC" < "$SRC" ) > "$OUT" 2> "$LOGDIR/stderr.$SHA"; rc=$?
got="$(md5sum "$OUT" | awk '{print $1}')"; exp="$(md5sum "$SRC" | awk '{print $1}')"
if [ "$rc" -eq 0 ] && [ "$got" = "$exp" ]; then echo "[$SHA] FIXED POINT (rc=$rc, md5=$got) — GOOD"; exit 0; fi
sz="$(wc -c < "$OUT" 2>/dev/null || echo 0)"
[ "$sz" = "0" ] && echo "[$SHA] ⛔ ZERO BYTES — instrument failure (include path?), NOT the regression. Refusing to vote." >&2 && exit 125
echo "[$SHA] NOT the fixed point (rc=$rc, md5=$got, bytes=$sz, expected md5=$exp) — BAD"; exit 1
