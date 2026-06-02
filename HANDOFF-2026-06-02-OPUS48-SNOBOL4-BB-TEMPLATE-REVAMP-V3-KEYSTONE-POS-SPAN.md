# HANDOFF — SNOBOL4 BB x86() template-revamp V3: internal-label KEYSTONE + POS + SPAN

**Author:** Opus 4.8 (third developer). **Date:** 2026-06-02. **Repo tips after this session:**
SCRIP `origin/main` = `24b9c78`; `.github` = the commit carrying this file.

This continues the x86()-self-encoding revamp (see V1 and V2-NO-PBB). It lands the shared **looping-box
keystone** plus two converted boxes (**POS**, **SPAN**), and corrects the **mode-4 "by design" verbiage**.

---

## 1. What the revamp is (recap)

Each BB template becomes ONE `return` per `PLATFORM_*`, a pure `x86(mnem, …)` string concatenation, with
NO `bb_bin_t` and NO template locals in the x86 arm. The medium switch is invisible to the template. The
hand-counted offset table is replaced by IN-BAND RECORDS in the returned string:

- `L <len> <bytes>` — literal code bytes
- `J <id>` — rel32 patch to a label (the opcode byte precedes it via an `L`)
- `D <id>` — define a label here (0 bytes)

`bb_emit_x86(s)` walks the records and DISCOVERS each byte position as it copies, so no offset can drift.
Ports are ids `0=α 1=β 2=γ 3=ω`. Converted boxes are **pBB-free**: they read `_` (g_emit) only; the
dispatcher `walk_bb_node` (emit_core.c) populates `_.nid/op_sval/op_ival` before each call, and converted
boxes are invoked argument-free (`bb_pat_pos();`).

Pre-existing pBB-free exemplars: `bb_pat_rem`, `bb_pat_len`, `bb_pat_any`, `bb_pat_notany`, `bb_lit`.

---

## 2. KEYSTONE — `a1779e6` (additive, zero-regression; unblocks looping boxes for ALL FOUR sessions)

In `src/emitter/BB_templates/x86_asm.h` unless noted.

### 2a. Internal (box-local) labels
- `#define X86_INTERNAL_BASE 4`, `X86_INTERNAL_MAX 16`; `struct x86_lbl{int n;}`; ctor `L(n)`.
- `x86_internal_name(n)` → `.Lx<uid>_<n>`; `x86_jmp_id/x86_jcc_id/x86_deflabel_id` emit `L`+`J`/`D` records
  with `id = X86_INTERNAL_BASE + n` (BINARY) or named labels (TEXT).
- `x86_begin()` sets `_.x86_uid = g_flat_node_id++` (TEXT only); a looping box's extern calls it BEFORE
  building the string.
- Walker change in `bb_emit_x86`: `x86_label_for(id, internal)` maps `id < 4` → port label (`x86_portlbl`),
  `id ≥ 4` → a box-local `bb_label_t internal[X86_INTERNAL_MAX]` allocated in the walker (names `.Lxi%d`,
  offset UNRESOLVED). Forward AND backward refs resolve via the EXISTING `bb_label_define` /
  `bb_emit_patch_rel32` + the global `bb_patch_list` — no new patch machinery.
- Front-end overloads: `x86("jmp"/jcc/"def", L(n))`.

### 2b. ζ-frame `[r12+off]` memory ops (PER-BOX LOCAL STORAGE / NO-VALUE-STACK)
- `x86_r12_modrm(regfield, off)` — `off==0`→mod00, int8→disp8, else disp32; SIB `0x24`, REX.B.
- `x86_frame_mov_imm` (41 C7…), `x86_frame_store` (41 89…), `x86_frame_load` (41 8B…),
  `x86_frame_add_imm` (41 83/81 /0), and (added with SPAN) `x86_frame_add_to_reg` (41 03 /r).
- `struct x86_frame{int off;}`; ctor `FR(off)`. Front-end: `x86("mov", FR(o), imm)`, `x86("mov", FR(o), reg)`,
  `x86("mov"/"add", reg, FR(o))`, `x86("add", FR(o), imm)`.
- These are register-relative, so the SAME bytes serve BINARY and TEXT (no `movabs` to a process address, no
  rip-rel `.data`). This is the re-entrancy fix for match-state scratch.

### 2c. Misc
- `x86_cmp_imm(reg, imm)` — imm8 (0x83 /7), eax (0x3D), else 0x81 /7. Wired into the `(reg, long)` overload.
- `int bb_slot_claim(int bytes)` in `emit_bb.c` — bumps `g_flat_slot_count` by `bytes`, returns the offset,
  and is NOT in the node-keyed slotmap (so a pBB-free box can claim private scratch with no `IR_t*`). Declare
  locally per-box: `int bb_slot_claim(int bytes);`.
