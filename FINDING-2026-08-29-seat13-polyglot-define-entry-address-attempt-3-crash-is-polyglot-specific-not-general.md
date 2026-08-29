# FINDING — polyglot DEFINE entry-address bug: attempt 3's new crash is polyglot-specific, NOT a general calling-convention gap

**seat13 · 2026-08-29 · row `polyglot-define-entry-address-wrong-in-merged-program` · SCRIP HEAD (unchanged from
session start — tree confirmed clean, `git status --short` shows only the unrelated, deliberately-preserved
`src/emitter/emit.cpp` from a different row)**

**No fix landed. Builds on `FINDING-2026-08-29-seat07-polyglot-define-entry-address-root-caused-not-cured.md`
(read first, not repeated here) — completes seat07's two concretely-recommended next steps, then adds a new,
significant result their own session didn't have time for: attempt 3's new crash does NOT reproduce on a
single-language program, only on a polyglot-merged one. This changes where the remaining bug most likely lives.**

## 1. Seat07's step (3): `x86_pair_loop()`/`x86_ro_seal_str()` are NOT a third consumer — read, ruled out

Both defined in `src/templates/x86/x86_asm.h` (:2294, :751). Neither reads `_.lbl_t0` or `_fn` (the
`rt_define_query`-sourced pointer) anywhere in their bodies. `x86_pair_loop()` only touches
`g_emit.xa_bb_emit_pair_{define,jmp}[]` (an unrelated deferred-pair-emission queue). `x86_ro_seal_str(int n,
const char *lit)` only takes an explicit string literal argument (`fname`/`_csv` at the two call sites in
`bb_define_bind()`) — it has no path to either shared field. Ruled out by direct reading, not by re-deriving
seat07's own trace.

## 2. Seat07's step (2): the attempt-3 crash, precisely pinned

Reproduced attempt 3 exactly (`bb_define_bind()`'s `blbl` computed as `fname + "_α"` directly when `_.lbl_t0`
is truthy, bypassing its stored value — the one-line change seat07's own `.s` diff already verified is
surgical). Rebuilt, reproduced the SIGSEGV (`rc=139`, matches seat07's report).

**First checked whether `fn` itself was actually wrong — it is not.** `gdb -batch -ex "break rt_define_site"`
shows `fn=0x40d2fa <n851_define_bx+214>` at the call. This LOOKS wrong (inside `n851_define_bx`, not a
separate `roman_α` symbol) but is a **display artifact, not a bug**: `gdb -ex "info address roman_α"` confirms
`roman_α` really is at `0x40d2fa` — it has no `.size`/symtab entry of its own (it's lexically nested inside
`n851_define_bx`'s single `.size` span in the `.s` output, `.size n851_define_bx, .-n851_define_bx` spanning
through `roman_α`/`roman_γ`/`roman_ω`), so gdb's nearest-preceding-symbol display shows ANY address in that
whole range as `n851_define_bx+N`. Same general shape as this row's sibling `pascal-m4-for-spine-leak`'s own
"a ζ pop lands textually next to the wrong label" trap — a different mechanism, same lesson: an instrument's
display convention misattributed the address, the address itself was right. **Attempt 3's entry-address fix
is confirmed correct**, independently of this session's own re-derivation.

**The actual crash, `run` to completion under gdb:** SIGSEGV at `0x40d359 <n851_define_bx+309>` —
`mov (%rdi),%rax` — which resolves (via the `.s` source, not just gdb's misleading label) to a specific
instruction sequence *inside `roman_α`'s own prologue body* (not `n851_define_bx`'s literal DEFINE-statement
code):
```
mov   rdx, [rcx + 0]
lea   r8,  [rsp + 80]
cmp   rdx, 0;  jbe .Ldefine_α_920_10
mov   rdi, [rcx + 24]        # rcx = 0x40e4bf at the crash (seat07's own gdb read, reproduced)
add   rdi, r8
mov   rax, [rdi + 0]         # <-- faults here
```
`rcx` is the value `roman_α`'s prologue saved from its OWN entry (`mov [rsp+48], rcx`, immediately re-read as
`[rcx+0]`) — i.e. **whatever was in `rcx` at the moment execution jumped into `roman_α`.**

## 3. Where `rcx` actually comes from: the call site never sets it to an argument-record pointer

