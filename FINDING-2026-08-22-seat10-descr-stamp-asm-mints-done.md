# FINDING seat10 — descr-stamp-asm-mints DONE: census, zero-cost mod_op stamping, and two latent 32-bit-tag-compare defects found and fixed

**Session:** seat10 (`/home/claude10`, Claude Sonnet 5) · **Date:** 2026-08-22 · **Queue row:** `descr-stamp-asm-mints` (rank 1)
**Verdict:** every DONE-WHEN clause met with receipts below. Calling `s4e_msg.sh done descr-stamp-asm-mints` after this FINDING lands.
**Precondition confirmed:** `descr-stamp-fields` claim reads `seat01` / `DONE` before any work here started.
**Commits (SCRIP, pushed to origin/main):** see Disposition — this FINDING lands with the code, not after it.

---

## 0. Scope note, read this first

The brief scoped this row to "all 14 .S files under `src/runtime/rtx/`." The census (§1) stayed inside that scope. The fix
(§2) also stayed inside it for the mint sites themselves — but making the fix *safe to ship* required following the
stamped values to their first consumers, which led outside the 14 files twice: `src/runtime/rt/rt_asm_helpers.S` (§3a)
and `src/templates/x86_asm.h` (§3b). Both are real, previously-latent defects that this row's own stamping is what
finally exercised. Fixing them is not scope creep — the alternative was shipping a stamp that segfaults the SNOBOL4
corpus on first array access, which is worse than not stamping at all. Both are called out explicitly rather than
folded silently into "the fix."

## 1. THE CENSUS — every descriptor-minting site in the 14 files, by shape

**Methodology:** a "site" is one textually distinct terminal code block (a `ret`, or an unconditional tail-jump to
another function) that decides what the caller receives. Guards that funnel through one shared bail label count as
that ONE physical block, not once per branch that reaches it; a direct one-instruction bail straight to a C fallback
(no shared label) counts as its own site, since it is textually its own decision point. Three shapes, matching the
brief's own vocabulary:

- **Shape A — 32-bit tag move**: a single `mov e*, DT_x` (register) or `mov dword/qword ptr [mem], DT_x` (memory) that
  sets a small constant and, by construction, zeroes mod_op/src_node (and slen, for the register form).
- **Shape B — 64-bit pair build**: a wider constant (`mov r64, imm64`, or an `or` combining a tag with a separately
  computed slen/value) that already spans more than the bare tag byte, currently still leaving mod_op/src_node at 0.
- **Shape C — passthrough**: forwards an existing descriptor (an input argument, a callee's already-computed return,
  or a tail-jump to the untouched C body) rather than minting a fresh one. Needs no change, and none was made.

