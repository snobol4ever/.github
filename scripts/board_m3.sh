#!/usr/bin/env bash
# m3-only board — same recipe as board_sno15_ident.sh, mode 3 only, for cheap set-sizing.
set -u
SC=${SC:-/home/claude/SCRIP}; D=${D:-/home/claude/corpus/programs/snobol4/demo}
SBL=${SBL:-/home/claude/x64/bin/sbl}; TMO=${TMO:-30}; TAG=${TAG:-?}
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
ulimit -s unlimited
inp_for() { case $1 in claws5*) echo "$D/CLAWS5inTASA.dat";; treebank*) echo "$D/VBGinTASA.dat";;
  json*) echo "$D/twitter.json";; calculator*) echo "$D/calculator.input";; *) echo "";; esac; }
xf_for()  { case $1 in treebank*) echo "-s256m";; *) echo "";; esac; }
for nm in "$@"; do
  src="$D/$nm.sno"; inp=$(inp_for "$nm"); xf=$(xf_for "$nm")
  printf -- '-CASE 0\n\t&TRIM = 0\n' > "$W/s.sno"; cat "$src" >> "$W/s.sno"
  if ! timeout $TMO "$SBL" -b -d512m -i64m $xf "$W/s.sno" < "$inp" > "$W/o" 2>/dev/null; then
    printf '%-26s %s\n' "$nm" "SBL-FAIL/TIMEOUT"; continue; fi
  if timeout $TMO "$SC/scrip" --run "$src" < "$inp" > "$W/m" 2>/dev/null; then
    cmp -s "$W/o" "$W/m" && printf '%-26s %s\n' "$nm" IDENT || printf '%-26s %s\n' "$nm" DIVERGE
  else printf '%-26s %s\n' "$nm" "RC=$?"; fi
done
