#!/usr/bin/env bash
# pcmp.sh <W> <B> <out> [langs] -- parse-only comparison (Lon 2026-09-29): C = W/out/parser_L timing only its parser (no lowering, no I/O,
# includes not expanded); SCRIP m4 (harness link, SCRIP_DIAG=0) and SPITBOL (-bf, transpiled) running the .sc chain, each timing only
# Init*() + Src ? Compiland + Pop(); input read by INPUT(...) + Src = INPUT and tree output are outside every clock. SCRIP and SPITBOL
# both -s2000m -d8000m -i64m. Same file list for all three (the C-complete subset where the C parser exits on an error). 3 runs, median.
S=/tmp/claude-1000/-home-claude-ceo/ceo-work-2026-09-29; W=$1; B=$2; O=$3; shift 3
C=/home/claude_ceo/corpus; SBL=/home/resources/spitbol-bench-oracle/sbl; export SCRIP_DIAG=0; SW="-s2000m -d8000m -i64m"; mkdir -p $O
m() { grep "^PARSER-METRICS" "$1" | grep -o " $2=[0-9]*" | head -1 | cut -d= -f2; }
med() { printf '%s\n' "$@" | sort -n | sed -n '2p'; }
ms() { awk -v u="$1" 'BEGIN { if (u == "") printf "-"; else printf "%.1f", u / 1000 }'; }
x() { awk -v r="$1" -v s="$2" 'BEGIN { if (r == "" || s == "" || s == 0) printf "-"; else printf "%.2fx", r / s }'; }
echo "PCMP tree $(git -C $W rev-parse --short HEAD)$(git -C $W diff --quiet || echo -dirty) RT_OPT=$(make -s -C $W RT_OPT="${RT_OPT:--O0 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer}" buildinfo 2>/dev/null | grep -m1 '^RT_OPT' | cut -d: -f2- | xargs) runtime=$(readlink -f $W/out/libscrip_rt.so | sed 's#.*/##') switches $SW load $(cut -d' ' -f1-3 /proc/loadavg)"
printf '%-8s %5s %9s | %-16s | %-16s | %-16s | %-9s | %s\n' lang files bytes "C parse ms" "SCRIP parse ms" "SBL parse ms" "SBL/SCRIP" trees
for L in ${*:-snobol4 snocone icon prolog rebus pascal}; do
  if [ -f $S/cclean/$L.ok ]; then cp $S/cclean/$L.ok $O/$L.list; else grep -vxF -f $S/corp/orig/$L/sbl.crash $S/corp/orig/$L.list > $O/$L.list 2>/dev/null || cp $S/corp/orig/$L.list $O/$L.list; fi
  cat $B/global.sc $B/case.sc $B/assign.sc $B/match.sc $B/counter.sc $B/stack.sc $B/tree.sc $B/ShiftReduce.sc $B/tdump.sc $B/gen.sc $B/qize.sc $B/semantic.sc $B/omega.sc $B/trace.sc $B/parser_$L.sc > $O/$L.sc
  $W/scrip --compile $O/$L.sc -o $O/$L.s < /dev/null > $O/$L.cc.err 2>&1 && (cd $W && gcc -c $O/$L.s -o $O/$L.o && gcc $O/$L.o -L out -lscrip_rt -lm -Wl,-rpath,$W/out -o $O/$L.bin) 2>> $O/$L.cc.err || { echo "$L: m4 build failed"; continue; }
  $W/scrip --transpile $O/$L.sc > $O/$L.sno 2>/dev/null
  cp=(); sp=(); bp=()
  for k in 1 2 3; do
    ( cd $C; PARSER_FILES=$O/$L.list timeout 3000 $W/out/parser_$L > $O/$L.c.out 2> $O/$L.c.err ); cp+=($(m $O/$L.c.err parse_us))
    PARSER_FILES=$O/$L.list SCRIP_DIAG=0 timeout 3000 $O/$L.bin $SW < /dev/null > $O/$L.m4.out 2> $O/$L.m4.err; sp+=($(m $O/$L.m4.err parse_us))
    PARSER_FILES=$O/$L.list timeout 3000 $SBL -bf $SW $O/$L.sno < /dev/null > $O/$L.sbl.out 2> $O/$L.sbl.err; bp+=($(m $O/$L.sbl.err parse_us))
  done
  c=$(med ${cp[@]}); s=$(med ${sp[@]}); b=$(med ${bp[@]})
  t=$(cmp -s $O/$L.m4.out $O/$L.sbl.out && echo SCRIP==SBL || echo DIFFER)
  printf '%-8s %5s %9s | %-16s | %-16s | %-16s | %-9s | %s\n' $L "$(m $O/$L.m4.err files)" "$(m $O/$L.m4.err bytes)" "$(ms $c)" "$(ms $s)" "$(ms $b)" "$(x $b $s)" "$t"
done