- `sm_emit_t` gained `int x86_uid;` and `int x86_scratch_off;` (emit_globals.h).

**Every new encoder was byte-verified against `as` (assemble Intel-syntax `.s` → `objdump -d`) BEFORE use.**

---

## 3. Converted boxes

### `bb_pat_pos` — `195bea4` (LOOP-FREE register-migration reference)
POS `cmp r14d,N`; RPOS `mov ecx,r15d / sub ecx,N / cmp r14d,ecx`; then `jne ω / jmp γ / def β / jmp ω`.
Cursor δ=R14d and length Δ=R15d read straight from the callee-saved regs (legacy `[r10]` cell and `&Σlen`
bake removed). RPOS is `sval[0]=='r'` (authoritative per `lower_pat_dcg.c`), NOT `ival!=0`.
Verified mode-3: `POS(0)'abc'=Xde`, `POS(2)'c'=abXde`, `'cde'RPOS(0)=abX`, `'b'POS(0)` fails.

### `bb_pat_span` — `3769d21` (box) + `24b9c78` (its encoders) — FIRST LOOPING box; reference for all sessions
Internal labels `loop=L(0)`, `done=L(1)`. Match-state z (matched length) and zo (β-undo origin) moved from a
process-global deque (`movabs` to a fixed addr) to ζ-frame z@`[r12+off]`, zo@`[r12+off+4]` via
`bb_slot_claim(16)` → BINARY==TEXT and re-entrant. cset/strchr reuse the any-style RO load (`movabs` in BINARY
/ `lea[rip]` in TEXT — REG-RO unifies later). Encoders added (byte-verified): `jle`(0F 8E), `add reg,reg`(01/r),
`add reg,[r12+off]`(03/r). Extern: `x86_begin(); _.x86_scratch_off = bb_slot_claim(16); bb_emit_x86(...)`.
Verified mode-3: `SPAN('a')/'aaabbb'=Xbbb`, `SPAN('ab')=X`, `SPAN('xyz')/'xyz123'=Q123`, `SPAN('a')/'bbb'` fails,
and **`SPAN('a')'ab'/'aaab'=X` (β GIVE-BACK)** — the backtrack test exercises internal labels + ζ-scratch + β
port end-to-end.

> ⚠ **Build note:** the three SPAN encoders were inadvertently left unstaged in `3769d21` and added in
> `24b9c78`. The remote TIP `24b9c78` builds; `3769d21` alone does not. Always build from the tip.

### Per-box recipe (followed by both conversions)
1. Write a pBB-free `bb_pat_X_str()` reading `_` (accessors for op_ival/op_sval/nid). x86 arm = an
   `IF(MEDIUM_TEXT, s_1asm(α:)+s_comment(...))` header + a chain of `x86(...)` calls (ratified regs δ=r14d /
   Δ=r15d / Σ=r13; internal labels via `L(n)`; ζ-scratch via `FR(off)` + `bb_slot_claim` in the extern +
   `x86_begin()` if looping). Other arms keep locals; translate `pBB->X` → `_.X`.
2. Extern `void bb_pat_X(void){ [x86_begin(); _.x86_scratch_off=bb_slot_claim(N);] bb_emit_x86(bb_pat_X_str()); }`.
3. `bb_templates.h` decl → `(void)`; `emit_core.c` dispatch → `bb_pat_X();` (SNOBOL4-owned line, conflict-free).
4. Any new encoder → add to `x86_asm.h`, byte-verify vs `as` FIRST.
5. `make scrip` (rc=0); verify semantics via direct `./scrip --run` mode-3 runs; run all gates; commit
   (**stage `x86_asm.h` too if it changed**); push.

---

## 4. mode-4 verbiage CORRECTION (Lon directive)

**mode-4 is NOT "aborting by design," and it is NOT inferior to mode-3.** The two modes are the SAME boxes in
two media — BINARY (mode-3, run in-process) vs TEXT (mode-4, relocatable) — emitted from one `x86()` body; for
the ζ-frame/REG-ratified boxes the bytes are identical. mode-4 already emits for Icon/Prolog. SNOBOL4 mode-4 is
pending ONE wiring step: LOWER emitting the four-port statement-BB graph directly (the emission scaffolding —
`codegen_flat_build` + the XA wrap templates — is intact). The earlier `sno_ring_to_tree` adapter was removed
(Lon directive), so until LOWER is wired the SNOBOL4 `--compile` path aborts — but that is a **narrow temporary
wiring gap, not a design limit**.

Corrected:
- `src/driver/scrip.c` — the SNOBOL4 mode-4 comment + the stderr abort message (no longer "Aborting (by design)").
- `GOAL-SNOBOL4-BB.md` — the stale historical note that claimed BOTH modes abort by design (mode-3 has NOT aborted
  since the `sno_flat_chain_build` re-wire) now carries a dated CORRECTION.