Traced the call site for `roman('1776')` directly in the `.s` (anchored on the literal string `"1776"`,
`n889_call_proc_staged_α`, the `CALL_PROC_STAGED` node — the compiled form of SNOBOL4 `roman(ARG)` call
syntax). After `rt_proc_call_open_slim` returns the resolved entry address in `rax`, the site does:
```
lea rcx, [rip + L7]; push rcx
lea rcx, [rip + L6]; push rcx
lea rcx, [rip + L7]; push rcx
lea rcx, [rip + L6]; push rcx;  jmp rax
```
— four `push`es building the γ/ω continuation pair on the stack (the "s110 floater pair" mechanism, per the
inline comment at this exact site), with `rcx` used purely as scratch for each `lea`. **`rcx` is never set to
point at anything resembling an argument record before the `jmp rax`** — it's simply left holding the last
`lea`'d label address (`L6`'s own address), which is exactly the "looks like a raw code address"
`0x40e4bf` seat07 already observed. Confirmed this is not an isolated omission: grepped every `"rcx"` use in
`src/templates/bb/bb_call_proc_staged.cpp` (the whole file, all arms — TINY shim, SLIM tail, LEGACY flat-glue,
each gated by its own killswitch/condition per the file's own extensive comments) — **every single one is this
same scratch-for-push pattern.** No arm of this template ever constructs a persistent argument-record pointer
in `rcx` (or hands one to the callee any other way this session found).

## 4. The open question this raises, answered empirically: is this general, or polyglot-specific?

The row's own task file explicitly flagged this as worth checking ("whether a single-language, mode-4-graded,
recursive Gimpel-idiom DEFINE already exists somewhere in the corpus and simply doesn't trigger this ... is
itself worth checking before assuming this is polyglot-only") but no session had done it yet. Two minimal,
purpose-built witnesses, both with attempt 3 applied:

- **`recur.sno`** (single-language SNOBOL4, same idiom as `roman`: `DEFINE('cnt(n)t')`, recursive
  `t = cnt(n-1)`, Gimpel-inline): `--run` **and** `--compile` (linked, executed) both print the correct
  `xxxxx` for `cnt(5)`, **rc=0, no crash, either mode.**
- **`recur_poly.scrip`** — the *identical* SNOBOL4 section, wrapped as a polyglot program (paired with a
  trivial Icon `main` and a trivial Prolog `main`, same fenced-block format as `roman.scrip`): `--run` hits
  the *other*, independent bug (`polyglot-main-collision-bug1-vs-bug2` — only one section's `main` executes,
  same shape seat01 already documented, not this row's concern). **`--compile` (linked, executed): SIGSEGV,
  rc=139 — same crash class, reproduced on a witness one-tenth `roman.scrip`'s size.**

**This settles the question the task file left open: attempt 3's new crash is not a general defect in
`bb_call_proc_staged`'s calling convention — the identical recursive-DEFINE machinery works correctly
standalone. Something about polyglot merging specifically changes what happens at this call site or in
`roman_α`'s own prologue.** Given `bb_call_proc_staged.cpp` itself is language-agnostic template code (no
`LANG_*`/`:lang` branching per `emit_no_lang`), the most likely mechanism is **shared emitter global state
(`g_emit.lbl_t0` is the field already implicated once, by seat07's attempt 2 — or a sibling field with the
same shape) carrying a stale or cross-language-contaminated value across the language-section boundary during
a merged compile**, not a per-language code-path difference. Not traced further this session — this is the
next concrete step, not a re-opening of steps 1-2 above.

## 5. What's actually needed, for whoever picks this up

1. **Do not re-attempt steps 1-2 above** (pin the crash location, check `x86_pair_loop`/`x86_ro_seal_str`) —
   both done, both answered, receipts in §1-2.
2. **Build `recur_poly.scrip` (reproduced here in full, trivially small) with `SCRIP_ZD_MAP`-style or a
   temporary diagnostic dump of `g_emit.lbl_t0` (and any field near it in the same struct) at both (a) the
   point `n851_define_bx`/SNOBOL4's own `DEFINE` statement compiles, and (b) the point
   `n889_call_proc_staged_α`-equivalent compiles** — single-language first (should show a sane, stable value
   throughout SNOBOL4's own compile), then polyglot (check whether Icon's or Prolog's OWN compilation touches
   the same field, or whether merge-order affects what SNOBOL4 sees). This is the direct empirical answer to
   §4's hypothesis, not yet gathered.
3. **The two witness files** (`recur.sno`, `recur_poly.scrip`) are far cheaper to iterate on than `roman.scrip`
   — copy them into the corpus (or reference this FINDING for their exact content) rather than re-deriving
   minimal witnesses from scratch.
4. Attempt 3's own architecture (separate role 6's `fn` from role 5's continuation-target, stop sharing
   `_.lbl_t0`'s VALUE) is still very likely correct and still needs to land eventually — the entry-address half
   of this bug is fixed by it, confirmed independently in this session too. The blocker is now specifically
   "what does polyglot merging do differently to a shared emitter field," not "is attempt 3's approach right."
5. Regression scope unchanged from seat06/seat07's own notes: full `test_gate_polyglot_demos.sh` + SNOBOL4
   blocking set + single-language explicit-DEFINE programs before any fix is considered landable.
