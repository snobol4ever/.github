#!/bin/bash
# util_relay_baton_bench.sh -- THE RELAY-BATON BEFORE/AFTER BENCHMARK of hq_zetas' spine chunks (ceo CEO-1756 Icon, CEO-1757 Prolog; Lon 2026-10-14 18:4x-18:5x CDT, in-chat to the ceo, verbatim:
# "Have the Icon do a before and after benchmark measurements under a RELAY-RACE build baton." / "Have the Prolog do ...").
# The coo holds the baton while it runs: it TELLS every working seat (no pushes, no builds, no tests), builds the landing's parent (BEFORE) and the landing (AFTER) in two scratch
# worktrees, runs bench_triangulate_<lang>.sh on each back to back at the shared machine's quiet, stamps the load, writes one line per tree to
# /home/resources/progress/bench/<LANG>_SPINE_BEFORE_AFTER.txt, composes the per-kernel multiples for the telegram, removes the worktrees and RELEASES the baton.
#   USAGE: util_relay_baton_bench.sh icon|prolog [LANDING_HASH [BEFORE_HASH]] [--dry]      (no hash: the newest origin/main commit whose message carries the chunk's tag;
#   no BEFORE: the landing's parent; a BEFORE names the pair the ceo rules when the cure sits past the chunk -- CEO-1756: 7eccc5280 BEFORE, 5e5b77076 AFTER, ceo to the coo 2026-10-15)
# EXIT 0 both lines written under the baton; 2 REFUSED (no landing yet, the box is busy or over the load guard, a build failed); 3 a tree read over the load guard twice (no reading).
# NEVER: it writes no progress row (S4E_PROGRESS_OFF=1: the Prolog instrument would append its kernels to the shared database stamped with the tree it measured) and no TSV into corpus/
# (OUT_TSV is scratch: the Prolog default lands inside the root corpus, where a coverage gate globs it); it sends the telegram text to a file and does not send it.
# SOURCED, IT ONLY DEFINES ITS FUNCTIONS (the coo's 10-14 18:45 incident: a sourced loop script ran three accidental loops).
RELAY_ROOT="${RELAY_ROOT:-/home/claude_coo}"
RELAY_SEATS="${RELAY_SEATS:-ceo cto cfo hq_snobol4 hq_icon hq_prolog hq_pascal hq_snocone hq_raku hq_templates hq_runtime hq_collector hq_zetas}"
RELAY_MSG="${RELAY_MSG:-$RELAY_ROOT/SCRIP/scripts/s4e_msg.sh}"
RELAY_BENCH_DIR="${RELAY_BENCH_DIR:-/home/resources/progress/bench}"

relay_load1() { echo "${RELAY_LOAD1:-$(cut -d' ' -f1 /proc/loadavg)}"; }
relay_guard() { echo "${LOAD_GUARD:-$(nproc)}"; }
relay_over() { awk -v l="$1" -v g="$(relay_guard)" 'BEGIN { exit !(l + 0 >= g + 0) }'; }  # CEO-1686/1574: a 1-minute load at or above the cores is no reading

relay_conf() {  # lang -> TAG LINE FILE INSTR (global)
  case "$1" in
    icon)   R_TAG=ICON-SPINE-CHUNK-CEO-1756;     R_LINE=ICON_SPINE_BENCH;   R_FILE=ICON_SPINE_BEFORE_AFTER.txt;   R_INSTR=bench_triangulate_icon.sh;;
    prolog) R_TAG=PROLOG-SPINE-CHUNK-CEO-1757;   R_LINE=PROLOG_SPINE_BENCH; R_FILE=PROLOG_SPINE_BEFORE_AFTER.txt; R_INSTR=bench_triangulate_prolog.sh;;
    *) echo "relay: language must be icon or prolog" >&2; return 2;;
  esac
}

relay_tell_all() {  # take|release: one line to every other working seat
  local what="$1" seat txt n=0
  case "$what" in
    take)    txt="coo HOLDS THE BUILD BATON ($R_TAG, $(date '+%F %H:%M %Z')): from now NO pushes, NO builds and NO tests by any seat until the coo releases it -- a before/after benchmark needs a quiet box. Keep what you have uncommitted; the release comes in a second telegram.";;
    release) txt="coo RELEASES THE BUILD BATON ($R_TAG, $(date '+%F %H:%M %Z')): pushes, builds and tests may resume.";;
  esac
  for seat in $RELAY_SEATS; do
    printf '%s\n' "$txt" | bash "$RELAY_MSG" send "$seat" "relay-baton-$what-$R_TAG" --stdin > /dev/null 2>&1 && n=$((n+1))
  done
  echo "baton $what: told $n of $(echo $RELAY_SEATS | wc -w) seats"
}

