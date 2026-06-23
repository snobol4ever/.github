# HANDOFF — 2026-06-23 — Claude — Icon scan builtins accept cset-keyword args

## One-line: any/many/upto now accept &lcase/&ucase/&letters/&digits (not just IR_LIT_S literal csets) in modes 3+4; verified end-to-end. Suite UNCHANGED 144/283. SCRIP pushed `66de67e`.

**Repos:** SCRIP `66de67e` (pushed). .github (this handoff + GOAL-ICON-BB.md watermark).

---

## What landed

The scan-builtin excision gate and emitter dispatch required an `IR_LIT_S` literal
string for the cset argument of any/many/upto, so a keyword cset like `any(&lcase)`
forced a clean EXCISE even though the value is a compile-time constant. Per canonical
`refs/icon-master/src/runtime/fstranl.r`, any/many/upto take a cset arg (c).

Three files, +37/-5:

1. **`src/runtime/keywords.c` / `keywords.h`** — `kw_cset_const_str(kw)` returns the
   canonical string for the printable csets (`lcase`/`ucase`/`letters`/`digits`) for
   compile-time use by the gate and emitter. `&ascii`/`&cset` are deliberately NOT
   covered (their canonical form carries a leading NUL, which `strchr`-based membership
   in the templates can't represent) → they continue to cleanly EXCISE.

2. **`src/driver/scrip.c`** — `scan_fn_cset_arg(nd)` accepts an `IR_LIT_S` literal OR a
   known cset-keyword arg. Wired into `scan_subgraph_safe` (any/many/upto) and
   `scan_tab_arg_ok`. `match`/`find`/`bal` keep `IR_LIT_S` (they take STRING args s1),
   split into their own gate branches.

3. **`src/emitter/emit_bb.c`** — `scan_cset_or_lit_arg(nd)` extracts either the literal
   string or the keyword-cset constant; used for ANY (cset)/MANY/UPTO dispatch. MATCH
   keeps `IR_LIT_S` (it's a `memcmp` string compare, not cset membership).

**Templates are UNCHANGED** — `bb_scan_any/many/upto` already read only `_.op_name1`
and seal it as RO data. The keyword's constant string flows into `op_name1` exactly
like a literal cset would; the box cannot tell the difference. (PER-BOX LOCAL STORAGE
+ language-blind-template rules honored: no language logic added to any template; the
cset-name→string mapping lives in the runtime/keywords + the lowerer-adjacent gate.)

## Verification (both modes, end-to-end)

- m3: `any(&lcase)`→2, `many(&lcase)`→6, `upto(&lcase)`→1 (correct Icon semantics).
- m4: same source → `--compile` → `as` → `gcc -lscrip_rt` → run → `1` (matches m3).
- Regression: `match("ab")`→3, `find("o")`→5, `any('a')` literal cset→2 unchanged.
- Rung suite 144/283 m3==m4 UNCHANGED. icon smoke 12/12 m3+m4; prolog 5/5 m3+m4.
- no-stack gate 0; one-reg gate 0; semicolon prison green.
- `CHECK=1 update_icon_bench_asm.sh`: no drift (new=0 updated=0) — change is invisible
  to the 13 benchmarks because none use the bare cset-keyword scan form yet.

## Why the suite number didn't move — and the REAL next lever

No rung test and none of the 8 SMX-blocked benchmarks use a BARE `s ? upto(&cset)`.
They use **`tab(upto(&cset))`** / `tab(many(&cset))` — `tab` WRAPPING A GENERATOR.

Traced this session: in `src/lower/lower_icon.c` (~lines 85-95), a call whose argument
is `is_resumable` (a generator) takes the `chains=1` path → `IR_LIT(call).dval = 1.0`
and threads its arguments as a CHAINED producer sequence. It does NOT take the
`subgraph` path (`dval=3.0`) that the scan-retag pass (`icn_retag_scan_body`, requires
`dval==3.0`) converts into `IR_SCAN_TAB`. So `tab(upto(...))` stays as
`IR_CALL sval="tab" dval=1.0` with `upto` as a chained generator producer — the
per-`IR_SCAN_TAB`-box path never fires, and the gate rejects it at
`scan_tab_arg_ok` (sees `dval=1` not `3`).

**This is the single blocker for concord/deal/ipxref/micsum/post/queens/shuffle/tgrlink.**
It needs the chained-call-with-scan-producer driver (flat-chain scan path), which is a
substantially larger piece than this gate widening. Recommended as the next dedicated
session, with full context — it touches `flat_drive_*` in emit_bb.c and the lowerer's
chained-call shape.

## Standing items (unchanged from prior handoff)
The 14 open FAILs (bb_call FATAL cluster, rung02 recursion, rung03 suspend, rung14
limit counter, rung13 cross-arg) and the smaller wins (`rt_size_d` `*L` list-size,
dv=1.0 userproc routing for rung32, bb_limit counter) are all still on the board.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
