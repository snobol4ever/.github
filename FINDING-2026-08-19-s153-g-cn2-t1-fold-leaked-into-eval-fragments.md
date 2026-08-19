# FINDING 2026-08-19 s153 — g-cn2: THE T1 FOLD LEAKED INTO EVAL/CODE FRAGMENTS AND SILENTLY EMPTIED A CONSTANT

**Seat:** claude.ai web (Claude Opus 5), CN front. **Tree:** SCRIP `b69c63a5` (pristine, full build), corpus `d1ab283b`+.
**Rung:** `g-cn2` — the EVAL boundary witness the s151 cursor listed as OWED. **Verdict: the witness found a live defect in landed T1; repaired in the same session.**

---

## 1. WHAT WAS OWED, AND WHY IT MATTERED

The s151 cursor recorded: *"g-cn2 (owed): the EVAL boundary — prove `&N` inside an EVAL-compiled thunk reads the SEALED cell (value + 341/342 behavior) in both modes; T1's literal table is DRIVER-side and must not be assumed in the runtime-compile path. Witness: `cn_t1_eval.sno`."*

ARCH-SN4-CONSTANTS §T1-FOLD-SEMANTICS stated the safe default in advance: *"no fold in the runtime-compile path is the safe default — verify which way the landed code behaves, then witness it."*

The landed code behaved the OTHER way. It folded.

## 2. THE MEASUREMENT

Minimal repro (`&USER_DECLARED_CONSTANTS = 1` · `&N = 42` · `OUTPUT = 'eval=' EVAL('&N')`), pristine build at `b69c63a5`:

| | T1 ON (**shipped default**) | T1 OFF (`SCRIP_CONST_T1=0`) |
|---|---|---|
| **m3 `--run`** | `eval=` ⛔ **EMPTY** | `eval=42` ✅ |
| **m4 `--compile`** | `eval=42` ✅ | `eval=42` ✅ |

Three things make this the severe class, not a cosmetic one:

1. **It is a MODE34-IDENTICAL violation ON THE DEFAULT ARM** — m3 ≠ m4 with no env var set. That is DEFINITION-OF-DONE item 1 (`m3 ≡ m4`).
2. **It is a SILENT WRONG ANSWER, not an error.** `EVAL('&N + 1')` returned **`1`**, not `43` — the empty read coerced to 0 and the arithmetic completed. Nothing failed, nothing aborted, no diagnostic.
3. **The killswitch arms diverge on a NON-degenerate case.** The s151 spec amendment licensed exactly ONE divergence between the T1 arms (a read textually after the assignment but executing before it). This is not that class: the read here is textually *and* dynamically after the assignment. The killswitch-byte-identity claim was never wrong about `.s` output — it simply never looked at the runtime-compile path.

**The confound was ruled out before the diagnosis.** EVAL is not broken generally: `EVAL('N')`→`42` for an ordinary variable, `EVAL('19')`→`19`, `EVAL('3 * 4')`→`12`, `EVAL('N + 1')`→`43`, and `EVAL('&ANCHOR')`→`0` for a tier-2 keyword. Only tier-3 user constants failed.

## 3. ROOT CAUSE — A FLAG THAT DOCUMENTED ITS OWN CONTRACT AND NEVER ENFORCED IT

`g_sno_seal_enabled` (`lower_snobol4.c:956`) carries this doc, verbatim, since s137: *"the runtime EVAL/CODE fragment compiler re-enters this file with fragment-local state and must stay conservative."* Both `sno_const_val` (T1) and `sno_const_pat` (T2) are gated on it **and on nothing else**.

Nothing ever cleared it. `lower_sno_stage2` grants `= 1` at the whole-program entry (`:2590`) and there is no other write in the file. `sno_lower_fragment_at` (`:2800`) resets the *freeze* tables — `g_sno_nfz`, `g_sno_fz_unsafe`, `g_sno_nsnapref`, `g_sno_nencl` — and leaves the SEAL table and its gate untouched. So a runtime fragment re-entered `sx_lower` with the **whole main program's seal table live**, and T1's TT_KEYWORD arm folded `&N` into a `tree_t *` owned by a compile that had already finished.

**Why m4 was accidentally right:** a mode-4 binary compiles its EVAL/CODE fragments in a **different process** from the one that produced the `.s`. That process's `g_sno_seal` is empty and its gate is 0, so no fold was possible and the read fell through to the sealed cell — the correct route, reached by luck rather than by design. This line now makes deliberate what mode 4 was already doing.

**Why the earlier gates were all green and honest.** The s151 seat's `0/529` killswitch byte-identity and the `blast radius 0/529` both measure emitted `.s`. Fragments are compiled at RUNTIME and appear in no `.s` file. The instrument was sound; the path was simply outside its field of view. This is the same shape as s149's `CLEAR()`-is-a-noop: a defect living exactly where every existing instrument was blind.

## 4. THE REPAIR (SCRIP, `src/lower/lower_snobol4.c`)

One line in `sno_lower_fragment_at`, beside the freeze-table resets that were already the fragment's state-scrubbing home:

```c
int seal_sv = g_sno_seal_enabled; g_sno_seal_enabled = 0;   /* ... */
...
g_sno_seal_enabled = seal_sv;
return g;
```