relay_quiet_refusal() {  # empty when the box is quiet enough to read; else the reason (this root's loop and boards, any bench or build, the load guard)
  local busy
  busy=$(ps -eo pid,args | grep -E 'bash loop3\.sh|run_blocking_set|test_.*_suite\.sh|corpus_suite_harness|bench_triangulate|make( |$)' | grep -v -E 'grep|util_relay_baton_bench' | cut -c1-110 | head -5)
  [ -n "$busy" ] && { echo "busy: $busy"; return; }
  relay_over "$(relay_load1)" && echo "load1 $(relay_load1) is at or above the guard $(relay_guard)"
  return 0
}

relay_mkwt() {  # name hash -> builds the tree in a fresh worktree; refuses a worktree whose runtime is not its own (memory: worktree out symlink swaps the root runtime)
  local wt="$RELAY_ROOT/.scratch/wt/$1"
  git -C "$RELAY_ROOT/SCRIP" worktree remove --force "$wt" 2>/dev/null; git -C "$RELAY_ROOT/SCRIP" worktree prune
  git -C "$RELAY_ROOT/SCRIP" worktree add -q --detach "$wt" "$2" || return 2
  [ -L "$wt/out" ] && { echo "relay: $wt/out is a symlink -- refused"; return 2; }
  ( cd "$wt" && make -j8 > "$RELAY_ROOT/.scratch/relay/$1.make.out" 2>&1 ) || { echo "relay: build of $1 failed, see .scratch/relay/$1.make.out"; return 2; }
  [ -x "$wt/scrip" ] && [ "$(readlink -f "$wt/out/libscrip_rt.so")" = "$wt/out/libscrip_rt.so" ] || { echo "relay: $1 did not build its own scrip and runtime"; return 2; }
  echo "$wt"
}

relay_summarize() {  # lang tsv -> "kernels=N PASS=p FAIL=f"
  case "$1" in
    icon)   awk -F'\t' '!/^#/ && NF >= 13 { k[$1]=1; if ($13 == "PASS") p++; else f++ } END { printf "kernels=%d PASS=%d FAIL=%d", length(k), p+0, f+0 }' "$2";;
    prolog) awk -F'\t' '!/^#/ && $1 != "kernel" && NF >= 6 { k[$1]=1; if ($6 == "AGREE") p++; else if ($6 == "DISAGREE") f++ } END { printf "kernels=%d PASS=%d FAIL=%d", length(k), p+0, f+0 }' "$2";;
  esac
}

relay_multiples() {  # lang before.tsv after.tsv -> per kernel and engine (m3, m4): "kernel engine multiple", multiple = BEFORE time / AFTER time (over 1 = faster); then the geometric mean per engine
  local lang="$1"
  awk -F'\t' -v lang="$lang" '
    FNR == 1 { fi++ }
    /^#/ || $1 == "kernel" { next }
    lang == "icon"   && NF >= 13 && ($2 == "m3" || $2 == "m4") && $4 > 0 && $5 > 0 { key = $1 SUBSEP $2; t = $5 / $4; if (fi == 1) B[key] = t; else A[key] = t }
    lang == "prolog" && NF >= 6  && ($2 == "m3" || $2 == "m4") && $4 + 0 > 0        { key = $1 SUBSEP $2; if (fi == 1) B[key] = $4 + 0; else A[key] = $4 + 0 }
    END {
      for (key in B) { if (!(key in A)) continue; split(key, p, SUBSEP)
        m = (lang == "icon") ? B[key] / A[key] : A[key] / B[key]
        printf "%s %s %.3f\n", p[1], p[2], m; ls[p[2]] += log(m); n[p[2]]++ }
      for (e in n) printf "GEOMEAN %s %.3f over %d kernel(s)\n", e, exp(ls[e] / n[e]), n[e] }' "$2" "$3" | LC_ALL=C sort
}

relay_run_tree() {  # label wt hash -> writes $OUTDIR/$label.tsv/.grid and sets R_LOAD (the highest 1-minute load seen), R_RC
  local label="$1" wt="$2" tsv="$OUTDIR/$1.tsv" grid="$OUTDIR/$1.grid" try max l sampler
  for try in 1 2; do
    : > "$tsv"; max=$(relay_load1)
    ( while :; do relay_load1; sleep 10; done > "$OUTDIR/$label.load" ) & sampler=$!
    case "$R_LANG" in
      icon)   S4E_HOME="$RELAY_ROOT" S4E_PROGRESS_OFF=1 SCRIP="$wt/scrip" bash "$wt/scripts/$R_INSTR" --out "$tsv" > "$grid" 2>&1; R_RC=$?;;
      prolog) S4E_HOME="$RELAY_ROOT" S4E_PROGRESS_OFF=1 OUT_TSV="$tsv" SCRIP="$wt/scrip" bash "$wt/scripts/$R_INSTR" > "$grid" 2>&1; R_RC=$?;;
    esac
    kill "$sampler" 2>/dev/null; wait "$sampler" 2>/dev/null
    for l in $(cat "$OUTDIR/$label.load" 2>/dev/null) $(relay_load1); do awk -v a="$l" -v b="$max" 'BEGIN { exit !(a + 0 > b + 0) }' && max=$l; done
    R_LOAD=$max
    relay_over "$R_LOAD" || return 0
    echo "relay: $label read at load $R_LOAD, at or above the guard $(relay_guard) -- no reading; take $try of 2"
  done
  return 3
}

