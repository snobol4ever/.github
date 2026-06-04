# HANDOFF 2026-06-04 (Sonnet 4.6) — ICN-SCAN-5 + ICN-SCAN-6

**SCRIP HEAD: `11922ec`** (two gated rungs: `aaa3b9b` ICN-SCAN-5 → `11922ec` ICN-SCAN-6,
individually gated/committed, no peer rebases needed this session — no orthogonal commits
landed on origin/main between session start and these pushes).
**Full detail = the two rung entries + Watermark in `GOAL-ICON-BB.md` (single source of truth).**

## Landed

1. **ICN-SCAN-5 (`aaa3b9b`)** — `bb_scan_match.cpp`: fstranl.r `match(s1)` {0,1}. α: len-check
   (`Δ−δ < len → ω`); `movsxd rcx,r14d; lea rsi,[r13+rcx]`; s1 sealed RO at index 0 via
   `x86_ro_seal_str(0,s1)` / `x86_ro_load_q("rdi",0)`; `mov rdx,len; push r10; call memcmp;
   pop r10; test rax,rax; jne ω`; `{DT_I, r14+1+len}` → slot → γ; δ untouched; β → ω.
   Driver arm: identical structure to `any` — IR_LIT_S sval → `op_name1`; `bb_slot_alloc16`.
   Safe-set: `match` admitted with `icn_scan_fn_lit_arg(nd, IR_LIT_S)`. `IR_SCAN_MATCH` off stub list.

2. **ICN-SCAN-6 (`11922ec`)** — `bb_scan_many.cpp`: fstranl.r `many(c)` {0,1}. α: `mov eax,r14d`;
   `L(0)`: cmp/jge to `L(1)`; `movsxd rcx,eax; movzx esi,[r13+rcx]`; cset RO at **index 2**
   (`x86_ro_load_q("rdi",2)` / `x86_ro_seal_str(2,cs)` — avoids L(0)/L(1) alias at indices 0/1);
   `push rax; push r10; call strchr; pop r10; test rax,rax; pop rax; je L(1)` — cursor preserved
   in rax across call (test uses strchr flags before pop restores cursor); `add eax,1; jmp L(0)`;
   `L(1)`: `cmp eax,r14d; je ω`; `{DT_I, p+1}` → slot → γ; δ untouched; β → ω.
   Driver arm: same as match/any. Safe-set: `many` admitted with `icn_scan_fn_lit_arg(nd, IR_LIT_S)`.
   `IR_SCAN_MANY` off stub list.

## Bug found and fixed (ICN-SCAN-6)

`strchr` returns in `rax`, clobbering the loop cursor stored in `eax`. First attempt used `eax`
directly as the cursor; after strchr returns a non-NULL pointer, `add eax,1` incremented the pointer's
low 32 bits, not the cursor. Fix: `push rax` (cursor) before call; `test rax,rax` while strchr result
is still in rax; `pop rax` to restore cursor (flags survive pop); `je L(1)` branches on the test.

## Key transferable findings

- **RO index must not alias L(n):** both use `X86_INTERNAL_BASE+n` as label IDs. A loop using L(0)
  and L(1) must seal RO data at index ≥2.
- **memcmp beats inline loop for match:** per NO-DUP-FORM-2, RT does value work. `memcmp` via
  `x86_call_ro` is simpler and correct; no new encoders needed.
- **push/pop to preserve a caller-saved cursor across a `call`:** flags set by `test` survive a `pop`;
  this pattern is safe and preserves the flags for the subsequent conditional jump.

## Gates (held at EVERY rung)

Corpus ALL THREE columns byte-identical set-diff at each rung: **m2 129 HARD / m3 15 PASS+150 EXC /
m4 22 PASS+89 EXC — zero PASS-set drift any mode any rung**. Smokes Icon m2 12/12 HARD · Prolog 5/5 ·
broker 32. All structural gates green: bb_bin_t=0 · no-handencoded `--strict` (non-Prolog-lane) ·
g_vstack=0 · no-stack 10≤127 · one-reg-frame 0≤21 · prove_lower2 · FACT=0.

## NEXT = ICN-SCAN-7 (`bb_scan_tab.cpp`)

fscan.r `tab(i)`, function{0,1+} that REVERSES on β (unlike {0,1} boxes, `tab` writes δ and must
restore it on failure). Per the goal spec:
- α: save δ → `[r12+op_off+16]` (scratch qword in the slot — driver must `bb_slot_claim(8)` after
  `bb_slot_alloc16`); bounds-check target `∈ [1,Δ+1]` else ω; δ ← target−1; substring spanned
  (order-normalized) via `rt_icn_substr(Σ, lo, hi)` → DESCR slot (RT value work); γ.
- **β: δ ← saved; ω.** (The reversal that distinguishes tab/move from any/match/many.)
- Wave-1 operand: literal positive n OR a sibling SCAN_* producer slot (`tab(upto(c))` idiom —
  read `[r12+op_sa+8]` like any consumer slot reader).
- Probes: `"hello" ? write(tab(3))` → `he`; `"hello" ? write(tab(upto('l')))` → `he`.
- Need: `rt_icn_substr` function in gen_runtime.c (verify it exists or add it); driver must handle
  two operand shapes (literal n → `op_sb`, sibling slot → `op_sa`).
- Read `fscan.r` tab implementation FIRST per CONSULT-CANONICAL-SOURCES.

## Session setup for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP.git   /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus.git  /home/claude/corpus
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
# canonical sources:
unzip /path/to/icon-master.zip -d refs/
unzip /path/to/jcon-master.zip -d refs/
bash scripts/test_smoke_icon.sh       # m2 12/12 HARD
bash scripts/test_icon_rung_suite.sh  # m2 129 HARD / m3 15/150EXC / m4 22/89EXC
# then: GOAL-ICON-BB.md → ICN-SCAN LADDER → ICN-SCAN-7
```
