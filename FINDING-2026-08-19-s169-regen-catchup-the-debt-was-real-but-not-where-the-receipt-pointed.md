# FINDING s169 (seat2) — regen-catchup: the artifact debt was REAL, but NOT where the receipt pointed

**Queue row 2 `regen-catchup`.** Brief: *283/340 tracked `.s` stale (seat3 receipt); RULES step-4 debt
from B2a-era onward.* First step: pristine build at HEAD, run all `util_regen_*_s_artifacts.sh`, ONE
regen commit per repo. DONE-WHEN: regen commits pushed + FINDING attributing the deltas to their eras.

**Landed:** corpus `0f0a8144` — 433 files, ONE commit, pushed. SCRIP: **no commit — nothing was stale.**

---

## 1. The headline: the debt was in `programs/`, not in `crosscheck/`

Pristine build at HEAD (`make pristine`, SCRIP `25d8970c`, RT_OPT at the `-O0` default per O2-DIRECTED-ONLY),
then every regen script. What the sweep measured:

| tree | script | emitted | **changed** | already current |
|---|---|---|---|---|
| `programs/{icon,prolog,rebus}` | `util_regen_programs` | 623 | **404** | 219 |
| `benchmarks/prolog/bench` | `util_regen_prolog_bench` | 22 | **19** | 0 |
| `benchmarks/icon` | `update_icon_bench_asm` | 20 | **10** | 10 |
| `crosscheck` | `util_regen_crosscheck` | 484 | **0** | **484** |
| `benchmarks/snobol4` | `util_regen_benchmark` | 24 | **0** | 24 |
| `programs/snobol4/demo` | `util_regen_demo` | 21 | **0** | 21 |
| `test/snobol4` (SCRIP) | `util_regen_feature` | 154 | **0** | 154 |

**Crosscheck is not part of the debt, and was not at the moment the row was written.** Seat3's
283/340 was paid by `f5538e01` *"crosscheck x86 .s artifacts: CN-14 constant fold + stale PAT$ road"*
— **414 files, 2026-08-19 18:14**, roughly an hour before this seat locked the row. All 484 crosscheck
artifacts now re-emit **byte-identical**.

## 2. The receipt's cited mechanism does not reproduce at HEAD

The receipt named a witness: *"`crosscheck/rungW02/W02_seq_basic.s` carries a `__gva_names` rodata
section current output does not emit."* Measured at pristine HEAD:

```
checked-in W02_seq_basic.s : __gva_names present (2 occurrences)
fresh --compile at HEAD    : __gva_names present (2 occurrences)  -> BYTE-IDENTICAL
before f5538e01            : __gva_names present (2)   after: present (2)
```

`__gva_names` was there before that commit and after it, and it is there now. The mode-4 emission site
(`src/driver/scrip.c:1487/1553`) is gated only on `n_gva = gva_count() > 0` — **no `MONITOR_BIN` gate on
the mode-4 path**; the `MONITOR_BIN ⇒ n_gva=0` override exists only on the two *mode-3* paths
(`:1611`, `:1759`). So a GVA-suppressed `.s` cannot come from the shipped mode-4 compiler.

**This does not void the receipt's count** — `W02_seq_basic.s` genuinely *was* stale (f5538e01 rewrote it
53+/135−). What it voids is the *mechanism*: the drift seat3 saw was not "HEAD stopped emitting GVA names",
so `__gva_names` is not a marker anyone should navigate by. The number was right, the cause named for it
was a property of the measuring build. **Seat3's refusal to fold the sweep into its FENCE commit remains
correct** — the debt was real, it just wasn't the class the witness suggested.

## 3. The deltas by era — the debt is a STACK, not one era

Every changed byte in `0f0a8144` decomposes into seven symbol-level classes, each pickaxed to the SCRIP
commit that introduced it:

| delta class | count | introduced by | era | date |
|---|---|---|---|---|
| 7× `rt_proc_set_{nparams,nformals,jmpentry,fn,frame_bytes,generator,dcfn}` → 1× `rt_proc_register_rec` | 2024 sites | `988aad0f` | ONE-REG s119 | 2026-08-16 |
| `rt_nret_fix` → `rt_nret_fix_tiny` | 3944 | `ba53a207` | R-2 TINY RECORD ENTER s104 | 2026-08-15 |
| `proc_<name>_dc` → `<name>_dc` (routing prefix dropped) | ~400 | `d0c122fd` | PROC-PREFIX-DROP s119 | 2026-08-16 |
| `proc_startup` → `module_init` | 285 | `a8dfff51` | SN4-MODULE-INIT s125 | 2026-08-16 |
| `str_concat_d` → `str_concat_fracdigit_d` | 184 | `4a8880c5` | ICN-CONCAT-CONV s240 | 2026-08-16 |
| `+ rtcc_load_all` | 19 | `129dbb06` | RC-4 CLAIM THE ARG TIER | 2026-08-08 |
| `+ rt_faildescr`, gen-spine resume entries | 117 | `4e84e986` / `9b50f004` | NCB-1b / GENP-SPINE s92 | 2026-07-11 |

