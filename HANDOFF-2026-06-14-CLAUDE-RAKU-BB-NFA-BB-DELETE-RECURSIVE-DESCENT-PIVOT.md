# HANDOFF 2026-06-14 — Raku: DELETE all NFA-BB; pivot to traditional recursive descent

## Session: GOAL-RAKU-BB. Directive from Lon: an NFA is the wrong primary engine for a top-down recursive-descent language → DELETE the entire NFA-on-Byrd-boxes apparatus; KEEP the C NFA matcher for plain regex.

**SCRIP HEAD at open: `448f529`. Local commits this session (PENDING PUSH — see push notes):**
- `69e232b` — Raku smoke: lock `$<name>` capture path (m2 PASS / m3/m4 clean EXCISE).
- `d63c374` — Raku: DELETE all NFA-BB.

**`.github` local commits (PENDING PUSH, push LAST):**
- `e23b9703` — drop deleted `test_gate_raku_nfa_oracle.sh` from Session Setup gate list.
- `4dfc4602` — GOAL-RAKU-BB pivot to recursive descent (priority block + obsoleted rungs + watermark).
- (this doc) — add on commit below.

**Gates at close — Raku m2 38/38 (HARD ✓); m3 35 PASS / 0 FAIL / 3 EXCISED; m4 same.** Peers invariant:
Icon m2/m3/m4 12/12/12, SNOBOL4 m4 7/7. `g_vstack`=0, `bb_bin_t`=0, **IR_NFA residual=0**. The 5 pre-existing
`audit_concurrency_invariants.sh` VIOLATIONs (stale `src/lower/lower.c` path + LOWER/EMITTER FACT md5 drift in
GOAL-ICON/PROLOG) and the 1 `util_template_purity_audit.sh` site (`bb_call_write_slot.cpp`) are UNCHANGED — a
`git stash`-equivalent baseline; NOT introduced here.

---

## WHY (the verdict, grounded in Rakudo/NQP internals + the code)

An NFA recognizes exactly the **regular** languages. Raku is a PEG/recursive-descent formalism (S05: "natively
implements Parsing Expression Grammars … as an extension of regular expression notation"). Subrule `<name>`
calls give **self-recursion** (Raku supports it) → at least context-free → **provably beyond any finite
automaton**. In real Rakudo the matcher **is** recursive descent: a backtracking **Cursor** machine + bstack;
the NFA is ONLY an LTM-dispatch oracle (`nfarunproto`/`nfarunalt`) that prunes/orders alternation+proto
candidates and does **zero** consuming or capturing. An engine is fully correct with no general NFA (the old
PGE engine matched Raku regex with only literal-prefix dispatch). The repo's `gram_expand` (flatten every
`<subrule>` into ONE NFA string, then `nfa_exec`) is a **non-recursive stopgap** — proven by the code: hard
`depth < 16` cap + fixed `pat[4096]` buffer in `by_name_dispatch.c`; a self-recursive rule overflows/caps out =
wrong. Flat grammars (the 4 grammar smoke tests) work; recursive grammars do not.

The greedy-capture bug (`12abc` → `"1"/"2abc"` not `"12"/"abc"`) is a structural symptom: a parallel NFA
returns *a* valid split, not the greedy leftmost-longest submatch a backtracking descent produces by
construction.

---

## WHAT WAS DELETED (`d63c374`) — the whole NFA-on-Byrd-boxes track

- **`IR_NFA_*` IR kinds** (all 11: CHAR/ANY/CLASS/SPLIT/EPS/BOL/EOL/CAP_OPEN/CAP_CLOSE/ACCEPT/MATCH) — removed
  from `src/contracts/IR.h` enum and the `src/contracts/scrip_ir.c` name table.
- **`nfa_to_bb` / `nfa_bb_exec` / `nfa_bb_graph_exec`** and the file **`src/parser/raku/nfa_bb.c`** (git rm) +
  their decls in `src/parser/raku/re.h` + the `Makefile` `RT_PIC_SRCS` line and compile rule.
- **`RK_NFA_BB` env dispatch** — two sites in `by_name_dispatch.c` and one in `IR_interp.c`, each
  `if (nfa_bb) nfa_bb_exec(...); else nfa_exec(...)` collapsed to just `nfa_exec(...)` (the C matcher).
- **`IR_NFA_MATCH` interp case** in `IR_interp.c` (deleted) + its **`bb_reset` counter-preserve exemption** in
  `scrip_ir.c`.
- **`scripts/test_gate_raku_nfa_oracle.sh`** (git rm) — its only reason to exist was validating NFA-BB == C-NFA.
- **`lower_raku.c` `TT_SMATCH` value-arm** — the `IR_NFA_MATCH` branch removed; `~~ /literal/` now always
  lowers to the plain `re_match` IR_CALL (dval=2) path that was already the fallback.
- **`scrip.c`** — `IR_NFA_MATCH` removed from `rhs_kind_ok`, `assign_safe_kind`, and the EXCISE guard. The
  guard line was REPLACED with a clean dval==2 regex-call excise (see next section).

## WHAT WAS KEPT (Lon directive 2026-06-14)

**The C NFA matcher `src/parser/raku/re.c`** (`nfa_build` / `nfa_exec` / `Nfa` / `Match`) — this is the regex
engine for `~~ /regex/` and the interim m2 grammar matcher (via `gram_expand`). It is NOT "NFA-BB"; it is the
runtime regex matcher and carries m2 regex+grammar today. Do not delete it until/unless the recursive-descent
engine replaces grammar matching AND a decision is made about regex.

