# FINDING 2026-07-23 (Claude Opus 4.8) — JCON self-host: record-serial FIXED (ast2ir byte-identical); next frontier = seq() co-expression re-init

**Repos/build:** SCRIP fresh clone HEAD `577abd60` (newer than GOAL-JCON-IN-SCRIP LIVE CURSOR's `fd5f9ed2`; GC work landed since). All `-O0`. Oracle icont/iconx 9.5.25a + oracle jtran built from `jcon-master/tran`. SCRIP-jtran 17-module: 507288 asm, 0 bombs, links clean. Java-free DATA comparison per s121 permanent note.

## Correction to stale prose (measured)
The LIVE CURSOR "preproc loops forever re-emitting the string-literal line (quote-scan path)" blocker is **RESOLVED at this HEAD**. `preproc` is byte-identical to oracle on hello AND on the `case move(1) of {"\""|"'":…}` quote-scan idiom (`/tmp/quote_semi.icn`). Pipeline is byte-identical through `preproc : yylex : parse : ast2ir` after the fix below.

## FIXED: record image() serial — per-type, not global (committed SCRIP `2934428f`)
**Bug:** first self-host divergence was at `ast2ir`. IR structurally identical to oracle; only the serial numbers in AST-node labels differed. `irgen.icn:1454 ir_naming()` derives every IR label from `image(record)`. Canonical Icon `ralc.r:349`: `blk->id = (((struct b_proc *)recptr)->recid)++;` — serial lives in each record CONSTRUCTOR's block, so every record type counts independently (unlike list/table/set/coexpr which use global per-type counters). SCRIP used one global counter in `rt_record_image_id`, assigned lazily at image() time.
**Minimal repro** (`/tmp/recser_semi.icn`): `foo(1) foo(2) bar(3) foo(4) bar(5)` → oracle `foo_1 foo_2 bar_1 foo_3 bar_2`; SCRIP was `foo_1 foo_2 bar_3 foo_4 bar_5`.
**Fix (5 files, +9/-4):** `serial_next` on the persistent per-type block (`DatType` in driver_private.h) + `id` on the instance (`DATINST_t` in core.h); `inst->id = t->serial_next++` at CONSTRUCTION in all three ctor paths — `dat_alloc_fill` (driver_data.c, the real mode3/mode4 emitted-code path), `_make_ctor` + `DATCON_fn` (core.c). `rt_record_image_id` returns `inst->id`.
**Verified:** m3==m4==oracle on repro; image() stable across repeated calls same instance; ZERO regression (stash/rebuild/diff named fail-sets IDENTICAL 22/22, 239/22/32 — 239-vs-241 is documented env math-drift rung17/19/26/30/37 present at baseline); SCRIP-jtran ast2ir now BYTE-IDENTICAL; `lhw.class` byte-identical to oracle.

## NEXT FRONTIER: seq() garbage on 2nd co-expression of the same lexical `create ("L"||seq())`
After the fix, `bc_File` emits `lhw.class` byte-identical; `p_lhw$main.class` matches 813 bytes then diverges. Localized upstream via the Java-free `u_gen_File` (ucode) stage: `.u2` BYTE-IDENTICAL, `.u1` differs in EXACTLY ONE token — a label: SCRIP `mark L6344161`/`lab L6344161` vs oracle `mark L1`/`lab L1`. Source: `gen_ucode.icn:571 u_nextlab := create ("L" || seq())`, one per procedure; label pulled via `@u_nextlab`.
**Minimal repro** (`/tmp/seq3_semi.icn`):
```
procedure gen_labels(); return create ("L" || seq()); end
procedure main(); g1 := gen_labels(); write(@g1); g2 := gen_labels(); write(@g2); write(@g1); end
```
Oracle: `L1 / L1 / L2`. SCRIP: `L1 / L140734507487313 / L2` (0x7FFF… STACK-ADDRESS range).
**Diagnosis:** the FIRST `create ("L"||seq())` co-expr works (`L1`). A SECOND `create` of the same lexical `seq()` call site yields a GARBAGE stack address on its FIRST `@` pull, then recovers (`g1`'s later pull is correct `L2`). This is a **per-box generator-state slot not zero-initialized on a fresh co-expression instance** — same family as the record-serial bug and the GOAL-ICON-BB tab-β-slot-lifetime bug (per-box state uninitialized on (re)entry). `seq()` in isolation (plain, and single `create ("L"||seq())`) works — the trigger is a SECOND instance of the same lexical create.
**Next step:** MONITOR-first / gdb the `seq` generator's counter slot allocation in `bb_create`/`bb_suspend`/the by-name generator dispatch — find where the second co-expression instance's seq counter slot is left uninitialized (reads stack). Fix = zero-init that per-instance slot at co-expression creation (α). Then re-run `u_gen_File` (.u1 byte-match) → `bc_File` (.class byte-match) → widen to compiler's own modules (irgen.icn etc.).

## State
- Fix COMMITTED locally SCRIP `2934428f` (NOT pushed — no credential this session; not a handoff).
- Binaries rebuilt with fix. SCRIP-jtran `/home/claude/jt/jtran`; oracle jtran `/home/claude/jcon-oracle-src/tran/jtran`; harness `/tmp/cmp.sh`.
- Repros: `/tmp/{recser,seq3,quote}_semi.icn`. Emitted classes `/tmp/{sc,or}_cls/`. ucode `/tmp/{sc,or}_hw.u1`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude

---

## UPDATE (same session): SEQ bug FIXED (committed SCRIP `a3b0e861`) — .u1/.u2 now byte-identical; next = JVM constant-pool ordering

**Bug (fully traced):** `seq()` lowers to `IR_TO` with implicit `from=1, to=INT64_MAX` (`lower_seq`, lower_icon.c:1099). `build()` (lower_icon.c:25) auto-promotes a generator-target γ edge to the target's β (`lc_γ_to_β` for generator kinds). So `seq()`'s hi-bound literal's γ into IR_TO landed `xchainN_β` (RESUME: `inc [op_off+16]; cmp`) instead of `xchainN_α` (INIT counter from `from`). The FIRST co-expression instance survived on a zeroed frame (counter 0 → inc → 1); a SECOND `create` of the same lexical `seq()` reused a POOLED frame slab with stale `[op_off+16]` → uninitialized counter read a garbage STACK ADDRESS on first `@` (0x7FFF… range), then recovered. `1 to 3` was immune because `lower_to` (line 1155) already re-wires its hi-bound with `lc_γ_to` (defeats build's β-promotion); `lower_seq` did not.
**Discriminator:** `create (1 to 3)` ×2 = correct; `create seq()` ×2 = garbage on 2nd. Both are IR_TO with byte-identical box bodies (`op_sa=128 op_sb=160 op_off=96 counter=112`); the ONLY difference was the hi-literal's γ edge (`xchain_β` vs `xchain_α`).
**Fix (1 line):** `lower_seq` now calls `lc_γ_to_α(mr, to)` after `build`, forcing the `α!` entry edge (the FORWARD-FIRST-ENTRY idiom, lower_icon.c:217). Emitted edge flips `xchainN_β → xchainN_α`.
**GOTCHA that cost time:** `lower_icon.c` is STATICALLY LINKED INTO `scrip` (nm scrip shows `lower_seq` at `t`), and `scrip --compile`/`--run` uses scrip's OWN lowering, NOT `out/libscrip_rt.so` (ldd scrip shows no scrip_rt dep). Rebuilding only the `.so` after a lowering change is a NO-OP for the compiler — **`make scrip` is required for any lower_*/emit change; `make libscrip_rt` only affects the standalone mode-4 output binaries' runtime.** (The record-serial fix touched driver_data.c which is in BOTH, so both were rebuilt there — masking this until now.)
**Verified:** both modes == oracle on all repros; ZERO corpus regression (named fail-set IDENTICAL 22/22); SCRIP-jtran `u_gen_File` `.u1` AND `.u2` now BYTE-IDENTICAL to oracle-jtran; `bc_File` `lhw.class` byte-identical.

## Next frontier: JVM constant-pool ORDERING in `p_lhw$main.class`
After the seq fix, `p_lhw$main.class` diverges at char 647 (moved earlier from 814). Both files contain the SAME UTF-8 string set but in different constant-pool ORDER: oracle emits the `Resume` method-ref before `error`; SCRIP emits `error` first (sizes 973 vs 983 — different index encodings, same content). Traces to the order `bc_File`/`interface.icn` first REFERENCES methods into the pool. Same order-of-creation family. **JVM-backend-only** — the entire Icon frontend (preproc→yylex→parse→ast2ir→ucode `.u1`/`.u2`) is now byte-identical, which is the substantive self-host milestone. Next step: find where the method-ref pool population order differs (likely a table/set iteration order in interface.icn's methodref emission, or a `bc_op_methodref` call-order difference) and align it; then `p_*$main.class` byte-matches → full self-host on hello → widen to compiler's own modules.

## Commits (local, NOT pushed — no credential this session)
- `2934428f` ICN-REC-SERIAL
- `a3b0e861` ICN-SEQ-COEXPR-REINIT
