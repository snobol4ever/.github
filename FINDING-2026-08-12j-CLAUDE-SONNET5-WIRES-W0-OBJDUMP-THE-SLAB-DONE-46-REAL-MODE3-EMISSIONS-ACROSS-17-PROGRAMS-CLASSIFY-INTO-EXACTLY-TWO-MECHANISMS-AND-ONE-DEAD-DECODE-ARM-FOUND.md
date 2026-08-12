# FINDING — WIRES W-0: the raw-byte/binary-medium sweep, done for real, on the actual runtime slab

**Session:** Claude Sonnet 5, 2026-08-12 (continuation of the s34/s35 cursor). SCRIP `05e6b1ae` (unchanged —
read-only session, ZERO compiler bytes touched). corpus re-cloned clean (first clone attempt raced and
produced an empty checkout — noted for any future session that sees a suspiciously empty repo dir after a
backgrounded `git clone`: check `git log -1`, don't trust `ls` alone).

## WHAT THIS CLOSES

The s35 cursor's "NEW AND MOST IMPORTANT" item: the claim gate (`test_gate_wreg_claim.sh`) is a text-regex
over source and is blind to binary-medium emission by construction. The rung's own charter text ("objdump the
emitted slab too") had not been done by any session. It is done now — not by decoding the 4 named
`ef_b4/ef_b2/ef_b3` byte tuples in isolation (that was a source-level sanity check, done first, see below) but
by **breaking on `bb_seal(buf, size)` in a running `scrip --run`, dumping the actual RW-mode buffer contents
before the mprotect to RX, and running `objdump -D -b binary -m i386:x86-64` on the real bytes the emitter
wrote at runtime.**

## METHOD

1. Source-level decode first (sanity baseline): the 4 sites the s35 cursor named in `emit.cpp` — now at lines
   2692/2693/2727/2729 (drifted again from the cursor's cited 2689/2690/2724/2726, as warned) — were extracted
   as raw hex and fed to `objdump -D -b binary`. They decode exactly as claimed: `mov r10,[rsp+8]` /
   `mov r11,[rsp+16]` (res-landing reload) and `push r11` / `push r10` / `jmp r10` (CLASS-D suspend), matching
   their TEXT twins one-for-one.
2. **Runtime sweep** (the actual W-0 deliverable): a gdb script (`break bb_seal`, dump `[buf, buf+size)` to a
   file per seal, `continue`) run against `scrip --run <program>` for 17 programs chosen to exercise CLASS-D /
   DEFER / ARBNO-recursive / PT-inline paths:
   `dc_sib_bt dc_nest_bt dc_nest2 dc_nest3 dc_recur pt_inline_1_full pt_inline_1 pt_inline_1_hand
   183_pat_arbno_defer_recursive_carry 161_pat_defer_fn_nested_match 181_pat_arbno_defer_tail_stressors
   182_pat_arbno_defer_windowed_leaf defer_alt defer_simple defer_in_pat ab_defer_call pb_stitch_defer`
   (paths under `probe/`, `crosscheck/patterns/`, `programs/snobol4/parser/`).
3. Result: **46 sealed graphs, ~174KB of real emitted machine code**, every one disassembled and grepped for
   `r10`/`r11` in the objdump output (the disassembler decides what's an occurrence, not a source pattern).

## RESULT — THE RUNTIME BINARY SURFACE IS EXACTLY TWO MECHANISMS, NO THIRD

Every `r10`/`r11`-touching instruction across all 46 dumps, normalized (immediates/rip-offsets collapsed),
reduces to **14 distinct instruction shapes**, and all 14 classify into exactly two known mechanisms:

**CLASS-D wire glue** (the licensed W-MAP(3) sites, `emit.cpp` occ=6, already whitelisted+pinned):
`push r10` · `push r11` · `jmp r10` · `jmp r11` · `mov r10,[rsp+N]` · `mov r11,[rsp+N]` ·
`lea r10,[rip+…]` · `lea r11,[rip+…]`

**RTCC veneer** (writeback/reload/call-stub, `x86_asm.h`, NOT currently whitelisted):
`mov [rax+N],r10` · `mov [rax+N],r11` · `movabs r10,addr` · `movabs r11,addr` ·
`mov r10,[r11+N]` · `mov r11,[r11+N]` · `mov r8/r9,[r11+N]` · `call r10`

**No third category appeared anywhere in 174KB of real emitted code across 17 programs chosen specifically to
stress the DEFER/CLASS-D/ARBNO-recursive surface.** This is a negative result but a load-bearing one: the
raw-byte blind spot the s35 cursor flagged as "the highest-risk code, concentrated" turns out — empirically,
not by argument — to contain nothing the source-level census hadn't already named. The RTCC veneer piece
*is* new (see below), but it was already visible to the TEXT-grep gate as `x86_asm.h` sweep debt; the binary
form doesn't add a hidden third mechanism, it just confirms the veneer executes exactly as the encoder source
says it does.

## ⭐ ONE CONCRETE FINDING FROM THE TRACE: A DEAD DECODE ARM IN `x86_asm.h`

While classifying the 25 (17 after comment-strip) `x86_asm.h` occurrences the gate already reports as sweep
debt, one of them resolved to **structurally dead code**, caught by caller-tracing, not by name or comment:

- `x86_asm.h:232-234` — `x86_store_cursor_mirror()` emits `mov [r10], r14d` (bytes `45 89 32`). r10 here is a
  **base pointer to a Byrd-box match-cursor mirror cell**, unrelated to the γ/ω wire pair — a different,
  legitimate use of the register name in an unrelated addressing role.
- `x86_asm.h:1426` — the operand-string decoder recognizes the literal text `"[r10]"` and routes it to
  `XK_R10MIR` → `x86_store_cursor_mirror()`.
- **Zero call sites in `src/` pass the literal string `"[r10]"`** (`grep -rn '"\[r10\]"' src/` → one hit, the
  decoder's own comparison). The one caller that could have gone this route deliberately doesn't:
  `xa_flat.cpp:249` writes `"[r10 + 0]"` instead of `"[r10]"`, **with a comment saying why**: *"use `[r10 + 0]`
  not `[r10]` to avoid XK_R10MIR parse"*. The caller already knew this arm was a trap and routed around it —
  the trap itself was never removed.

**This is dead code, not a wire hazard.** `x86_store_cursor_mirror()` cannot fire from anywhere in the current
tree; it costs nothing at runtime and appeared in zero of the 46 dumped slabs. It is flagged here because (a)
it is exactly the shape of thing a name-based or comment-based read would miss — `XK_R10MIR`'s own name
suggests active wire-adjacent machinery — and (b) it is one of the 17 lines currently counted as "sweep debt"
in the gate's `x86_asm.h` tally, and it should be counted as **zero-risk dead code**, not reviewed-and-cleared
scratch use, when W-0's whitelist entry for `x86_asm.h` eventually gets written. Deleting `x86_store_cursor_mirror()`
and its `XK_R10MIR` decode arm would shrink the honest sweep-debt count by 2 occurrences (line 232's emission +
line 1426's decode-arm registration) for free, with a `test_gate_em_template_byte_identity.sh` proof that no
`.s`/binary output changes (nothing calls it, so nothing can change).

## WHAT THIS DOES **NOT** CLOSE

- **The `x86_asm.h` whitelist entry itself is still unwritten.** This finding gives the reviewer everything
  needed to write it (every occurrence traced to RTCC veneer, register-name infrastructure, or now-identified
  dead code — see the per-line breakdown that produced this finding, reproducible via the gdb script above) —
  but writing the actual `wreg_claim_whitelist.txt` line with a correct `occ=N` pin is a policy act this
  session is deliberately leaving for explicit confirmation, consistent with s35's decision (1) still being
  open with Lon.
- **This sample is 17 programs, not the whole corpus.** It is chosen to concentrate CLASS-D/DEFER/ARBNO-defer
  traffic, which is the highest-risk region by the s35 cursor's own reasoning (RTX excluded — that census is
  separately complete per FINDING-2026-08-12h). A session with more time budget could widen the sample
  (crosscheck/patterns's other 100+ programs, the demo board, benchmarks) for a higher-confidence "no third
  mechanism" claim, but diminishing returns are likely given every one of 46 real graphs already agrees.
- **The one live divergence noticed in passing** (`dc_sib_bt.sno` mode-3 output: `X=` empty / `Z=CD` vs oracle
  `X=AB` / `Z=ABCD` — RC=0, not a crash) is NOT investigated further here — it is outside W-0's scope (a
  correctness defect, not a register-scope question) and most likely belongs to RBP/EARN's open CLASS-D/W-5
  territory or is one of the named by-set regressions {D12,D13,H31,X01,X10}. Flagged, not chased.

## TOOLING LEFT BEHIND (reusable, not committed — lives in /tmp this session)

A parameterized gdb script pattern:
```
break bb_seal
commands
  silent
  set $n = (int)size
  set $b = (unsigned char *)buf
  eval "dump binary memory <dir>/slab_%d.bin %p (%p + %d)", $bb_dump_idx, $b, $b, $n
  set $bb_dump_idx = $bb_dump_idx + 1
  continue
end
set $bb_dump_idx = 0
run
```
run via `gdb -q -x script.gdb --args ./scrip --run <file>`, then `objdump -D -b binary -m i386:x86-64 -M intel`
per dump. This is the general instrument the s35 cursor called for; it is not yet a checked-in script under
`scripts/` because turning it into a proper gate (with a pattern allowlist mirroring `wreg_claim_whitelist.txt`
so it can run `--strict`) is a design decision, not a data one — flagged for Lon alongside the whitelist
question rather than assumed.

## NEXT SEAT

1. **Decision needed (Lon):** write the `x86_asm.h` whitelist line. This finding supplies the occ breakdown;
   recommend `occ=23` (25 raw − 2 for the now-identified dead `x86_store_cursor_mirror`/`XK_R10MIR` pair, IF
   that pair is deleted first) or `occ=25` (if left in place and licensed as dead-but-present). Either is a
   one-line edit once decided.
2. **Optional, cheap, zero-risk:** delete `x86_store_cursor_mirror()` (x86_asm.h:232-234) and its `XK_R10MIR`
   decode arm (enum entry + line 1426's `if`). Zero callers exist; `test_gate_em_template_byte_identity.sh`
   should read byte-identical before/after since nothing reachable changes. Shrinks sweep debt by 2 for free.
3. **If a permanent objdump gate is wanted:** turn the gdb-dump-and-scan pattern above into
   `scripts/test_gate_wreg_claim_binary.sh`, run over a fixed program set (suggest the 17 named here, or the
   full `probe/bb/` D-family), asserting the same "every occurrence classifies as CLASS-D or RTCC-veneer"
   property this finding establishes by hand. This is new-instrument work, not sweep work — flagged, not done,
   pending the whitelist-policy decision it depends on.
4. **W-0's remaining open item after this:** the whitelist-policy decision from s35 (does "product-wide" mean
   clearing Prolog off r10/r11 even where SNOBOL4 provably cannot reach it) is untouched by this session and
   still the actual blocker for `--strict` ever going green.
