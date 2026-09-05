#!/usr/bin/env bash
# land_oracle_swap_receipts.sh -- the two receipts still owed after the 2026-09-05 SPITBOL oracle swap.
#
# WHY THIS IS A SCRIPT AND NOT A SEAT DOING IT (hq_B, ceo CEO-282/284): every write under /home/resources is
# refused by the harness auto-mode classifier from the hq_B seat AND from the ceo seat -- that is why Lon ran
# fix_sbl_trace_dispatch.sh at 10:34:17 CDT on a one-line `! bash`. These two receipts need the same hand.
#
# THE SWAP ITSELF IS ALREADY DONE. This script does NOT touch the binary. It records what happened:
#   (1) commit + push the fork -- bin/sbl and sbl.min ONLY. The two bin/sbl.bak-* files stay OUT of history
#       (they are ~290KB binaries apiece and are recovery artifacts, not source); a .gitignore line is added
#       so they cannot be swept in by a later `git add -A`.
#   (2) ORACLES.md's top line names the new fork commit and the swap minute.
#
# ⛔ ORACLES.md IS EDITED BY INSERTION ONLY. hq_B never saw that file -- reads under /home/resources are
# refused from the seat too -- so this script will not rewrite content it cannot inspect. It PREPENDS one
# line, prints the first lines before and after so the operator can see exactly what changed, and keeps a
# .bak. If the shape is wrong, the .bak restores it in one move.
#
# Usage:  bash land_oracle_swap_receipts.sh [--dry-run]
# Exit:   0 done (or dry-run ok) · 1 something was already different · 2 REFUSE, cannot measure.
set -u
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
FORK=${FORK:-/home/resources/x64}
ORACLES=${ORACLES:-/home/resources/ORACLES.md}
STAMP_UTC=20260905T153417Z
STAMP_CDT="2026-09-05 10:34:17 CDT"
NEWMD5=bc694a0cc699f91d06ff7fde01732000
OLDMD5=d15160bb1874276c8a53be010fef6202
refuse() { echo "⛔ REFUSE(rc=2): $*"; exit 2; }
red()    { echo "⛔ RED(rc=1): $*"; exit 1; }

[ -d "$FORK/.git" ] || refuse "no git repo at $FORK"
[ -f "$FORK/bin/sbl" ] || refuse "no $FORK/bin/sbl"
have=$(md5sum "$FORK/bin/sbl" | cut -d' ' -f1)
[ "$have" = "$NEWMD5" ] || refuse "the installed binary is $have, not the swapped $NEWMD5 -- this script records a swap that is not the one on disk. Nothing written."
[ -f "$FORK/bin/sbl.bak-$STAMP_UTC" ] || refuse "the dated backup bin/sbl.bak-$STAMP_UTC is missing -- refusing to record a swap whose rollback is not there"
# The repair must actually be in the source we are about to commit, or the commit message would lie.
command grep -q 'beq  wa,=ch_ua,trc10' "$FORK/sbl.min" || refuse "$FORK/sbl.min does not carry the ch_u* repair -- refusing to commit it as the fix"
command grep -q 'blt  wa,=ch_la,fst02' "$FORK/sbl.min" || red "flstg's a-z guard is missing from sbl.min -- that guard must survive verbatim; do not commit this tree"

echo "== fork: $FORK"
echo "   bin/sbl md5 $have  (pre-swap was $OLDMD5)"
echo "   backup  bin/sbl.bak-$STAMP_UTC present"
echo "== pending:"; ( cd "$FORK" && git status --porcelain | sed 's/^/   /' )

if [ "$DRY" = "1" ]; then echo; echo "DRY RUN: would commit bin/sbl + sbl.min, add the .gitignore line, push, and prepend one line to $ORACLES."; exit 0; fi

cd "$FORK" || refuse "cannot cd $FORK"
# Keep the recovery binaries out of history without touching anything else in .gitignore.
if [ -f .gitignore ] && command grep -qx 'bin/sbl.bak-\*' .gitignore; then :; else printf 'bin/sbl.bak-*\n' >> .gitignore; fi
git add bin/sbl sbl.min .gitignore || refuse "git add failed"
git -c user.name=LCherryholmes -c user.email=lcherryh@yahoo.com commit -F - <<MSG || refuse "commit failed"
TRACE dispatch: eleven constants to ch_u*, so the oracle traces every documented type AND still folds names

