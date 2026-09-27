# FINDING 2026-09-27 hq_snocone -- two FENCE lowering defects in lower_snobol4.c, cured and parked with their gate

**⭐ LANDED 2026-09-27 at SCRIP `cc0e5a2a6`** (hq_snocone; folded into GOAL-SNOCONE-100.md's cursor SC-PARSERS-TENET-2026-09-27c and the baton): the patch below applied byte-for-byte after the cfo's match-frame cell (6760234e8), the gate grew to 11 witnesses (witness 11 = the 09-16 runtime-built FENCE under nested ARBNO, whose row is now DONE by its DONE-WHEN), FAIL-ONCE on the unpatched a418edc3e and PASS-ONCE cured, wired and adopted; per CEO-1316 the per-landing verdict was the touched gates and preflight 63/0; the four arms this file listed as unattributed all read the same on the unpatched tree (A/B). No bare-poll re-cut was owed: origin's df02f017e carried it. What remains open in this file: the fenced body held in a VARIABLE (with the cto, trace sent) and the switch row (the delta-debug tool below is its instrument).

**Tree:** SCRIP `18084049f` + the patch below (uncommitted, reverted at handoff) · corpus `ae37b27ae` · RT_OPT=-O0 · incremental `make`.
**Why parked, not landed:** the shared-node control arm (`make test`, 582 arms) was stopped part-way at the handoff Lon asked for; a
cure to `lower_snobol4.c` does not land on a partial blocking set. **Row:** `snocone-a-switch-case-arm-holding-any-statement-refuses-under-parser-snocone-on-scrip-and-parses-on-spitbol-ctl-switch-and-ctl-switch-default`
(reowned to hq_snocone by the cto 2026-09-27, CLAIMED).

## The two defects -- pure SNOBOL4, SPITBOL YES, SCRIP NO in m3 and m4 before the patch, YES after

1. **A one-argument FENCE followed by a multi-element run.** `TT_SEQ` builds a fenced sequence right to left; after building
   FENCE1 it re-routes the right-hand run's failure exit into the FENCE's beta through `right_tail`. For a MULTI-element run
   `right_tail` held the run's LAST element (its resume node, `n_rt`), so the last element's omega jumped straight to
   `match_fence1_beta` and every alternative between the FENCE and it was skipped (ASM-DIFF of a passing and a failing sibling in
   one mode: the literal `'c'`'s three failure jumps retargeted from `match_alternate_beta` to `match_fence1_beta`).
   Witness: `'xabc' ? FENCE('x') ('a' | 'ab') 'c'`. Cure: for a multi-element run `right_tail` is its FIRST element's head
   (`g->all[_rb2]`, index `_rb2`), the node a one-element run already used.
2. **An ARBNO whose body is a fenced sequence.** `TT_ARBNO` pushes operands 1 and 2 as the first and the last node BUILT; the
   emitter (`flat_drive_match_alt`, PAIR 4) scans that index range backwards for the last node whose gamma is the ARBNO and takes
   its beta as the iteration's resume. A right-to-left fenced body put the range over its first elements only, so resuming fell
   to the body's first element. Witness: `'{c:bb}' ? POS(0) '{' ARBNO('c' FENCE('') ':' ARBNO('b')) '}' RPOS(0)`. Cure: the
   fenced `TT_SEQ` publishes the last node built for its rightmost segment together with the entry it returns
   (`scx_t.seq_rlast`, `seq_rlast_for`, fields not globals); `TT_ARBNO` uses entry and that node when the entry is its own body's.

## STILL OPEN after the patch

- `ARBNO(P)` with the fenced sequence held in a VARIABLE (a PAT$ graph whose fenced body root meets the zeta seam-tier check in
  `sno_pat_publish_body_root`): `P1 = 'c' FENCE('+' | '') ':' ARBNO('b'); '{c:bb}' ? POS(0) '{' ARBNO(P1) '}' RPOS(0)`.
- The switch row itself: with the patch the bracket (`run_parser_sync_monitor.sh snocone` on `x = 1; switch (x) { case 1: OUTPUT = 1; }`)
  moves from step 2296 to 2283 -- both engines now read `case` and then `OUTPUT` twice; SPITBOL then tries the next Command
  alternative (`if_cmd` reads `OUTPUT` a third time) while SCRIP abandons the FENCE'd Command alternation after the deferred
  `DefaultArm` fails and backtracks to `case`. Two SNOBOL4 mirrors of that grammar (static, and runtime-built through a
  pattern-returning `NINC()`) pass on SCRIP, so the trigger needs more of the real grammar; a statement-level delta-debug of
  `parser_snocone.sc` (script below) was started and stopped at the handoff.

## MEASURED with the patch (the parts that ran)

- The gate below: 10/10 witnesses byte-identical to the oracle in m3 and in m4.
- The partial `make test` (serial phase before the stop): four non-green arms, none yet attributed --
  `test_gate_sc_port_trace` rc 1 (20 failed of 268, 248 NOREF), `test_gate_pas_port_trace` rc 1 (20 failed of 70; Pascal does not
  lower through `lower_snobol4.c`, so at least this one predates the patch), `test_gate_sno_port_trace_oracle_diff` rc 2 (a DEFINE
  witness produced zero call-box lines), `test_gate_preflight_arms_stay_cheap` rc 1 (wall time at load 35, CPU within budget).
  Each owes an A/B on the unpatched build before the landing.
- Parser censuses with the patch built: snocone SCRIP 97 parsed / 2 declared / 2 refused (the switch members) of 101 -- unchanged.

## THE LANDING, for the next sitting, in order

1. Pull, rebuild, `git -C SCRIP apply <the patch below>`, save the gate below as
   `SCRIP/scripts/test_gate_sno_a_fence_before_a_run_or_inside_an_arbno_body_retries_what_follows_it.sh` (chmod +x), `make`.
2. FAIL-ONCE / PASS-ONCE: the gate FAILS on the unpatched build (witnesses 1, 2, 3, 4, 5, 6, 7 read NO) and PASSES on the patched one.
3. `make test` to completion; each red arm A/B'd on the unpatched build (the four above first). SnoM is hq_snobol4's to grade.
4. The cfo's order (2026-09-27 08:17 CDT): if the cfo's match-frame cell (grows every match frame by 32 bytes) lands first, run
   `test_gate_gc_a_nested_match_restores_a_moved_outer_subject.sh` on the combined tree before landing this.
5. The cto's bare-poll re-cut, in the same landing (the patch moves credited `lower_snobol4.c` sites by line): on the freshly built,
   rebased tree, with `SCRIP_HEAP_KB` unset and `SCRIP_HEAP_MB=512`, run `scripts/util_gc_safe_point_contract.py` over every program
   in `scripts/gc_witnesses` (the icn, sno, pl, raku and sc files) with `--write-bare-poll-table`; it must read
   `CONTRACT BARE-POLL-NOTES mismatched=0` and `sites=156 unwitnessed=57 undeclared=0`; then
   `test_gate_gc_every_credited_bare_poll_site_has_a_zero_collection_witness.sh` must be 4 of 4; commit
   `scripts/gc_bare_poll_witnesses.tsv` with the cure. If unwitnessed rises, send the reading to the cto.
6. Wire the gate into `Makefile:test-sequential`, commit naming both witnesses and this bracket, push, then regenerate the owed
   `.s` artifacts of this lane (codegen touched) and re-run the snocone census.

## The patch (`git diff src/lower/lower_snobol4.c` on `18084049f`)

```diff
diff --git a/src/lower/lower_snobol4.c b/src/lower/lower_snobol4.c
index f42195f72..56c851168 100644
--- a/src/lower/lower_snobol4.c
+++ b/src/lower/lower_snobol4.c
@@ -16,7 +16,8 @@ static int sno_kw_static_slot(const char * kw) { return kw ? rt_kw_index(kw) : -
 extern void global_register(const char * name);
 extern int stage2_proc_grow(stage2_t * s2);
 typedef struct { const tree_t * arg; IR_t * prim; int str; long codes; const char * snapg; } sprearg_t;
-typedef struct { IR_graph_t * g; IR_t * loop_exit; IR_t * loop_next; const char * result_name; IR_t * pat_fail; IR_t * pat_seal; sprearg_t pre[64]; int npre; long prog_nstmt; long stno_base; } scx_t;
+typedef struct { IR_graph_t * g; IR_t * loop_exit; IR_t * loop_next; const char * result_name; IR_t * pat_fail; IR_t * pat_seal; sprearg_t pre[64]; int npre; long prog_nstmt; long stno_base;
+                 IR_t * seq_rlast; IR_t * seq_rlast_for; } scx_t;
 #define SNO_DEF_NAMES_MAX 64
 typedef struct { const char * fname; const char * entry; const char * result_name; const char * names[SNO_DEF_NAMES_MAX]; int nnames; int nformals; } sno_def_t;
 static int sno_fname_is_multiproto(const char * fname);
@@ -1802,7 +1803,9 @@ static IR_t * sno_pat_node(scx_t * cx, const tree_t * t, IR_t * succ, IR_t * fai
         int before = g->n;
         IR_t * prev_seal = cx->pat_seal; cx->pat_seal = R;
         sno_in_arbno++;
+        cx->seq_rlast = NULL; cx->seq_rlast_for = NULL;
         IR_t * ei = sno_pat_node(cx, t->c[0], R, R);
+        IR_t * rl = (cx->seq_rlast && cx->seq_rlast_for == ei) ? cx->seq_rlast : NULL;
         sno_in_arbno--;
         cx->pat_seal = prev_seal;
         if (before >= g->n) sno_fatal("ARBNO body lowered to zero nodes (bare FENCE / null pattern body)", NULL);
@@ -1818,8 +1821,8 @@ static IR_t * sno_pat_node(scx_t * cx, const tree_t * t, IR_t * succ, IR_t * fai
             if (x->γ.node == R) { if (x->op == IR_GOTO && x->ω.node == R) { memcpy(x->γ.sz, "φ", 3); } else { memcpy(x->γ.sz, "σ", 3); } x->γ.sz[3] = 0; }
         }
         ir_operand_push(R, ei);
-        ir_operand_push(R, ri);
-        ir_operand_push(R, (g->n > before) ? g->all[g->n - 1] : ei);
+        ir_operand_push(R, rl ? ei : ri);
+        ir_operand_push(R, rl ? rl : ((g->n > before) ? g->all[g->n - 1] : ei));
         { sno_tvec_t bv = {0}; sno_seq_flatten_pat(t->c[0], &bv);
           if (bv.n > 0 && sno_is_fence(bv.v[bv.n - 1])) ir_operand_push(R, R); ct_drop(bv.v); }
         IR_LIT(R).ival = 1;
@@ -1891,7 +1894,7 @@ static IR_t * sno_pat_node(scx_t * cx, const tree_t * t, IR_t * succ, IR_t * fai
         for (int i = 0; i < ne; i++) if (sno_is_fence(elems[i])) { first_fence = i; break; }
         for (int i = 0; i < ne; i++) if (sno_is_fence0(elems[i])) { first_f0 = i; break; }
         if (first_fence == ne) { IR_t * r0 = ne == 1 ? sno_pat_node(cx, elems[0], succ, fail) : sno_seq_nary(cx, elems, ne, succ, fail, NULL); ct_drop(ev.v); return r0; }
-        IR_t * cur_succ = succ; IR_t * right_tail = NULL; int right_tail_idx = -1; int right_sealed = 0;
+        IR_t * cur_succ = succ; IR_t * right_tail = NULL; int right_tail_idx = -1; int right_sealed = 0; IR_t * rlast = NULL;
         for (int i = ne - 1; i >= 0; ) {
             if (sno_is_fence(elems[i])) {
                 const tree_t * inner = sno_is_fence1(elems[i]) ? elems[i]->c[0] : NULL;
@@ -1941,6 +1944,7 @@ static IR_t * sno_pat_node(scx_t * cx, const tree_t * t, IR_t * succ, IR_t * fai
                     IR_LIT(F).ival = 0;
                     cur_succ = F; right_tail = F; right_tail_idx = f_idx;
                 }
+                if (!rlast && g->n > 0) rlast = g->all[g->n - 1];
                 i--;
                 continue;
             }
@@ -1952,10 +1956,12 @@ static IR_t * sno_pat_node(scx_t * cx, const tree_t * t, IR_t * succ, IR_t * fai
             int _rb2 = before_r; while (_rb2 < g->n && g->all[_rb2] && g->all[_rb2]->op == IR_GOTO && g->all[_rb2]->n_operands == 0) _rb2++;
             IR_t * r_tail = n_rt ? n_rt : ((_rb2 < g->n) ? g->all[_rb2] : re);
             if (right_tail && !right_sealed && before_r < g->n) sno_resume_ω_to(g, right_tail_idx, right_tail, r_tail);
-            cur_succ = re; right_tail = r_tail; right_tail_idx = before_r; right_sealed = 0;
+            cur_succ = re; right_tail = (n_rt && _rb2 < g->n) ? g->all[_rb2] : r_tail; right_tail_idx = (n_rt && _rb2 < g->n) ? _rb2 : before_r; right_sealed = 0;
+            if (!rlast && g->n > 0) rlast = g->all[g->n - 1];
             i = j - 1;
         }
         ct_drop(ev.v);
+        cx->seq_rlast = rlast; cx->seq_rlast_for = cur_succ;
         return cur_succ;
     }
     case TT_ALT: {
@@ -2278,6 +2284,7 @@ static int sno_exprdef_seen(const cv_t * v, const char * f) { if (!f) return 0;
 static IR_graph_t * sno_build_graph(const tree_t ** st, int nst, int entry_idx, const int * is_def, const char * result_name, long stno_base, long end_line) {
     IR_graph_t * g = IR_alloc(nst * 16 + 256);
     scx_t cx; cx.g = g; cx.loop_exit = NULL; cx.loop_next = NULL; cx.result_name = result_name; cx.pat_fail = NULL; cx.pat_seal = NULL; cx.npre = 0; cx.prog_nstmt = (long)nst + 1 + stno_base; cx.stno_base = stno_base;
+    cx.seq_rlast = NULL; cx.seq_rlast_for = NULL;
     IR_t * exitnd = lc_build(g, IR_SUCCEED, NULL, NULL);
     IR_t * failnd = lc_build(g, IR_FAIL, NULL, NULL);
     IR_t ** anchor = (IR_t **) ct_zalloc((size_t) nst, sizeof(IR_t *));
```

## The gate

```bash
#!/usr/bin/env bash
# test_gate_sno_a_fence_before_a_run_or_inside_an_arbno_body_retries_what_follows_it.sh -- FENCE(P) COMMITS P, NOT WHAT
# FOLLOWS IT: after a one-argument FENCE succeeds, an alternation, an ARBNO or an ARB to its RIGHT is still retried when a
# later element fails, exactly as SPITBOL does (hq_snocone 2026-09-27, found under the Snocone and Pascal self-hosted parsers;
# Lon 2026-09-27: "Get the parser_*.sc programs to 100%.").
#
# MECHANISM, measured by ASM-DIFF between a passing and a failing sibling in one mode: src/lower/lower_snobol4.c's TT_SEQ
# lowering builds a fenced sequence RIGHT TO LEFT and, after building FENCE1, re-routes the right-hand run's failure exit into
# the FENCE's beta through right_tail. For a MULTI-element run right_tail held the run's LAST element (its resume node), so the
# last element's omega jumped straight to match_fence1_beta and every alternative between the FENCE and it was skipped:
#     'xabc' ? FENCE('x') ('a' | 'ab') 'c'          SPITBOL succeeds, SCRIP failed in m3 and m4.
# And TT_ARBNO takes its body range (operands 1 and 2, which the emitter scans for the body's tail beta) as the first and the
# last node BUILT, which for a right-to-left fenced body is the wrong end, so resuming an iteration fell to the body's FIRST
# element instead of the inner ARBNO that could grow:
#     '{c:bb}' ? POS(0) '{' ARBNO('c' FENCE('') ':' ARBNO('b')) '}' RPOS(0)       SPITBOL succeeds, SCRIP failed.
# CURE: right_tail is the run's FIRST element for a multi-element run; the fenced TT_SEQ publishes the last node built for its
# rightmost segment with the entry it returns, and ARBNO uses it (entry and that node) when the entry is its own body's.
# STILL OPEN, not armed here (with the cto): ARBNO(P) with the fenced sequence held in a VARIABLE (a PAT$ graph whose fenced
# body root meets the zeta seam-tier check): P1 = 'c' FENCE('+' | '') ':' ARBNO('b'); '{c:bb}' ? POS(0) '{' ARBNO(P1) '}' RPOS(0).
#
# ARMS: (1) mode 3 and (2) mode 4 run one witness program of ten statements, each printing a YES or NO line; the ref is CUT FROM
# THE ORACLE at run time and every line must match byte for byte. Two control lines (no FENCE; nested ARBNO without a FENCE)
# were green before the cure and must stay green.
"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/util_require_fresh.sh" --gate "$(basename "${BASH_SOURCE[0]}" .sh)" || exit $?
set -uo pipefail
G="$(basename "${BASH_SOURCE[0]}" .sh)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
SCRIP="${SCRIP_BIN:-$ROOT/scrip}"; [ -x "$SCRIP" ] || { echo "⛔ GATE REFUSE(2) [$G]: no scrip at $SCRIP"; exit 2; }
LIBDIR="$ROOT/out"; [ -f "$LIBDIR/libscrip_rt.so" ] || { echo "⛔ GATE REFUSE(2) [$G]: no libscrip_rt.so in $LIBDIR"; exit 2; }
SBL="${SBL_BIN:-/home/resources/x64/bin/sbl}"; [ -x "$SBL" ] || { echo "⛔ GATE REFUSE(2) [$G]: no sbl at $SBL -- this gate's ref is CUT FROM THE ORACLE at run time, never typed"; exit 2; }
T=$(mktemp -d) || exit 2; trap 'rm -rf "$T"' EXIT
cat > "$T/w.sno" <<'EOF'
        'xabc' ? FENCE('x') ('a' | 'ab') 'c'                                  :S(Y1)
        OUTPUT = 'NO  1 FENCE(x) (a|ab) c'                                     :(W2)
Y1      OUTPUT = 'YES 1 FENCE(x) (a|ab) c'
W2      'xab' ? FENCE('x') ('a' | 'ab') RPOS(0)                              :S(Y2)
        OUTPUT = 'NO  2 FENCE(x) (a|ab) RPOS(0)'                               :(W3)
Y2      OUTPUT = 'YES 2 FENCE(x) (a|ab) RPOS(0)'
W3      'xybb' ? FENCE('x') 'y' ARBNO('b') RPOS(0)                            :S(Y3)
        OUTPUT = 'NO  3 FENCE(x) y ARBNO(b) RPOS(0)'                           :(W4)
Y3      OUTPUT = 'YES 3 FENCE(x) y ARBNO(b) RPOS(0)'
W4      'xybb' ? 'x' FENCE('') 'y' ARBNO('b') RPOS(0)                         :S(Y4)
        OUTPUT = 'NO  4 x FENCE() y ARBNO(b) RPOS(0)'                          :(W5)
Y4      OUTPUT = 'YES 4 x FENCE() y ARBNO(b) RPOS(0)'
W5      'xybb' ? FENCE('x') 'y' ARB RPOS(0)                                   :S(Y5)
        OUTPUT = 'NO  5 FENCE(x) y ARB RPOS(0)'                                :(W6)
Y5      OUTPUT = 'YES 5 FENCE(x) y ARB RPOS(0)'
W6      P = FENCE('x') 'y' ARBNO('b') RPOS(0)
        'xybb' ? P                                                            :S(Y6)
        OUTPUT = 'NO  6 the same pattern held in a variable'                  :(W7)
Y6      OUTPUT = 'YES 6 the same pattern held in a variable'
W7      '{c:bb}' ? POS(0) '{' ARBNO('c' FENCE('') ':' ARBNO('b')) '}' RPOS(0) :S(Y7)
        OUTPUT = 'NO  7 ARBNO body c FENCE() : ARBNO(b)'                       :(W8)
Y7      OUTPUT = 'YES 7 ARBNO body c FENCE() : ARBNO(b)'
W8      'c:bb' ? POS(0) 'c' FENCE('+' | '') ':' ARBNO('b') RPOS(0)            :S(Y8)
        OUTPUT = 'NO  8 c FENCE(+|) : ARBNO(b) RPOS(0)'                        :(W9)
Y8      OUTPUT = 'YES 8 c FENCE(+|) : ARBNO(b) RPOS(0)'
W9      'xab' ? 'x' ('a' | 'ab') RPOS(0)                                      :S(Y9)
        OUTPUT = 'NO  9 control: no FENCE'                                     :(W10)
Y9      OUTPUT = 'YES 9 control: no FENCE'
W10     'abb' ? POS(0) ARBNO('a' ARBNO('b')) RPOS(0)                          :S(Y10)
        OUTPUT = 'NO  10 control: nested ARBNO, no FENCE'                      :(END)
Y10     OUTPUT = 'YES 10 control: nested ARBNO, no FENCE'
END
EOF
( cd "$T" && timeout 20s "$SBL" -bf w.sno </dev/null ) > "$T/w.ref" 2>&1 || { echo "⛔ GATE REFUSE(2) [$G]: the oracle refused its own witness -- no ref to grade against"; exit 2; }
[ "$(grep -c '^YES' "$T/w.ref")" = 10 ] || { echo "⛔ GATE REFUSE(2) [$G]: the oracle's ref does not read ten YES lines -- the witness is not the one this gate was minted on"; exit 2; }
RC=0
got="$(timeout 20s "$SCRIP" "$T/w.sno" </dev/null 2>&1)"
if [ "$got" = "$(cat "$T/w.ref")" ]; then echo "  m3 PASS (10/10 lines byte-identical to the oracle)"
else echo "  m3 FAIL (diverged from the oracle on: $(diff <(echo "$got") "$T/w.ref" | grep '^<' | cut -c3- | tr '\n' '|'))"; RC=1; fi
if "$SCRIP" --compile "$T/w.sno" -o "$T/w.s" </dev/null >/dev/null 2>&1 && gcc -m64 -no-pie -rdynamic "$T/w.s" -Wl,-rpath,"$LIBDIR" -L"$LIBDIR" -lscrip_rt -lm -lpthread -o "$T/w" 2>"$T/ld.log"; then
    got4="$(timeout 20s "$T/w" </dev/null 2>&1)"
    if [ "$got4" = "$(cat "$T/w.ref")" ]; then echo "  m4 PASS (10/10 lines byte-identical to the oracle)"
    else echo "  m4 FAIL (diverged from the oracle on: $(diff <(echo "$got4") "$T/w.ref" | grep '^<' | cut -c3- | tr '\n' '|'))"; RC=1; fi
else echo "⛔ GATE REFUSE(2) [$G]: mode-4 compile or link failed, so arm 2 measured nothing"; exit 2; fi
if [ "$RC" = 0 ]; then echo "✅ GATE PASS(0) [$G]: what follows a FENCE is retried as SPITBOL retries it, flat and inside an ARBNO body, in both modes (2 arms, 10 witnesses)"
else echo "⛔ GATE FAIL(1) [$G]: a FENCE cut more than its own argument (examined 2 arms, 10 witnesses)"; fi
exit $RC
```

## The statement-level delta-debug of a parser (scratch tool, for the switch row)

```python
#!/usr/bin/env python3
"""dd_grammar.py PARSER.sc WITNESS OUT.sc -- shrink a bootstrap parser by whole statements while SPITBOL still parses the
witness (a tree line) and SCRIP m3 still refuses it (Parse Error), both through the transpiled chain. hq_snocone 2026-09-27."""
import subprocess, sys, os, re, tempfile
SCRIP = '/home/claude_snocone/SCRIP/scrip'
SBL = '/home/resources/x64/bin/sbl'
BOOT = '/home/claude_snocone/SCRIP/bootstrap'
CHAIN = ['global', 'case', 'assign', 'match', 'counter', 'stack', 'tree', 'ShiftReduce', 'tdump', 'gen', 'qize', 'semantic', 'omega', 'trace']
src, witness, out = sys.argv[1], sys.argv[2], sys.argv[3]
tmp = tempfile.mkdtemp(prefix='ddg.')
def stmts(text):
    """split into top-level statements: a statement ends at a ';' at line end outside strings and comments, or is a comment line"""
    out, cur = [], []
    for line in text.split('\n'):
        cur.append(line)
        s = re.sub(r"'[^']*'|\"[^\"]*\"", '', line)
        s = re.sub(r'/\*.*?\*/', '', s)
        if s.rstrip().endswith(';') or s.strip().startswith('/*') and s.strip().endswith('*/') or not s.strip():
            out.append('\n'.join(cur)); cur = []
    if cur: out.append('\n'.join(cur))
    return out
def reproduces(parts):
    p = os.path.join(tmp, 'p.sc'); open(p, 'w').write('\n'.join(parts) + '\n')
    sno = os.path.join(tmp, 'p.sno')
    with open(sno, 'w') as f:
        r = subprocess.run([SCRIP, '--transpile'] + [os.path.join(BOOT, c + '.sc') for c in CHAIN] + [p], stdout=f, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    if r.returncode != 0: return False
    try:
        a = subprocess.run([SBL, '-bf', '-s2000m', '-d4000m', sno], stdin=open(witness, 'rb'), capture_output=True, timeout=60).stdout.decode('latin-1')
        b = subprocess.run([SCRIP, '-s4096m', '-d16384m', sno], stdin=open(witness, 'rb'), capture_output=True, timeout=60).stdout.decode('latin-1')
    except subprocess.TimeoutExpired:
        return False
    sbl_tree = any(l.startswith('(') for l in a.splitlines()) and 'Parse Error' not in a
    scr_ref = 'Parse Error' in b
    return sbl_tree and scr_ref
parts = stmts(open(src).read())
assert reproduces(parts), 'the full parser does not reproduce the divergence'
n = 2
while len(parts) >= 2:
    chunk = max(1, len(parts) // n); removed = False
    for i in range(0, len(parts), chunk):
        trial = parts[:i] + parts[i + chunk:]
        if trial and reproduces(trial):
            parts = trial; n = max(n - 1, 2); removed = True
            print('kept %d statements' % len(parts), flush=True); break
    if not removed:
        if chunk == 1: break
        n = min(len(parts), n * 2)
open(out, 'w').write('\n'.join(parts) + '\n')
print('minimal: %d statements -> %s' % (len(parts), out))
```
