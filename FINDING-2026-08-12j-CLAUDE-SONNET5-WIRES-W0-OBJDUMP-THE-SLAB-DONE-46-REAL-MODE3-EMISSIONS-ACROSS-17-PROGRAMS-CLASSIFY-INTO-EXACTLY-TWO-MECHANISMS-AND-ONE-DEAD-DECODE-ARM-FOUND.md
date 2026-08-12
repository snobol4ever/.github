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


## ADDENDUM (same session, continuation) — `x86_asm.h` FULLY CLASSIFIED, 23/23 OCCURRENCES, READY FOR THE WHITELIST DECISION

The optional cleanup this finding flagged is now **landed** (SCRIP `825ab0a4`): `x86_store_cursor_mirror()`
and its `XK_R10MIR` decode arm deleted (zero live callers — the one caller that could reach it,
`xa_flat.cpp:249`, already routed around it by its own comment). Proof of safety: `test_gate_em_template_byte_
identity.sh` PASS=4/4 before and after · the same 17-program mode-3 runtime set (this finding's sample)
byte-for-byte identical stdout+rc before/after · `test_smoke_compile_hello_all_langs.sh` PASS=6/6 · all three
RULES.md-mandated `.s` regen scripts (benchmark/feature/demo) report zero artifact drift (one pre-existing
EMIT-FAIL on `coverage_sno_nodes.s` and one pre-existing SKIP on `json.s`, both confirmed to reproduce with
the edit absent — not caused by this change).

This shrinks `x86_asm.h`'s honest sweep-debt count from 25 occ/17 lines to **23 occ/15 lines**. Every one of
those 23 is now traced to a real source line and classified, closing out the "x86_asm.h internals" half of
W-0's remaining decision:

| Real line(s) | Occurrences | Content | Class |
|---|---|---|---|
| 46-47 | 4 (`r10d`,`r10`,`r11d`,`r11`) | register-name string → number decoder | (3) name infrastructure |
| 57 | 2 (`r10b`,`r11b`) | same decoder, byte-width forms | (3) name infrastructure |
| 318 | 1 (`r11`, inside a `static_assert` message string) | ABI-drift self-check comment-string, not code | (3) infrastructure (diagnostic text) |
| 368 | 1 (`r10`) | RTCC writeback: `mov [rax+56],r10` | RTCC veneer (save half) |
| 369 | 1 (`r11`) | RTCC writeback: `mov [rax+64],r11` | RTCC veneer (save half) |
| 377 | 1 (`r11`) | RTCC reload: `mov r11,[rip+g_rtcc_block]` — block-base load | RTCC veneer (reload half) |
| 378 | 1 (`r11`) | RTCC reload: `mov r8,[r11+40]` — r11 as block base | RTCC veneer (reload half) |
| 379 | 1 (`r11`) | RTCC reload: `mov r9,[r11+48]` — r11 as block base | RTCC veneer (reload half) |
| 380 | 2 (`r10`,`r11`) | RTCC reload: `mov r10,[r11+56]` — r11 base, r10 destination | RTCC veneer (reload half) |
| 381 | 2 (`r11`,`r11`) | RTCC reload: `mov r11,[r11+64]` — r11 as both block base and restored value | RTCC veneer (reload half) |
| 769 | 1 (`r11`) | DC-fn call stub: `movabs r11,&slot; call [r11]` — r11 used as a scratch indirect-call pointer, comment states "r11 is caller-saved and dead at every site" | RTCC-adjacent scratch, already self-documented as safe |
| 1385 | 2 (`r10`,`r11`) | 64-bit register name table (decode/encode infra) | (3) name infrastructure |
| 1386 | 2 (`r10d`,`r11d`) | 32-bit register name table | (3) name infrastructure |
| 1387 | 2 (`r10b`,`r11b`) | 8-bit register name table | (3) name infrastructure |

Sum check: 4+2+1+1+1+1+1+1+2+2+1+2+2+2 = **23**, matches the gate's own count exactly.

**23/23 accounted for. Zero unclassified. Zero ambiguous.** Three categories:
- **Register-name infrastructure** (13 occ: lines 46-47, 57, 318, 1385-1387) — string tables and decoders that
  must spell every GPR name, including r10/r11, to do their job. These can never be "cleared" by any wire
  reachability argument because they are not wire USES at all — they are the encoder's own vocabulary. This is
  class (3) from the whitelist header ("x86_asm.h internals — the encoders themselves; they name every
  register by construction") applied literally.
- **RTCC veneer** (9 occ: lines 368-369, 377-381) — the writeback/reload machinery that IS the mechanism
  making it safe to cross into C with the wire pair live. This is the thing WIRES' own charter cites as owned
  "HERE per the s14 arbitration: safe config = RTCC-ON and wire capture/restore, neither alone." Licensing
  this is not scope creep — it is licensing the seat's own named mechanism.
- **DC-fn call stub** (1 occ: line 769) — a single self-documented scratch use of r11 as an indirect-call
  pointer, distinct from the veneer proper, with the caller's own comment already asserting the safety
  argument ("r11 is caller-saved and dead at every site"). Small enough to fold into either bucket at the
  reviewer's discretion, or list as its own line-item — flagged separately here so nothing gets silently
  absorbed into the larger RTCC justification without its own read.

**Recommendation for the whitelist entry** (not written to `wreg_claim_whitelist.txt` this session — a
licensing act belongs to the explicit decision, not a data-gathering pass):
```
x86_asm.h   3   occ=23   OP5-sN-WIRES   register-name infrastructure (13 occ: decode/encode tables,
                                         diagnostic assert text) + RTCC veneer save/reload (9 occ: the
                                         s14-arbitrated wire-preservation mechanism itself, WIRES' own
                                         charter) + DC-fn call-stub scratch (1 occ, self-documented safe).
                                         Every occurrence traced to real line + content, table in
                                         FINDING-2026-08-12j addendum. Zero ambiguous, zero ordinary-scratch
                                         uses found.
```
This is a one-line edit, `occ=23`, once approved.

## NEXT SEAT

1. **Decision needed (Lon):** write the `x86_asm.h` whitelist line — data is now 100% complete for this call
   (the per-line table above). Every one of the 23 remaining occurrences is either register-name
   infrastructure or the RTCC veneer WIRES' own charter already owns; recommended entry text is above, ready
   to paste into `wreg_claim_whitelist.txt` once approved.
2. **If a permanent objdump gate is wanted:** turn the gdb-dump-and-scan pattern into
   `scripts/test_gate_wreg_claim_binary.sh`, run over a fixed program set (suggest the 17 named here, or the
   full `probe/bb/` D-family), asserting the same "every occurrence classifies as CLASS-D or RTCC-veneer"
   property this finding establishes by hand. This is new-instrument work, not sweep work — flagged, not done,
   pending the whitelist-policy decision it depends on.
3. **W-0's remaining open item after this:** the whitelist-policy decision from s35 (does "product-wide" mean
   clearing Prolog off r10/r11 even where SNOBOL4 provably cannot reach it) is untouched by this session and
   still the actual blocker for `--strict` ever going green. RTX (223/223) + template raw-byte (46 slabs) +
   x86_asm.h (23/23 classified) are ALL data-complete now — this is purely a policy call away from `--strict`
   going green product-wide.