- **It is the spec's own ruling made mechanical** — ARCH-SN4-CONSTANTS already said no fold in the runtime-compile path is the safe default.
- **It closes T1 and T2 together.** Both resolvers are gated on this one flag; an inlined T2 graph carries the identical cross-compile pointer hazard and is now equally excluded. T2 was never separately witnessed here — it is closed by the same line, not by a second measurement.
- **Fragments keep reading the SEALED CELL by name**, which is what makes 341/342 answerable inside a thunk at all: CN-2's `NV_t.is_const` binding is process-global, unlike the lowerer's table.
- **Placed after the two early `return NULL`s**, so there is one clear and one restore and no early-return leak. Saved/restored rather than left 0 because mode 3 keeps lowering state alive for the life of the process.

**Safety of touching a shared entry point, checked not assumed:** `sno_lower_fragment_at` has exactly two external callers, `runtime_eval.c:451` and `lower_snobol4()` — and `lower_snobol4()` is itself called ONLY from `runtime_eval.c:286`. Both are runtime fragment compiles. The whole-program path enters at `lower_sno_stage2` and never routes through this function.

## 5. GATES

- **`test_gate_udc.sh`: 19/19** (was 12/12; +7 from g-cn2 — `cn_t1_eval` × 2 T1 arms × 2 media, plus 3 checks on the abort lane).
- **⭐ THE GATE IS PROVEN NON-VACUOUS.** With the one line reverted and the tree rebuilt, the gate reads **18/19 with exactly one red: `m3 cn_t1_eval CONST_T1=1`** — precisely the one broken cell of the four-cell matrix, and no other. A gate that cannot go red proves nothing (s68); this one was made to go red on purpose before it was trusted.
- **`test_gate_kw_static.sh --armed`: unchanged** — the only reds are `kw_bare_shadow` (B1) and `kw_protected_write` (KW-5), the two routed non-regressions the s148 cursor already names. Armed 10/14, exactly the recorded watermark.
- **`.s` blast radius:** measured A/B against a **separate worktree built at origin `b69c63a5`** (per-tree objdir build law, `b69c63a5`) rather than against this seat's own tree — the s149 STANDING LAW. See the cursor for the number.

## 6. WITNESSES MINTED (corpus `probe/cn/`)

- **`cn_t1_eval.sno` + `.ref`** — the success lane: `EVAL` of an integer constant, of an arithmetic expression over it, of a string constant; a direct read for comparison; and a **`CODE`** fragment reading the same constant through a direct Goto `:<C>`. All read `42`/`43`/`hello`.
- **`cn_t1_eval_undecl.err_sno`** — the abort lane: an UNDECLARED `&name` read inside a fragment raises **342** with the name, in both media. `.err_sno` + no `.ref` is the repo convention for an abort lane; streams are checked separately because m4 buffers stdout to exit and m3 does not, so `2>&1` interleaving is not comparable (the s148 witness-authoring trap).

## 7. ⛔ ONE SEMANTIC QUESTION FOR LON — RECORDED, DELIBERATELY NOT RULED

The SPITBOL manual (v3.7 p.131) says: **EVAL *fails* if evaluation of its argument fails, or if the argument contains a syntax error**, leaving the reason in `&ERRTEXT`. SCRIP instead **aborts** with error 342 when a fragment reads an undeclared `&name`.

I did not change this, for two reasons. First, converting an error into a statement failure is the `&ERRLIMIT` mechanism SCRIP does not have yet — the same missing machinery `kw_protected_write` is parked on (rung KW-5), so the two should move together or not at all. Second, 341/342 are SCRIP extensions with no oracle entry (the manual's table ends the 240s at 251 = *"Keyword operand is not name of defined keyword"*, which is what stock `sbl` answers for every `&name` in this family), so their interaction with EVAL's failure semantics is a design call that belongs to Lon and not to a repair rung. Today's behaviour is now PINNED in `cn_t1_eval_undecl.err_sno` so KW-5 moves it deliberately rather than silently.

## 8. ⛔ SIDE-FINDING — B2a's ARTIFACT DEBT, NOT g-cn2's (attribute it correctly)

The mandatory RULES-step-4 regens (this seat touched `lower_snobol4.c`) moved **50 checked-in `.s` files** — 43 feature (SCRIP `89d569da`), 7 benchmark (corpus `6faf02f4`), plus demo (corpus `65bf9aca`). **None of it is g-cn2's.** Proof, not assertion: for a changed artifact, the ORIGIN-HEAD binary and the fixed binary emit the byte-identical `.s` (`93a9a38e…` from both), while the version committed at `b69c63a5` was `60e748dd…` — i.e. **both** compilers disagree with the checked-in file, so the file was stale before this seat existed. The whole-corpus number says the same thing: `0 movers / 527`.

The drift is **B2a** (`d9f5cf24`): every hunk is the match-β continuation cell, `lea rax, [rip + .Lx32_13]` + `mov qword ptr [rbp-48], rax` with the `match_beta_cont` comment, which is precisely what that commit introduced. B2a landed on main without its RULES-step-4 regens, so the artifacts have been describing a pre-B2a compiler ever since. A later seat reading those `.s` files as "what the compiler emits" would have been reading history — the exact failure RULES step 4 exists to prevent (*".s = HONEST CURRENT compiler output, never a pinned golden … to know what the compiler emits, sweep the COMPILER, never the artifacts"*).

## 9. LAW THIS EPISODE ARGUES FOR

**A killswitch-byte-identity claim is a claim about the paths the instrument can see.** `0/529 .s` movers was true, carefully measured, and did not cover the runtime-compile path, because fragments never reach a `.s` file. Any optimizer tier that installs LOWERER-side static state (T1's literal table, T2's staged graphs, and every tier CVA/T3 will add) must be witnessed at the EVAL/CODE boundary SEPARATELY — the `.s` sweep structurally cannot do it. The next tier should mint its boundary witness in the same commit as the tier, not a rung later.
