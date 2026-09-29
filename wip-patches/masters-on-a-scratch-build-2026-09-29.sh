#!/usr/bin/env bash
# masters_speed.sh [langs] -- every master on the SPEED build (wt-o2: RT_OPT -O2 ... -DRT_DIAG=0), both modes, progress rows to a
# scratch table (never the live one), each master's FAIL list printed whole.
T=/home/satirical/.claude/jobs/ef0b4539/tmp; W=${W:-$T/wt-o2}; TAG=${TAG:-speed}; C=/home/claude_ceo/corpus
export S4E_HOME=/home/claude_ceo S4E_PROGRESS_DB=$T/${TAG}_progress.tsv SUITE_LIST_ALL=1
echo "MASTERS on $(readlink -f $W/out/libscrip_rt.so | sed 's#.*/##') tree $(git -C $W rev-parse --short HEAD)+rtdiag load $(cut -d' ' -f1-3 /proc/loadavg) at $(date '+%H:%M:%S')"
for L in ${*:-snobol4:sno snocone:sc icon:icn prolog:pl rebus:reb pascal:pas raku:raku}; do
  lang=${L%%:*}; ext=${L##*:}; t0=$(date +%s)
  python3 $W/scripts/corpus_suite_harness.py run $C/tests/$lang/ALL.$ext $C/tests/$lang/ALL.ref --lang $lang --modes m3,m4 > $T/ms_${TAG}_$lang.log 2>&1; rc=$?
  echo "$lang rc=$rc $(( $(date +%s) - t0 ))s $(grep -m1 -o 'SUITE_BOARD.*' $T/ms_${TAG}_$lang.log | grep -o 'total=[0-9]*\|m[34]_pass=[0-9]*\|m[34]_fail=[0-9]*\|m[34]_crash=[0-9]*\|m[34]_hang=[0-9]*\|m[34]_xfail=[0-9]*\|m[34]_skip=[0-9]*' | tr '\n' ' ')"
done
echo "done $(date '+%H:%M:%S')"