NOT changed: `src/runtime/core/eval_code.c:424` "Aborting (by design)" — that is a DIFFERENT, correct abort (the
removed global value stack, gone by FACT RULE; hitting it is a genuine violation).

Consequence for gate reporting: keep `MODE4_MIN=0` as a measured floor, but describe m4 0/6 as "pending the LOWER
wiring," never "by design."

---

## 5. Gate state (GREEN throughout; build `make scrip` then `make libscrip_rt`)
- SNOBOL4: m2 **7/7 HARD**, m3 5/6 (floor `MODE3_MIN=5`; `define` fails — known), m4 0/6 (floor `MODE4_MIN=0` —
  pending LOWER wiring).
- PAT-BB probes 3/3; `prove_lower2` PASS; `g_vstack`==0.
- The SNOBOL4 smoke does NOT exercise pos/span/tab/any (its "pattern" case is `S 'b' = 'X'` = bb_lit) — so
  POS/SPAN were verified by direct `./scrip --run` mode-3 programs (listed above), which is the authoritative check.

---

## 6. NEXT STEPS (SNOBOL4 x86() conversion remainder), in priority order

All map onto POS (loop-free) or SPAN (looping) — examples are ample.

1. **`bb_pat_abort`** — TRIVIAL: x86 arm = `x86("jmp",PORT_OMEGA)+x86("def",PORT_BETA)+x86("jmp",PORT_OMEGA)`;
   pBB-free; other arms `pBB->_`. Verify a pattern that hits ABORT fails; gate; commit.
2. **`bb_pat_tab`** — loop-free, like POS. TAB(N): `cmp r14d,N / jg ω / mov r14d,N / jmp γ / def β / jmp ω`
   (TAB requires δ ≤ N then sets δ=N). RTAB(N): `mov ecx,r15d / sub ecx,N / cmp r14d,ecx / jg ω / mov r14d,ecx /
   jmp γ / def β / jmp ω`. RTAB via `sval[0]=='r'`. NEEDS ONE NEW ENCODER: `mov r32,imm32` (e.g. `mov r14d,N` =
   `41 BF imm32`; B8+rd, REX.B if reg≥8) — byte-verify vs `as`. Legacy `[r10]`/`&Σlen` removed.
3. **`bb_pat_atp`, `bb_pat_arb`, `bb_pat_defer`** — loop-free legacy → REG-ratified + x86(). (@var assign /
   generator / deferred eval; read each box for its exact shape; arb/atp touch variable storage.)
4. **`bb_pat_break`** — LOOPING; follow SPAN. Plain BREAK ≈ SPAN with one loop; BREAKX is a TWO-loop scanner
   needing `L(0..3)`. Move z (and BREAKX's z_orig) from the `rt_cs_t` spare slots `[zeta+8]`/`[zeta+12]` to the
   ζ-frame via `bb_slot_claim`. NOTE break still legitimately sets `bb_cs_zeta` (it reads it at line ~78); decide
   whether to keep the cset object or switch wholly to raw-sval+ζ-frame like SPAN did.
5. **VARIABLE-LENGTH (separate define/jmp-pair design; shared with Icon/Prolog `xa_bb_emit_pair_*`):**
   `bb_pat_fence` (its pair-array path is the simplest instance), then `bb_pat_cat`, `bb_pat_alt`, `bb_match`.
   The open question is expressing the driver-supplied pair arrays (`g_emit.xa_bb_emit_pair_n/_jmp/_define`) as
   `x86()` `D`/`J` records in a loop. The niladic FENCE path (`α:jmp γ; β:jmp ω`) is trivial; the pair path is not.

---

## 7. Divvy-up (conflict-free; this session = SNOBOL4)
- **SNOBOL4:** bb_pat_cat, bb_pat_alt, bb_match (variable-length); loop-free remainder span✅/break/pos✅/tab/atp/
  arb/fence/defer/abort.
- **Icon:** bb_iterate, bb_binop_gen, bb_upto, bb_to/to_by, bb_alt, bb_seq, bb_every, bb_suspend, bb_succeed, bb_unop.
- **Prolog:** bb_builtin, bb_goal, bb_choice, bb_ite, bb_disj, bb_conj, bb_unify, bb_cut, bb_catch, bb_arith.
- **Raku:** bb_rk_gather, bb_nfa.

Each session edits only its own boxes; dispatch/decl inserts land on different lines; `x86_asm.h` is shared but
additive. **All three other sessions should rebase onto `24b9c78` to pick up the keystone** before converting any
looping/scratch-bearing box.

## 8. Handoff sequence reminder (RULES.md)
Mark GOAL steps `[x]`; update the watermark in the GOAL file ONLY; commit; `git pull --rebase && git push`
(code repos FIRST, `.github` LAST). Build: `make scrip && make libscrip_rt`.