Scope note on what counts as a "mint": beyond the `rax:rdx` register-pair return the brief's own example
(`rt_faildescr`) uses, a handful of sites mint a fresh descriptor via a different convention — an out-parameter
pointer (`rt_coerce_num2_d`) or a struct field write (`rt_subscript_var`'s `VCELL_t.sv`, all four DT_FAIL inits).
These are real mints of the identical zero-stamped shape and are stamped alongside the register-pair ones; they are
marked **[out-of-band]** below so the count is auditable against a pure register-pair reading too.

| File | Shape A | Shape B | Shape C | Notes |
|---|---:|---:|---:|---|
| `rtx_misc.S` | 1 | 0 | 0 | `rt_faildescr` |
| `rtx_icncall.S` | 0 | 1 | 0 | `rt_proc_value` |
| `rtx_icngen.S` | 1 | 0 | 1 | `rt_gen_spine_pass_ω` (A), `_γ` (C, pure passthrough) |
| `rtx_plunify.S` | 2 | 0 | 1 | `rt_pl_dop_unify`: two bail-shaped FAIL mints, one passthrough of `rt_pl_deref_val`'s result |
| `rtx_icnnum.S` | 0 [+2 out-of-band] | 0 | 1 | `rt_coerce_num2_d`'s two out-param mints use the memory-store shape A pattern; its own exit is a bail (C) |
| `rtx_icnagg.S` | 3 | 0 | 14 | `rt_size_d`(2A/4C), `rt_list_bang_at`(1A/1C), `dat_field_get`(0/9C — an 8-guard linear scan, see §1a) |
| `rtx_alloc.S` | — | — | — | N/A: `rt_gcheap_alloc`/`rt_str_alloc`/`rt_agg_alloc` return raw pointers, no DESCR_t |
| `rtx_icnvar.S` | 0 | 0 | 5 | `rt_assign_var`: every exit relays an existing `val` argument or bails; zero fresh mints |
| `rtx_icnrel.S` | 0 | 0 | 3 | `rt_jct_relop` returns `int`, not DESCR_t (N/A); `rt_str_coerce` is identity + bail, zero mints |
| `rtx_str.S` | 0 | 1 | 4 | `str_concat_d`(1B/4C incl. the two null-identity passthroughs); `VARVAL_fn` returns `char*`, N/A |
| `rtx_zdp.S` | — | — | — | N/A: anchor/probe/report instrumentation, no DESCR_t anywhere in the file |
| `rtx_arith.S` | 6 | 0 | 6 | `rt_cmp_d` returns `int` (N/A); `rt_add`/`rt_sub`/`rt_mul` each 2A + 1C |
| `rtx_icnsub.S` | 2 [+4 out-of-band] | 5 | 10 | `rt_subscript_var`: 5 NAMETRAP mints (B) across list/table-hit/table-miss/substring/array arms, 2 FAIL mints (A), 4 VCELL.sv FAILDESCR struct inits (A, out-of-band), 8 direct bails + 1 shared `.Lsub_bail` block (C) |
| `rtx_match.S` | 1 | 0 | 2 | Only `rt_defer_get_pat_fn` returns DESCR_t via the pair (1A + 1C); everything else in this 1,177-line, mostly-eradication-slice file returns a plain scalar (`long`/`int`/`void`) or is a tombstone — **the file's own size is not a proxy for mint-site count**, a finding worth stating since it ran against the intuition going in |

**Totals, register-pair convention only:** Shape A = **16**, Shape B = **7**, Shape C = **47**. Out-of-band (out-param /
struct-field mints, same shapes, different calling convention): **6** (2 in `rt_coerce_num2_d`, 4 in
`rt_subscript_var`'s VCELL.sv). Grand total of sites carrying a fresh zero-stamp before this row: **29** (23
register-pair + 6 out-of-band). Cross-checked against a raw `grep` for every `mov`/`or` that places a named `DT_x`
constant into a register or memory operand across the 14 files: 29 hits after excluding one false positive
(`rtx_alloc.S:119`'s `mov edi, DT_S` is an argument being staged for `rt_gcheap_alloc`, not a descriptor mint) and
one deliberate exclusion (§1b).

### 1a. `dat_field_get`'s 9-site count is real, not a miscount

Nine `c_dat_field_get` bail instructions/passthrough in one function looks high; it is the honest shape of an inlined
linear scan with an early-reject guard at every dereference step (null instance, null type, `nfields<3`, null fields
vector, null field name pointer, scan-miss, null instance fields, plus the gate). Each guard is a textually distinct
one-instruction decision point per this row's counting rule (§1 methodology) and none of them mint — they either bail
to C or, on a hit, load and relay a pre-existing stored value (itself a passthrough, since a stored cell may legally
hold `DT_FAIL` — "return `*cell` verbatim" per the function's own header).

### 1b. One site left deliberately unstamped: `rt_defer_get_pat_fn`'s `.Ldfpf_null`

```
.Ldfpf_null:
    xor     eax, eax                             /* return NULL */
    ret
```

This mints `DT_SNUL` (0) via `xor eax,eax`, not a named-constant `mov`. Every other shape-A site in this census
widens a `mov e*, DT_x` (5 bytes, fixed width regardless of the immediate's value) into the identical instruction
with a stamped immediate — genuinely zero cost (§2). This one does not: `xor eax,eax` is a 2-byte encoding, while the
smallest immediate-carrying replacement (`mov eax, imm32`) is 5 bytes. Stamping it would be the one site in this row
that actually costs something, on a function with no stated speed claim either way. Left unstamped, named here so it
is a recorded decision rather than an oversight, and not folded into a killswitch discussion because a 3-byte size
delta on one leaf does not warrant one.

## 2. THE FIX — sentinel mod_op, zero cost, no killswitch, no new global

Read `bb_lit_scalar.cpp`'s `lit_tag_imm()` first (the reference implementation `descr-stamp-fields` landed): it packs
`mod_op = (IR_* opcode) + 1` and `src_node = the current node id`, both **only knowable at compile time**, because
that function runs once per SNOBOL4 statement the compiler is actively lowering. None of the 14 rtx/*.S files are
compile-time codegen — they are ONE hand-written runtime shared by every compiled program — so there is no per-call
IR node or opcode to read, and `SCRIP_DESCR_STAMP` (a `static int` cached inside `bb_lit_scalar.cpp`, internal
linkage, compiled only into the `scrip` compiler's own codegen path) is not reachable from a `.S` runtime file at all.

What **is** knowable at assembly time: *which runtime function* mints a given descriptor, and that identity is fixed
forever once the file is written — `rt_faildescr` always means "the generic runtime FAIL mint," on every call, in
every process. That turns the fix into a compile-time constant, not a runtime decision, which has two consequences
the brief explicitly asked to be priced honestly:

- **No killswitch is needed.** There is nothing to toggle at runtime — the sentinel is baked into the same immediate
  the mint already builds, unconditionally, exactly the way `rt_proc_value`'s existing `PROCVAL_SLEN` sentinel
  already is. `⛔ NO NEW GLOBAL` is satisfied by construction: nothing added is mutable state, every `MOD_OP_RT_*` is
  a `#define` constant in `descr_tags.inc` (the file "no future file has an EXCUSE to hand-encode" already owns, and
  the natural home for the existing `DT_NAMETRAP_LO`-style packed-constant precedent).
- **The ON-arm cost is not a killswitch A/B — it is a static, provable zero, checked at the encoding level, not
  benchmarked.** Every touched site already builds its return via one `mov`/`or` against a small immediate; folding
  `(MOD_OP_RT_x << 8)` into that same immediate produces the byte-identical instruction *encoding width* in every
  case but one (§1b), confirmed directly rather than assumed: `mov e32, imm32` is a fixed 5-byte form regardless of
  the immediate's value, `mov r64, imm64` (the NAMETRAP sites, already ≥33 bits wide before this row because of the
  packed `slen`) is a fixed 10-byte form, and `mov m64, imm32` (the VCELL.sv inits) is a fixed 10-byte form. The one
  encoding-width trap this row found and avoided: `or reg, small_imm` (`str_concat_d`, `rt_match_replace`'s NV_SET_fn
  argument staging) can shrink to a 4-byte `imm8`-sign-extended form for values in ±127 — DT_S(2) qualifies, the
  stamped combination does not — so those two sites do cost 3 extra bytes each. Priced, not hidden: two sites, +3
  bytes each, on paths that are not the ones this campaign's benchmark family times.

Values start at **130**, one past `IR_OP_COUNT` (129, `IR.h`; confirmed live, matches `descr-stamp-fields`'s own
"129/129 real ops named" count) so a stamp reader can tell "compiler-stamped IR op" (mod_op 1–129) from "hand-written
runtime mint" (130+) on sight. `src_node` stays 0 at every site: there is no per-call source-program node to name
here, and per `descr.h`'s own naming (`DESCR_MOD_OP_UNSTAMPED`/`DESCR_SRC_NODE_UNSTAMPED`, both 0, named as two
separate constants), a nonzero `mod_op` alone already distinguishes "runtime-stamped" from the true all-zero pair
that means "nothing touched this" — closing exactly the false-signal gap the brief describes, without needing
`src_node` to carry anything. **Not wired into `kind_names[]`**: a debug printer indexing `kind_names[mod_op-1]` needs
its own bounds check for any externally-derived index regardless of this row, and extending a shared array outside
this row's actual defect is deferred as a named follow-up rather than bundled in silently.

13 sentinels defined (`descr_tags.inc`, immediately after `DT_NAMETRAP_LO`): `MOD_OP_RT_{FAILDESCR, ADD, SUB, MUL,
SIZE_D, LIST_BANG_AT, PROC_VALUE, GEN_SPINE_PASS_OMEGA, PL_DOP_UNIFY, SUBSCRIPT_VAR, STR_CONCAT_D, COERCE_NUM2_D,
MATCH_REPLACE}`. `rt_subscript_var`'s five NAMETRAP arms and two FAIL arms, plus its four VCELL.sv inits, all share
`MOD_OP_RT_SUBSCRIPT_VAR` — one runtime function, one identity, regardless of which internal arm fired. **29 of the
30 sites found in the census carry a stamp; the 30th (§1b) is a named, reasoned exception.**

Also fixed in the same pass: `rtx_abi.inc`'s own `DESCR_t` layout comment still described the **pre-split 2-field**
struct (`v (int32) at 0, slen (uint32) at 4`) — stale since `descr-stamp-fields` narrowed `v` to a `uint8_t` and
inserted `mod_op`/`src_node` in the same eightbyte. The old comment was never *wrong* in the sense of producing bad
values (`(slen<<32)|v` with a small `v` bit-packs identically either way), which is exactly why it went unnoticed for
a full row — but it is precisely the kind of doc-vs-code drift `rtx_abi.inc`'s own header calls out having already
cost 14 sessions once (the r12-pin correction). Updated to describe the current 4-field layout, with the stale
2-field reading kept below it marked SUPERSEDED for provenance, matching this file's own convention.

## 3. Two latent defects this row's stamping exposed, and fixed

Both defects are instances of the **exact hazard `descr-stamp-fields` §3 named and left open**: "a 32-bit compare
against a bare tag constant reads mod_op/src_node too, and will silently misbehave once they carry real values." That
row found and converted 171 such sites *inside* `src/runtime/rtx/` and the compiler's own templates. Both defects
below sit **just outside** that swept surface, and neither was reachable by grepping for the literal text `DT_x` —
which is exactly why they survived the 171-site sweep and were only found by making mod_op nonzero for the first
time on a corpus-live path and watching what broke.

### 3a. `rt_deref` and `to_int` (`src/runtime/rt/rt_asm_helpers.S`) — SIGSEGV, not a slowdown

This file is **outside `src/runtime/rtx/`** (it lives in `src/runtime/rt/`), is AT&T syntax (its own header explains
why: it predates `rtx_abi.inc`, which is Intel-only), and was the exact "sixth phantom class" `rtx_misc.S` warns
about — invisible to any grep scoped to `*.S` under `runtime/rtx/`.

```
.Lrd_asm:
    movl   %edi, %eax
    cmpl   $DT_N, %eax        /* 32-bit: reads v + mod_op + src_node, not just v */
    jne    .Lrd_retd
```

Once `rt_subscript_var`'s NAMETRAP return carries `mod_op=139` (§2), `%eax`'s low 32 bits are `0x00008B28`, not
`0x28` — the compare misses, `rt_deref` falls to `.Lrd_retd` (return the input **unchanged**, its "not a NAMETRAP"
arm) instead of actually dereferencing it. `VARVAL_fn`'s `DT_N` arm calls `rt_deref` and recurses on the result;
fed its own unchanged input forever, it recurses without bound. **Reproduced and captured**: running
`corpus/crosscheck/data/091_array_create_access.sno` (`A=ARRAY(5); A<1>='first'; ...; OUTPUT=A<1>`) on the stamped-
but-unfixed build SIGSEGVs; `gdb bt` shows ~280,000 identical `c_VARVAL_fn` frames terminating in `NV_SET_fn` →
`output_val`, with the literal value `0x0000000200008b28` (my exact stamped NAMETRAP low-eightbyte) sitting in the
stack scan — the smoking gun, not an inference.

`to_int`'s `cmpl $DT_I, %edi` has the identical shape, one function down, with a milder consequence: a stamped `DT_I`
value fails the compare and falls to `to_int_slow` — the **correct** C body, just without the fast path. Not a
correctness bug on its own, but the same defect class, fixed in the same commit rather than left for a value that
happens not to trigger it today. (`rt_subscript_var`'s own `DT_I` handling never calls `to_int` — it inlines the
32-bit truncation directly — so this specific miss was latent, not yet corpus-live; fixed anyway since it is the same
one-line defect.)

**Fix**: `cmpb $DT_N, %dil` / `cmpb $DT_I, %dil` — byte compares on the *already-live* low byte of `%rdi`, deleting
the now-redundant `movl %edi,%eax` scratch copy in `rt_deref` (its target, `%eax`, is overwritten two instructions
later by the SLEN extraction regardless of the compare's outcome, so the copy was write-only even before this fix).

### 3b. `x86_cmp_imm` (`src/templates/x86_asm.h`) — the encoder never supported 8-bit registers at all

The Icon-family "171-site conversion" converted **template-emitted** compares from `x86("cmp","eax",...)` to
`x86("cmp","al",...)` — e.g. `bb_subscript.cpp`'s `x86("cmp", "al", (long)DT_FAIL)`, checking whether
`rt_subscript_var`'s return failed. Tracing the OOB-array SIGSEGV symptom (`a<4>` on a 3-element array silently
returning success instead of failing) past the 3a fix, `gdb`'s live disassembly of the JIT-emitted call site showed:

```
cmp    $0x68,%eax        ; NOT %al — a 32-bit compare, despite the template requesting "al"
jne    0x7fffee00089e
```

`x86_rnum("al")` deliberately returns the same index as `x86_rnum("eax")` (0) — by design, for callers like `movzx`
where the *opcode itself* fixes the operand width and the caller only needs the bare register number. But
`x86_cmp_imm` (and every other `x86_alu_rr`-based encoder: register-register `cmp`, `test`, `mov`, `and`, `or`,
`xor`, `add`) has **zero register-width detection** — it always emits the 32-bit `0x83`/`0x81` opcode forms
regardless of what string was passed. `x86("cmp", "al", (long)DT_FAIL)` was therefore **silently identical to**
`x86("cmp", "eax", (long)DT_FAIL)` in the BINARY medium (mode-3's own hand-rolled byte encoder) for as long as this
encoder has existed. Grepped for a pre-existing correct 8-bit `CMP` opcode (`0x38`/`0x80`) anywhere in `x86_asm.h`
first — **zero hits** — confirming there was never a working alternate path a template could have used instead.

This is why the "171-site conversion"'s own byte-identity proof (§6 of the `descr-stamp-fields` FINDING, a full
322-program `.s` diff with the killswitch OFF) could not have caught this: mode-4's TEXT medium hands the literal
string `"cmp al, 104\n"` to the *real* `as`, which encodes it correctly regardless of this encoder's bug — the .s
text and the resulting `.o` are right either way. Only mode-3's BINARY medium runs this hand-rolled encoder, and
`descr-stamp-fields`'s own verification never diverged mode-3 from mode-4 on a path this specific (the two arms
"were performance-equal, as the m3 ≡ m4 design invariant requires" — true for cycle counts, not for what turned out
to be an unequal-but-dormant *encoding* bug). And it was truly dormant: with mod_op/src_node always 0 before this
row, a 32-bit compare against a small tag constant and an 8-bit one agree on every input, because the upper 24 bits
being compared are 0 on both sides of the `cmp`. This row's stamping is the first thing to make those upper bits
nonzero on a corpus-reachable path, which is what surfaced a bug that predates this row entirely.

**Fix**: added `x86_is8()` (checks against the 16 canonical 8-bit register names) and one new branch in
`x86_cmp_imm` that emits the correct `CMP r/m8, imm8` form (`0x80 /7 ib`, with a REX prefix whenever `x86_is8()` is
true — mandatory for `spl/bpl/sil/dil` to avoid aliasing the legacy `ah/ch/dh/bh` encoding, harmless-but-consistently-
emitted for `al/cl/dl/bl` too) ahead of the existing 32/64-bit logic, which is otherwise untouched. The TEXT-medium
branch of the function (`x86_rec("cmp") + reg + ...`) was not touched at all — confirmed byte-identical by the
regen sweep (§4).

**Scope discipline on this one**: only `x86_cmp_imm` was fixed, because it is the one function this row's own
changes proved is exercised with an 8-bit register argument today. `x86_alu_rr` (backing register-register `cmp`,
`test`, `mov`, `xor`, `add`) and `x86_and` share the identical missing-width-detection shape and are equally capable
of the same silent 32-bit fallback if ever called with an 8-bit register name — flagged here as a **named, unproven
risk** for whoever next touches an 8-bit register operand in a template, not fixed speculatively against a call site
that does not exist yet.

## 4. Verification

- **`scripts/util_tag_layout_verify.py`**: `GATE PASS` before and after every code change in this row, including
  "no hand-encoded tags in .S 2 asm dirs swept" and "descr.h == descr_tags.inc 22 defines cross-checked" (the 13 new
  `MOD_OP_RT_*` defines do not perturb that count — they are not `DTYPE_t` tag values).
- **Reproduced, bisected, and fixed a real regression rather than asserting none existed.** First pristine build +
  full corpus with all 30 stamps in place: SNOBOL4 crosscheck **308/321 m3, 307/321+1skip m4** (13 failures, all
  array/GC-shaped) — reproduced identically on a second immediate rebuild+rerun (ruling out flakiness before
  investigating). Stashed every `.S`/`descr_tags.inc` change, rebuilt, reran: **320/321, 1 failure** (the sole
  pre-existing `160_pat_alt_inner_gen_resume`), reproduced identically on a third rerun. Bisected by reverting only
  `rtx_icnsub.S`: baseline restored, isolating the regression to that file. Root-caused via gdb backtrace (§3a) and
  live disassembly (§3b) rather than guessed at. Cross-repo diligence during the bisection: confirmed `corpus/`'s
  local checkout was byte-identical and clean throughout the whole investigation window (`git status` empty at every
  check) — the regression is attributable to this row's own code, not concurrent fleet activity, even though
  `origin/main` on both SCRIP and corpus moved substantially (6 and 2 commits respectively) during this session.
- **Post-fix, both defects closed**: SNOBOL4 **320/321 m3, 319/321+1skip m4, DIVERGE=0** — exactly the pre-existing
  baseline, byte-for-byte the same single known failure. Icon **4/4**, unchanged. Prolog: three back-to-back runs on
  the *identical* fixed binary returned three different PASS/FAIL/SKIP counts (114/3/72/1 → 108/5/76/1 →
  106/2/81/0 → 107/2/80/1) with no code change between any of them — the suite has genuine pre-existing run-to-run
  flakiness (its own baseline run showed this before any code from this row existed), unrelated to and not
  addressed by this row; `rung81_neq_unify` in particular is not stably reproducible in either direction.
- **`test_gate_emit_no_lang.sh`**: `OK: LANG-BLIND` (relevant: this row's `x86_asm.h` fix touches a shared encoder).
- **`test_gate_template_medium_invisible.sh`**: ratchet unmoved — `0` BOTH-MEDIUM sites in `bb_*.cpp` (same as
  before this row; the pre-existing `xa_flat.cpp(8)` WIP item is untouched by this row).
- **`test_gate_rtx_store_width.sh`**: `GATE PASS`, 10 GOT-tainted stores checked — directly relevant to this row's
  defect class, unaffected.
- **Core-dump witness** (not a live-breakpoint peek): broke at `rt_subscript_var`'s 4th call in
  `1110_array_1d.sno` (`a<4>`, the OOB-high case), `finish`ed one frame out, `generate-core-file`d, then **reloaded
  the core in a fresh `gdb` invocation** (`gdb ./scrip witness.core`) and decoded `$rax` independently:
  `v=104(0x68, DT_FAIL)`, `mod_op=139(0x8B, MOD_OP_RT_SUBSCRIPT_VAR)`, `src_node=0`, `rdx=0` — exactly the designed
  stamp, read from a genuine post-mortem artifact, not inferred.
- **`make pristine` EXIT=0**: five times over the course of this row (each code iteration), always clean; final
  state confirmed clean immediately before this FINDING was written.
- **`.s` artifact regen** (mandatory: this row touched `src/templates/x86_asm.h`, codegen): ran
  `util_regen_benchmark_s_artifacts.sh`, `util_regen_feature_s_artifacts.sh`, `util_regen_demo_s_artifacts.sh` in
  order. All three report **no changes** (byte-identical) — expected and confirms the fix is confined to the BINARY
  medium: the TEXT-medium branch of `x86_cmp_imm` was never touched, so every mode-4-compiled program's `.s` is
  provably unaffected. (One pre-existing, already-known EMIT-FAIL — `coverage_sno_nodes.s` — is unrelated to this
  row and was not newly introduced; the regen script's own output frames it as expected for mid-design BB shapes.)

## 5. DONE-WHEN, clause by clause

| Clause | Status | Evidence |
|---|---|---|
| Confirm `descr-stamp-fields` DONE before starting | ✅ | `$PO/claims/descr-stamp-fields.claim`: `seat01` / `DONE` |
| Census every asm mint site in `src/runtime/rtx/*.S` by shape, post the three counts | ✅ | §1: A=16, B=7, C=47 (register-pair); +6 out-of-band; totals cross-checked against a raw grep |
| No per-op filter | ✅ | Every shape-A/B site in scope stamped uniformly by *function identity*, none excluded by which IR op/language reached it |
| No new global | ✅ | 13 `#define` constants (`descr_tags.inc`), zero mutable state added anywhere |
| Pair ABI survives untouched | ✅ | §2: same instruction, same operand count, same registers at every site but the two named in §2's `or`-shrink note |
| ON-arm cost measured/priced, not hidden | ✅ | §2: zero-cost proven at the encoding level for 27 of 29 stamped sites; +3 bytes each named for the remaining 2; RT_OPT=-O0 throughout (project default, O0-DEV-O2-BENCH) |
| Killswitch OFF arm byte-identical | ✅ (reframed) | No killswitch exists or is needed (§2) — stronger than byte-identical-when-off: the `.s` regen sweep (§4) proves the TEXT medium is byte-identical *unconditionally*, and the stamp is always-on by construction like `rt_proc_value`'s existing sentinel |
| A witness with a correct non-zero stamp, read from a core dump | ✅ | §4: independent core reload, `v/mod_op/src_node` decoded and correct |
| Corpus m3/m4 unchanged | ✅ | §4: SNOBOL4 and Icon exactly match pre-row baseline; Prolog's pre-existing flakiness documented, not caused by this row |
| `make pristine` EXIT=0 | ✅ | §4, five times |
| FINDING states the by-shape census before and after | ✅ | §1 (before: every site zero-stamped); §2 (after: 29/30 stamped, 1 named exception) |

## 6. Follow-ups, named and routed rather than silently skipped

- **`x86_alu_rr` and `x86_and`** share `x86_cmp_imm`'s pre-fix defect shape (no 8-bit register detection) and are
  unproven-but-plausible risks for the next template that requests an 8-bit register in a `cmp`/`test`/`mov`/`and`
  reg-reg or reg-imm form. Not fixed here — no call site currently exercises them with an 8-bit register, per the
  same "measure, don't assume" discipline this row's own bug hunt depended on.
- **`kind_names[]` is not extended** for the 130+ range. A future debug tool printing "who minted this" for a
  hand-written-runtime stamp needs its own bounds check or its own small lookup table; deferred rather than bundled.
- **`rt_defer_get_pat_fn`'s `.Ldfpf_null`** (§1b) is the one census site left deliberately unstamped, for a stated,
  measured reason (encoding-size growth on a leaf with no speed claim either way).
- **`rtx_zdp.S` is missing the `.section .note.GNU-stack,"",@progbits` trailer** every sibling `.S` file in this
  directory carries (linker warning observed during this row's builds: "missing .note.GNU-stack section implies
  executable stack"). Pre-existing, unrelated to this row's edits (this row made zero changes to `rtx_zdp.S`, which
  has no DESCR_t mint sites at all), noted here only because it was seen along the way.
- **`descr-stamp-fields`'s own §3 hazard** (11 `cmp,e*,(long)0` sites in `src/templates/bb_*.cpp` testing the whole
  tag word against zero as a DT_SNUL stand-in) is untouched by this row — it is a template-emitted zero-test
  pattern, not an asm mint site, and stays that row's named follow-up, not this row's.
