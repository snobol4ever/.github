#!/usr/bin/env bash
# FF-0b — is the calculator DIVERGE quartet a SECOND defect, or the DEL-T1 culprit?
# Runs the four never-bisected programs against the sbl oracle using board_sno15_ident.sh's
# recipe VERBATIM (temp-prepend -CASE 0 + tab &TRIM=0; sbl -b -d512m -i64m; ulimit -s unlimited).
set -u
SC=${SC:-/home/claude/SCRIP}; D=${D:-/home/claude/corpus/programs/snobol4/demo}
SBL=${SBL:-/home/claude/x64/bin/sbl}; TAG=${TAG:-HEAD}
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
ulimit -s unlimited
printf '%-28s %-10s %s\n' "PROGRAM@$TAG" M3 NOTE
for nm in calculator-1-match calculator-1-match-fence calculator-2-match calculator-2-match-fence; do
  src="$D/$nm.sno"; inp="$D/calculator.input"
  printf -- '-CASE 0\n\t&TRIM = 0\n' > "$W/$nm.sbl.sno"; cat "$src" >> "$W/$nm.sbl.sno"
  if ! timeout 120 "$SBL" -b -d512m -i64m "$W/$nm.sbl.sno" < "$inp" > "$W/$nm.sbl" 2>/dev/null; then
    printf '%-28s %-10s %s\n' "$nm" - "SBL FAILED"; continue; fi
  if timeout 120 "$SC/scrip" --run "$src" < "$inp" > "$W/$nm.m3" 2>/dev/null; then
    if cmp -s "$W/$nm.sbl" "$W/$nm.m3"; then m3=IDENT; note=""
    else m3=DIVERGE
      note="sbl=$(wc -c < "$W/$nm.sbl")B m3=$(wc -c < "$W/$nm.m3")B firstdiff=$(cmp "$W/$nm.sbl" "$W/$nm.m3" 2>/dev/null | sed 's/.*byte //;s/,.*//')"
    fi
  else rc=$?; m3="RC=$rc"; note="(139=SIGSEGV)"; fi
  printf '%-28s %-10s %s\n' "$nm" "$m3" "$note"
done
