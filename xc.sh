#!/usr/bin/env bash
# Lean resumable 2-arm crosscheck runner (m3/m4), TSV per program.
# Usage: xc.sh <scrip-binary> <out.tsv> <start-idx> <count>
SB="$1"; OUT="$2"; ST="${3:-0}"; CNT="${4:-1000}"
RT="${RTDIR:-/home/claude/SCRIP/out}"
W=$(mktemp -d); trap "rm -rf $W" EXIT
mapfile -t FILES < <(ls /home/claude/corpus/crosscheck/*/*.sno | sort)
i=0
for f in "${FILES[@]}"; do
  i=$((i+1)); [ $i -le $ST ] && continue; [ $i -gt $((ST+CNT)) ] && break
  n=$(basename "$f" .sno); ref="${f%.sno}.ref"
  [ -f "$ref" ] || { printf "%s\tNOREF\t0\tNOREF\t0\n" "$n" >> "$OUT"; continue; }
  # ---- m3 ----
  ( cd "$W" && timeout 8s env LD_LIBRARY_PATH=$RT "$SB" --run "$f" > m3.o 2> m3.e ); r3=$?
  if [ $r3 -eq 124 ]; then v3=TIMEOUT; elif diff -q "$W/m3.o" "$ref" >/dev/null 2>&1; then v3=PASS; else v3=FAIL; fi
  # ---- m4 ----
  ( cd "$W" && timeout 8s env LD_LIBRARY_PATH=$RT "$SB" --compile "$f" > m4.s 2> m4.ce ); rc=$?
  if [ $rc -ne 0 ]; then v4=CERR; r4=$rc; else
    ( cd "$W" && gcc -no-pie -o m4.bin m4.s -L$RT -lscrip_rt 2> m4.le ); lc=$?
    if [ $lc -ne 0 ]; then v4=LERR; r4=$lc; else
      ( cd "$W" && LD_LIBRARY_PATH=$RT timeout 8s ./m4.bin > m4.o 2> m4.e ); r4=$?
      if [ $r4 -eq 124 ]; then v4=TIMEOUT; elif diff -q "$W/m4.o" "$ref" >/dev/null 2>&1; then v4=PASS; else v4=FAIL; fi
    fi
  fi
  printf "%s\t%s\t%s\t%s\t%s\n" "$n" "$v3" "$r3" "$v4" "$r4" >> "$OUT"
done
echo "done through index $i"