relay_write() {  # label hash -> appends the DONE-WHEN line and the grid to the progress file
  local label="$1" hash="$2" up; up=$(echo "$label" | tr a-z A-Z)
  { printf '%s %s tree=%s %s load=%s baton=held\n' "$R_LINE" "$up" "$hash" "$(relay_summarize "$R_LANG" "$OUTDIR/$label.tsv")" "$R_LOAD"
    sed 's/^/  /' "$OUTDIR/$label.grid"; } >> "$RELAY_BENCH_DIR/$R_FILE"
}

relay_main() {
  local lang="${1:-}" land="" before="" dry=0 parent bwt awt rc=0 refusal a
  shift
  for a in "$@"; do
    case "$a" in
      --dry) dry=1;;
      *) if [ -z "$land" ]; then land="$a"; elif [ -z "$before" ]; then before="$a"; else echo "relay: too many arguments" >&2; return 2; fi;;
    esac
  done
  R_LANG="$lang"; relay_conf "$lang" || return 2
  git -C "$RELAY_ROOT/SCRIP" fetch -q origin 2>/dev/null
  [ -n "$land" ] || land=$(git -C "$RELAY_ROOT/SCRIP" log origin/main -1 --format=%H --grep="$R_TAG")
  [ -n "$land" ] || { echo "REFUSED(2): no commit carrying $R_TAG is on origin yet -- hq_zetas has not pushed the chunk"; return 2; }
  land=$(git -C "$RELAY_ROOT/SCRIP" rev-parse --verify -q "$land^{commit}") && parent=$(git -C "$RELAY_ROOT/SCRIP" rev-parse --verify -q "${before:-$land^}^{commit}") || { echo "REFUSED(2): a hash does not name a commit"; return 2; }
  git -C "$RELAY_ROOT/SCRIP" merge-base --is-ancestor "$parent" "$land" || { echo "REFUSED(2): BEFORE $parent is not an ancestor of AFTER $land"; return 2; }
  OUTDIR="$RELAY_ROOT/.scratch/relay/$(date +%Y%m%dT%H%M%S)-$lang"; mkdir -p "$OUTDIR" "$RELAY_BENCH_DIR"
  echo "relay $lang: BEFORE=$parent AFTER=$land out=$OUTDIR guard=$(relay_guard)"
  [ "$dry" = 1 ] && { echo "dry run: nothing taken, built or measured"; return 0; }
  relay_tell_all take
  # a seat told to stop may be mid-build when the baton is taken: wait up to RELAY_QUIET_WAIT seconds (default 600) for the box to go quiet, then refuse
  local waited=0
  while refusal=$(relay_quiet_refusal); [ -n "$refusal" ] && [ "$waited" -lt "${RELAY_QUIET_WAIT:-600}" ]; do sleep 15; waited=$((waited + 15)); done
  [ -z "$refusal" ] || { echo "REFUSED(2): still not quiet after ${waited}s: $refusal"; relay_tell_all release; return 2; }
  echo "quiet after ${waited}s (load1 $(relay_load1), guard $(relay_guard))"
  trap 'git -C "$RELAY_ROOT/SCRIP" worktree remove --force "$RELAY_ROOT/.scratch/wt/relay-before" 2>/dev/null; git -C "$RELAY_ROOT/SCRIP" worktree remove --force "$RELAY_ROOT/.scratch/wt/relay-after" 2>/dev/null' RETURN
  mkdir -p "$RELAY_ROOT/.scratch/relay"
  bwt=$(relay_mkwt relay-before "$parent") || { echo "$bwt"; relay_tell_all release; return 2; }
  awt=$(relay_mkwt relay-after "$land")   || { echo "$awt"; relay_tell_all release; return 2; }
  relay_run_tree before "$bwt" "$parent"; rc=$?; [ $rc = 0 ] && relay_write before "$parent"
  [ $rc = 0 ] && { relay_run_tree after "$awt" "$land"; rc=$?; [ $rc = 0 ] && relay_write after "$land"; }
  if [ $rc = 0 ]; then
    { echo "$R_LINE before/after multiples (BEFORE time / AFTER time, over 1 is faster), BEFORE $parent, AFTER $land, load $R_LOAD, the chunk $R_TAG:"
      relay_multiples "$lang" "$OUTDIR/before.tsv" "$OUTDIR/after.tsv"; } > "$OUTDIR/telegram.txt"
    echo "wrote $RELAY_BENCH_DIR/$R_FILE; telegram text at $OUTDIR/telegram.txt (not sent)"
  fi
  relay_tell_all release
  return $rc
}

[ "${BASH_SOURCE[0]}" = "$0" ] && { set -u; relay_main "$@"; }
