# HANDOFF 2026-06-04 OPUS48 — Pascal BB: LB-3 + LB-FENCE closed · PB-9e-0 + design

**Goal:** `GOAL-PASCAL-BB.md`. **Repos:** SCRIP (`f4a7187`; LB-3 = `95fdc2f`), corpus (`10940fd`),
`.github` (watermark + LB-3/LB-FENCE/PB-9e-0 `[x]` + this file). PLAN.md untouched (routine handoff).
Hashes are POST-REBASE (pull onto concurrent ICN-SCAN-7 + PB-RB work; pre-rebase LB-3 `780de9f`, design
`fa08c4e`): gates re-verified at merged HEAD `f4a7187` — SNOBOL4 19/0, Pascal m2 37/0/1, m3 probes PASS.

Three things landed; one design held for Lon's fork call.

---

## 1. LB-3 — DEFINE name-gate ELIMINATED (SCRIP `95fdc2f`)

Done re-route-FIRST per the directive, so **the named gate never moved** (SNOBOL4 smoke 19/0: m2 7/0
HARD, m3 6/6, m4 6/6 — byte-identical pre/post; not even the survivable 5/5 floor was paid).

Mechanism: `IR_CALL dval=5.0` is the define IR shape, tagged by LOWER (`lower.c` SNO TT_FNC arm — the
one place name knowledge is sanctioned, the same boundary PB-9a drew for `__pas_*`). Six single-line
shape-only edits: producer (lower.c), m2 interp generic arm (`IR_interp.c:1938`), flat-chain driver FILL
route (`emit_bb.c:1751`), chain-arity arity-0 (`emit_bb.c:2172` — the 591ed37 RETURN-class clobber
pre-empted), nested-call marshal (`bb_call.cpp:82`), and the dispatch itself (`bb_call.cpp:311`) where
`strcmp(fn,"DEFINE")` is **deleted outright** — the violating snippet no longer exists, nothing left to
abort. Tier-1 audit item 3 closed.

Drift-proofing (the stash→rebuild→diff method): Snocone smoke 2/3 and Prolog smoke m3 `unify` FAIL are
**stash-proven pre-existing** at the clean baseline; lang-names gate output **byte-identical** pre/post
(its exit-1 hits are the LB-7-NEW ICN-SCAN `emit_core.c` sites, concurrent-session-owned, do not touch).

## 2. LB-FENCE — CLOSED

Tier-1 grep over `BB_templates/` + `XA_templates/` == **0**. Full matrix pinned at `95fdc2f` (Pascal ·
Icon · Prolog · SNOBOL4 · Raku · all-langs m4 hello — exact numbers in the goal-file watermark). Every
LB-1..8 delta accounted: the single measured delta remains raku m4 `str_reverse` (LB-1), re-confirmed
identical this session (raku 25/0 · 1/1/23 · 1/1/23). The LANGUAGE-BLIND FACT RULE's completion test is
green. LB-7-NEW stays open by design (Tier-2-class strings, ICN-SCAN-owned).

## 3. PB-9e-0 — the discriminator probe (corpus `10940fd`)

`nestshadow.pas`: sibling-calls-sibling through a shadowing local (`outer{x; p2{x:=x+100}; p1{x;
x:=7; p2; writeln(x)}; x:=1; p1; writeln(x)}`). pcom-accepted (in-subset). Oracle **7/101**; m2 PASS
(suite 36→**37/0/1**); m3 **107/107** expected-fail pinned. The structural point: deepening the current
param-style NV save/restore to locals is *dynamic-chain* semantics — it would fix `nestrec` but can
NEVER fix `nestshadow` (p2 would read p1's seated cell). The static-link model is forced, not preferred
— the watermark's "not more NV flattening" made into a failing gate.

## 4. PB-9e — DESIGNED, build held (SCRIP `f4a7187`, `SCRIP/PB-9E-DESIGN.md`)

Traced, not assumed: `rt_call_named_proc` (rt.c:515) already hands every activation a frame block `fb`
from the depth arena and enters the compiled body `p->fn(fb,0)`; params are shallow-NV
(`rt_name_save_push`), **Pascal locals are bare NV** — the whole gap. The m2 mirror (`GenFrame`,
`static_link = pas_base(caller, caller_lvl − decl_level)`, `IR_interp.c:1815-2070`) yields the key
emit-time fact: **both levels are lexical constants**, so every mode-3/4 SL computation and uplevel
access compiles to an emit-time-constant chain of `[base+0]` hops — pure port-chasing, no display, no
runtime level bookkeeping, no name search. `[fb+0]` = static link (the parent-port thread made
addressable); `[fb+16+k*16]` = `lower_sc`-ordered param/local DESCRs; new language-blind shapes
`IR_VAR_FRAME`/`IR_ASSIGN_FRAME` (`ival`=slot, `dval`=hops); funcname-return stays NV (smallest blast
radius); var params = SlotRef flattened to a cell address at PB-9e-2.

**Fork points awaiting Lon (then PB-9e-1 is turn-key):**
- **A. Migration scope:** nested-only (flat gates untouched by construction) vs uniform.
  Recommend nested-only first, LB-3-style move-the-gate-last.
- **B. Runtime signature:** explicit `rt_call_named_proc_sl(name,args,nargs,void *sl)` vs in-band
  `args[np]`. Recommend explicit.

## Gotchas / environment notes for the next session

- `out/libscrip_rt.so` was missing in the fresh container — `make libscrip_rt` restores it; without it
  every m4 smoke reports `<mode4-build-failed>`. Run it right after `make scrip`.
- `fpc` install: plain `apt-get install fpc` 404s on a stale lzma dep — run `apt-get update` first,
  then install; `fpc -h` works but `fpc --version` errors (harmless).
- `pcom` prints the source listing to **stdout** — discard it (`./pcom < p.pas > /dev/null`) before
  `cp prr prd && ./pint < /dev/null`, or oracle diffs are garbage.
- Pascal suite count is now 37/0/1 (ppp.pas included; +nestshadow; XFAIL=recursion fact-8 16-bit).
- Session-13 full-corpus pins (Icon 130/117/36, Prolog honest 136/0/0) were NOT re-run this session —
  smokes only; re-pin them when next touched.

## Build / verify

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip && make libscrip_rt
apt-get update -qq && apt-get install -y fpc
( cd /home/claude/corpus/programs/pascal && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas )
bash scripts/test_smoke_snobol4.sh        # 19/0
# PB-9e gates: nestrec + nestshadow vs oracle (m3 fails today by design — that IS the rung)
```
