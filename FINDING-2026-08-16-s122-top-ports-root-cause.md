# FINDING — TOP-PORTS ROOT CAUSE (s122): the s118 double failure was ONE mechanism plus ONE accident, and it is the BINARY ENTRY POINT

**Supersedes the "Suspects for the next seat" section of `FINDING-2026-08-16-s118-top-ports.md`.** That file's mechanism map is accurate and still worth reading; its three suspects are not. Two of them cannot produce the failure that was actually measured, and the third was never needed.

## The falsification (two lines of source, no experiment required)

s118 measured its cleanest repro as **`fibonacci` m3 rc=1 under the ports-only variant**. m3 is BINARY. Both leading suspects are TEXT-medium-only:

- `x86_asm.h:926` — `inline void x86_begin() { if (!MEDIUM_BINARY) _.x86_uid = g_flat_node_id++; }` — uids are minted **only when not binary**.
- `emit.cpp:2733` — `if (g_is_text) g_emit_pos += 7;` — the compensation moves **only in text**.

Neither can fire during a binary run, so neither can explain a binary rc=1. Suspect 2 (ZD SR-role staging) is real but belongs to a *different* witness (`cap_imm_nret` under the full variant), not to this one.

## The actual mechanism

`emit.cpp:3413`, the binary tail of `emit_chain`:

```c
bb_seal(buf, (size_t)nbytes);
bb_pool_trim_last(buf, FLAT_BUF_MAX, (size_t)nbytes);
return (bb_box_fn)buf;
```

**In BINARY the chain's entry point IS the first byte emitted.** Two corroborating facts:

- There is no `main:` symbol in m3 at all — `main:`/`main_init:` are `emit_textf` on the m4 driver path (`scrip.c:949`, `:990`), which mode 3 never executes.
- `lbl_α` is defined only under `text_externalise && g_is_text` (`emit.cpp:2730`), so in binary there is not even an α label to enter by name.

Hoist the ports above α and the buffer base becomes `main_β` → `jmp main_ω` → `exit(1)`. The program returns **rc=1 having executed no statement** — precisely the recorded ports-only signature.

## Why the FULL variant looked different

The s118 full variant carried "a one-jmp α_body bridge to `lbls[first_non_floater]`". That bridge *is* the fix, arrived at incidentally while solving the floater reorder. It restored the entry point, so fibonacci passed. The two variants were never two interleaved mechanisms — they were **one mechanism (binary entry hijack) plus one accident (the bridge that masked it)**. The full variant's residual `cap_imm_nret` break is the genuinely separate, still-real SR-staging coupling.

## The law this yields

⛔ **ANY emission hoisted above α in `codegen_flat_chain_body` MUST be preceded by a jmp into `lbl_α_body`.** `lbl_α_body` is the correct target because it is defined at `emit.cpp:2774` under `if (!bare)` with **no medium gate** — it is the only α-side label that exists in both media. `lbl_α` will not do.

Encoded as `bb_main_entry_bridge()` in `src/templates/bb_main.cpp` (SCRIP `90f31a5d`), emitted unconditionally as the first thing in the hoisted block.

## Second law, for the floater half (still open)

RETURN/FRETURN are `IR_DEFINE ival=1/2` (`emit_floater_kind`, `emit.cpp:64`) whose bodies are emitted **through the drive loop** by `bb_define.cpp` (role 1/2, lines 761-774). `zd_sr_role` claims the same ival values, and the drive loop mutates per-node staging accumulators in emission order. **Reordering the floaters therefore perturbs SR staging** — that, and not the uid stream, is what broke `cap_imm_nret` under the full variant. s122 held the floaters in place and `cap_imm_nret` is green in both arms, which is the confirming half of the experiment. Making them template stubs (Lon's `bb_main.cpp` proposal) removes them from the drive loop entirely and dissolves the coupling; that is the next rung.

## State at s122

`SCRIP_TOP_PORTS=1` opt-in, default OFF and byte-identical (fibonacci m4 `.s` md5 `a48740453935fb0999c070cac7c77cec` on both compilers). ON: fibonacci m3 rc=0, m4 links+runs; cap_imm_nret m3 == oracle; fibonacci/roman/func_call/cap_imm_nret all ON == OFF == oracle by md5. ⛔ ON-arm blast radius is 4 programs — **not** the corpus-wide md5 sweep a default flip requires.