**The oldest era in the debt is 2026-07-11.** `programs/` and `benchmarks/prolog` went **five weeks**
without a step-4 sweep — not "B2a-era onward" but considerably further back. The reason is structural, not
neglect: RULES step 4 names `util_regen_benchmark` · `util_regen_feature` · `util_regen_demo` (+
`update_icon_bench_asm` for Icon), and **`util_regen_programs` and `util_regen_prolog_bench` appear in no
step of the handoff sequence at all.** The two trees nobody was told to sweep are exactly the two that
accumulated five weeks of drift. The three trees step 4 names UNCONDITIONALLY — benchmark · feature · demo —
were all current before this seat ran. The fourth it names CONDITIONALLY (`update_icon_bench_asm`, fired only
"if the session touched the Icon emitter/lowerer") had **10 of 20 stale**: a condition on a sweep is doing the
same work as an omission, because the sessions that drift a tree are rarely the sessions that sweep it.

⭐ **`util_regen_prolog_bench_s_artifacts.sh` writes but NEVER COMMITS.** It has no git section; its 19
rewritten `.s` sat unstaged in the worktree. Any seat that ran it and then ran `git status` filtered to its
own lane would have left them behind — a silent contributor to this tree's drift. Its five siblings all
stage and commit. Fixing it is a one-block change, not done here (out of lane).

## 4. What did NOT regenerate — the honest frontier, unchanged by this sweep

Per the scripts' shared philosophy an emit-fail or assembler-reject leaves the last-good `.s` **untouched**;
none of the below were clobbered, and none are new breakage from this seat:

- **`AS-FAIL` 42**: `programs/prolog` 40 (incl. `gnu_prolog/BipsPl/{all_solut,call,consult,list}`,
  `Pl2Wam/{code_gen,pl2wam,read_file}`, `demo/prolog_{parser,recognizer}`), `programs/icon` 2
  (`rung36_jcon_{args,coerce}`).
- **`EMIT-FAIL` 30**: `crosscheck/snocone` 14 (rungA05/A13/A15/B05/B06/B11), `programs/icon` 11
  (the `rung36_jcon_*` family), `programs/rebus` 3, `coverage_sno_nodes` (both repos), `coverage_pl_nodes`.
- **prolog bench assembler-rejected 3**: `cal`, `crypt`, `sendmore`.
- **icon bench compile-error 3**: `options`, `post`, `shuffle`.

## 5. Coverage gap — tracked `.s` that NO script maintains

1275 tracked `.s` in corpus + 175 in SCRIP. Outside every regen script's reach:

| where | n | note |
|---|---|---|
| `corpus/probe/bb` | 12 | witness artifacts, no sweeper |
| `corpus/programs/snobol4/feat` | 1 | — |
| `SCRIP/test/icon` | 9 | feature script covers `test/snobol4` only |
| `SCRIP/test/prolog` | 8 | same |
| `SCRIP/{test/backend/x64, seed, archive/backend}` | 3 | — |
| `corpus/programs/snobol4/demo` | 6 of 27 | see below |

**Four of those six demo files are dead-tool output.** `{roman,claws5,treebank,wordcount}.byrd-reference.s`
(2026-05-08) carry `; generated by scrip-cc -asm` and **NASM** syntax (`%include "snobol4_asm.mac"`) — the
exact provenance class `util_regen_crosscheck`'s header was written to eradicate ("a tool that no longer
exists, linking a dead external GC removed at GC-U-4"). Their `.byrd-reference` name reads as a deliberate
historical snapshot, so **deleting them is a ruling, not a drive-by** — flagged, untouched. The other two
(`bb_macros.s`, `sm_macros.s`) are hand-maintained GAS macro libraries with no `.sno` source: correctly
outside regen, not fossils.

## 6. Build state observed at HEAD (not caused by this row — no code was touched)

`bash scripts/test_smoke_snobol4.sh` on the pristine HEAD build: **PASS=6 FAIL=1 both modes** — `define`
fails m3 and m4 with empty output. This seat changed only `.s` artifacts (nothing consumes them at build
or test time), so this is HEAD's state, reported for whoever owns it. One `ld` warning in the pristine
build: `rtx_zdp.o: missing .note.GNU-stack section implies executable stack`.

## 7. For HQ

1. **RULES step 4 is missing two scripts.** Add `util_regen_programs_s_artifacts.sh` and
   `util_regen_prolog_bench_s_artifacts.sh` to the handoff sequence, or the five-week drift re-accumulates
   on the same two trees.
2. **`util_regen_prolog_bench` needs its commit block** (writes, never commits — §3).
3. **Ruling wanted** on the four `*.byrd-reference.s` NASM fossils (§5).
4. `__gva_names` is **not** a staleness marker (§2) — worth saying out loud before it is navigated by again.
5. The regen scripts share fixed scratch paths (`/tmp/cc_regen.s`, `/tmp/prog_regen.s`) across ALL seat
   roots. Two seats regenerating concurrently would corrupt each other's artifacts. Ran strictly
   sequentially here; a `$$`-suffixed temp is the one-line fix.