---

## THE ONE SUBTLE FIX (read before touching the m3/m4 excise gate)

With `IR_NFA_MATCH` gone, `~~ /regex/` reverts to `re_match` (IR_CALL dval=2). That dval=2 descr-chain arm is
**not** a blanket bomb — `bb_call_route_classify` (`emit_bb.c`) routes `dval==2 && rt_builtin_is_known(fn)` to
`CALL_ROUTE_BYNAME` (NATIVE), and only `dval==2 && !known && !__rk_bool` to `CALL_ROUTE_DVAL2_BOMB`. The
`known[]` list in `by_name_dispatch.c::rt_builtin_is_known` CONTAINS `array_sort`/`arr_get`/`hash_get`/`elems`/
`reverse`/`sort`/`push_pure`/… (so array/hash/string builtins emit natively) but does **NOT** contain
`re_match`/`re_capture`/`re_named_capture`/`re_match_global`/`fh_capture` (so those bomb).

The new gate guard in `graph_native_emittable_mode` (`scrip.c`) therefore mirrors the bomb predicate EXACTLY:
```c
if (nd->op == IR_CALL && IR_LIT(nd).dval == 2.0 && IR_LIT(nd).sval
    && strcmp(IR_LIT(nd).sval,"__rk_bool") && strcmp(IR_LIT(nd).sval,"__rk_try")
    && !rt_builtin_is_known(IR_LIT(nd).sval)) return 0;   /* clean EXCISE, never bomb */
```
(`extern int rt_builtin_is_known(const char*)` declared at the top of the function.) This excises ONLY the
regex/capture family; array/hash/string/jct/obj builtins (known) still emit natively. **MISTAKE TO AVOID
(I made it first, then fixed):** a broad `dval==2 && !__rk_bool/__rk_try` guard WITHOUT the `!rt_builtin_is_known`
clause over-excises 10 working builtin tests (array_sort/hash_set_get/str_reverse/say_list/… flip PASS→EXCISE).
The `rt_builtin_is_known` clause is load-bearing.

---

## NEXT RUNG — RK-GRAM-3 (THE SEAM): the recursive-descent grammar engine (LEAD)

Build subrule `<name>` recursion + backtracking on the EXISTING four-port box-resumption substrate — the
SNOBOL4 pattern boxes `bb_match_*`/`bb_pattern_*` ARE a backtracking recursive-descent matcher:
- γ = matched / advance-cursor; ω = fail / redo.
- alternation (`|`/`||`) = `IR_ALT` (the proven `bb_match_alt.cpp` / `bb_pattern_alt.cpp` choice point).
- subrule call = recursion into another box graph (rides the C call stack + the Prolog-style choice-point
  ledger `g_resolve_bfr`/`resolve_choice` — both explicitly KEPT by the NO-VALUE-STACK rule; **NOT** a value
  stack, **NOT** a flattened NFA).
- the Σ/δ/Δ subject triad (R13/R14/R15) reserved for the regex slab IS the cursor.

This REPLACES `gram_expand`'s flatten-to-NFA for recursive grammars and builds a real Match tree, then
`$<name>`/`$0` capture access. Grammar registration + `.parse` dispatch already landed (`f3b1837`); regex `~~`
stays on the kept C matcher `re.c`. **NEEDS FULL BUDGET + read `ARCH-x86.md` AND `ARCH-SCRIP.md` first**
(MODE3/4-EMIT work). Deliberately NOT started this session (closed at ~63% after the deletion).

Obsoleted rungs (marked `[x] OBSOLETE` in the ladder): RK-NFA-4 (native NFA boxes), RK-NFA-5 (BB greedy),
RK-NFA-CONV (IR_NFA_* ↔ IR_PAT_* convergence) — all referenced the deleted NFA-BB track.

---

## ⚠ PUSH NOTES (the bare `git push origin main` failed for prior sessions — use the token URL)

```bash
cd /home/claude/SCRIP
git fetch origin && git pull --rebase origin main      # peers may be ahead; resolve, then rebuild + re-gate
rm -f scrip && make -j4 scrip && make libscrip_rt       # MUST rebuild BOTH after any rebase
bash scripts/test_smoke_raku.sh                         # m2 38/38; m3/m4 35+3X
bash scripts/test_smoke_icon.sh ; bash scripts/test_smoke_snobol4.sh
git push https://<TOKEN>@github.com/snobol4ever/SCRIP main
# THEN .github LAST:
cd /home/claude/.github
git pull --rebase origin main
git push https://<TOKEN>@github.com/snobol4ever/.github main
# Confirm in each: git log origin/main --oneline -1   shows your hash.
```

## Session Setup (next session)
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
rm -f scrip && make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_raku.sh      # m2 38/38 HARD; m3/m4 35 PASS / 3 EXCISED
bash scripts/test_smoke_icon.sh      # 12/12/12 HARD
bash scripts/test_smoke_snobol4.sh   # m4 7/7 HARD
# (test_gate_raku_nfa_oracle.sh is GONE — do not look for it.)
```

## Commits this session
| Commit | Repo | What |
|---|---|---|
| `69e232b` | SCRIP | Raku smoke: lock `$<name>` capture path (m2 PASS / m3/m4 clean EXCISE) |
| `d63c374` | SCRIP | DELETE all NFA-BB; revert `~~` to `re_match`; narrowed clean dval=2 excise |
| `e23b9703` | .github | drop deleted oracle gate from Session Setup |
| `4dfc4602` | .github | GOAL-RAKU-BB pivot to recursive descent |
| (this doc) | .github | handoff |