MINIMAL has ONE opcode flc (fold character). asm.sbl's g_flc emits it as lower->UPPER in
this fork (stock emits upper->lower; that three-line difference is the whole translator
diff), flipped by e68dfeb "SN-30g ... UPPERCASE canonical case".

But flc has FOUR call sites demanding OPPOSITE directions. flstg -- the &CASE name folder
-- guards blt =ch_la / bgt =ch_l_, admitting only a-z, so it REQUIRES lower->UPPER. The
trace procedure and the cnc control-card scanner fold the first character and then compare
it against LOWERCASE constants (ch_la equ 97), so they REQUIRE upper->lower. One opcode
cannot serve both, so this build folded names correctly and refused EVERY trace type with
ERROR 199, while stock traced correctly and its &CASE folding was a silent no-op. Neither
was a correct SPITBOL.

The cure keeps flc as this fork emits it -- that matches the MINIMAL contract, whose own
comment reads "fold to upper case" and whose flstg guard admits only a-z -- and repairs the
eleven dispatch constants to the ch_u* equates, which already existed with correct values
(ch_ua 65, ch_ui 73, ch_un 78, ch_uv 86):

  trace  ch_la->ch_ua  ch_lv->ch_uv  ch_lf->ch_uf  ch_lr->ch_ur (x2)
         ch_ll->ch_ul  ch_lk->ch_uk  ch_lc->ch_uc (x2)          ch_bl unchanged
  cnc01  ch_li->ch_ui
  cnc07  ch_ln->ch_un

Deliberately NOT the three-line translator revert: that trades the trace defect for the
&CASE defect -- green on the trace witness while silently disabling name folding.

Measured before the swap: 4/4 acceptance in ONE binary (TRACE('X','VALUE') traces,
TRACE('X','value') traces, abc==ABC under -b prints 5, -bf stays case-sensitive), which no
build on this box achieved before; 180-fixture regression census against the pre-fix binary
changed exactly the 8 trace-class fixtures with zero collateral; 3/3 byte-agreement with
stock on the fixtures SCRIP already passes.

Swapped $STAMP_CDT (backup bin/sbl.bak-$STAMP_UTC, pre-swap md5 $OLDMD5,
installed $NEWMD5). Law: RULES.md sec Oracles STOP-AND-FIX, CEO-280/282/284.
Found and staged by hq_B; run by Lon.
MSG
git push origin HEAD 2>&1 | tail -2 || refuse "push failed -- the commit is local; retry the push"
NEWCOMMIT=$(git rev-parse --short HEAD)
echo "== fork committed and pushed: $NEWCOMMIT"

# ---- ORACLES.md: INSERT one line at the top. Never a rewrite of content this seat cannot read.
if [ ! -f "$ORACLES" ]; then
    echo "⚠ $ORACLES does not exist -- skipping the top line rather than creating a file whose shape nobody specified."
    echo "  Record by hand: SPITBOL correctness oracle swapped $STAMP_CDT, fork $NEWCOMMIT, md5 $NEWMD5, backup bin/sbl.bak-$STAMP_UTC."
    exit 0
fi
cp -p "$ORACLES" "$ORACLES.bak-$STAMP_UTC" || refuse "could not back up $ORACLES -- refusing to edit it"
echo "== $ORACLES BEFORE (first 3 lines):"; head -3 "$ORACLES" | sed 's/^/   | /'
LINE="⛔ SPITBOL correctness oracle \`/home/resources/x64/bin/sbl\` SWAPPED $STAMP_CDT — fork commit \`$NEWCOMMIT\` (TRACE dispatch: eleven constants to \`ch_u*\`), md5 \`$NEWMD5\` (pre-swap \`$OLDMD5\`), rollback \`bin/sbl.bak-$STAMP_UTC\`. Any board or ref measured BEFORE that minute on a program calling TRACE or setting &FTRACE must be re-measured; \`sbl -bf\` is unchanged as the invocation."
printf '%s\n' "$LINE" | cat - "$ORACLES" > "$ORACLES.new" && mv "$ORACLES.new" "$ORACLES" || refuse "insert failed; restore from $ORACLES.bak-$STAMP_UTC"
echo "== $ORACLES AFTER (first 4 lines):"; head -4 "$ORACLES" | sed 's/^/   | /'
echo
echo "✅ BOTH RECEIPTS LANDED. fork=$NEWCOMMIT · ORACLES.md top line written (backup $ORACLES.bak-$STAMP_UTC)."
echo "   If the ORACLES.md shape is wrong: mv $ORACLES.bak-$STAMP_UTC $ORACLES"
