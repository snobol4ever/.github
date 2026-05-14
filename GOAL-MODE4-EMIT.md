# GOAL-MODE4-EMIT.md — Mode 4 x86 backend (`--jit-emit --x64`)

⛔ **Read before any source file:** `ARCH-x86.md` then `ARCH-SCRIP.md` then `ARCH-EMITTER.md`.

**Repo:** one4all. **Done when:** `scrip --jit-emit --x64 file.{sno,sc}` → standalone binary output identical to `--sm-run`. Binary links `libscrip_rt.so`. M5 extends to Icon/Raku/Prolog/Rebus.

**Mode-4 is mode-3's SEG_CODE dumped to `.s`.** One shared emitter; no parallel text-emitter.

---

## Architecture

```
IR ─► sm_lower ─► SM_Program ─► sm_codegen ─► SEG_CODE
                                                  ├─ mode 3: jmp in-process
                                                  └─ mode 4: dump to .s → ld → ELF
```

SM opcodes → GNU-as macros (`sm_macros.s`), 3-col `LABEL: OPCODE args`.
BB boxes → GNU-as procs, 4-col `LABEL: ; ACTION ; jmp target`.

**Current compiled emitter units** (post RW-6 consolidation):

| File | Role |
|---|---|
| `emit_core.c` | L0–L2: buf, form, insn, label, text, mode |
| `emit_bb.c` | L3–L4: BB box templates + macro library writer |
| `emit_sm.c` | L4–L5: SM opcode templates, shape renderers, text+walk codegen |
| `sm_jit_interp.c` | **frozen** — mode-3 C interpreter; never touched |

---

## Tracked artifacts protocol

After any session touching emitter files or `rt.c`, regenerate and commit:

```bash
DEMO=/home/claude/corpus/programs/snobol4/demo; SCRIP=/home/claude/one4all/scrip
cd $DEMO
for f in roman wordcount claws5 treebank-list treebank-array; do
    $SCRIP --jit-emit --x64 $f.sno > $f.s 2>/dev/null; done
for s in roman.s wordcount.s claws5.s treebank-list.s treebank-array.s; do
    gcc -c "$s" -o /tmp/$(basename "$s" .s).o 2>/tmp/as_err.txt \
        && echo "OK $s" || { echo "FAIL $s"; cat /tmp/as_err.txt; exit 1; }; done
cd /home/claude/corpus
git add programs/snobol4/demo/{roman,wordcount,claws5,treebank-list,treebank-array,sm_macros,bb_macros}.s
git diff --cached --quiet || git commit -m "x64 artifacts: regen <rung>"
```

---

## Steps

## EM-STATEFUL-FLAT — Make stateful boxes flat (spec-correct, no RTCALL)

Stateful boxes require per-invocation DATA in the flat glob's DATA block — not a heap struct via RTCALL.

- [x] **SF-1** ✅ `3fcc90a7` — `emit_bb_xbal` flat BAL. `.data` slot for `int δ`; inline `'('`/`')'` byte-compare loop via RIP-relative Σ/Σlen/Δ. Binary: heap zeta (unchanged). Gates: smoke 7/7, byte-id 4/4, beauty 10/17.
- [x] **SF-2** ✅ `c99fe633` — `emit_bb_xfarb` flat ARB. DATA: .long count; .long start. α: count=0; start=Δ; →γ. β: count++; if start+count>Σlen →ω; else Δ=start+count →γ. Gates: smoke 7/7, byte-id 4/4, beauty 10/17.
- [x] **SF-3** ✅ `4e3306d5` — `emit_bb_xstar` flat REM. Stateless. α: Δ=Σlen →γ. β: →ω. Gates: smoke 7/7, byte-id 4/4, beauty 10/17.
- [x] **SF-4** ✅ `98b2e204` — `emit_bb_xlnth/xtb/xrtb` flat LEN/TAB/RTAB. n baked as immediate; no DATA. LEN: Δ+n≤Σlen→γ. TAB: Δ≤n→γ, Δ=n. RTAB: Δ≤Σlen-n→γ. All β→ω. Gates: smoke 7/7, byte-id 4/4, beauty 10/17.
- [x] **SF-5** ✅ `55857945` — `emit_bb_xbrkx` flat inline BREAKX. DATA: .string chars; .quad chars_ptr; .long δ. α: scan fwd while Σ[Δ+δ] not in chars; δ==0||Δ+δ>=Σlen →ω; else Δ+=δ →γ. β: Δ-=δ →ω. Assembles clean. Gates: smoke 7/7, byte-id 4/4, beauty 10/17.
- [x] **SF-6** ✅ `8a63e515` — ICN_* boxes: `emit_bb_stateful` gains `nquads` param; all 45 ICN box emitters pass `ICN_NQ(state_t)` = `(sizeof(state_t)+7)/8` so TEXT path emits a correctly-sized zeroed `.data` block per box kind. Non-ICN callers (ARBNO/BREAKX/CALLCAP/CHARSET) retain `nquads=6`. Companion gate fixes (SF-6-pre `f7400d23`): JUMP/JUMP_S/JUMP_F dispatch→macro form; rt_arith case values corrected; RETURN macro→plain ret; sm_phase2_sim_test field names fixed; bb_flat_text_test intern_str callback. Gates: smoke_snobol4 7/7, jit_emit_x64 11/13 (em7c runtime pre-existing).
- [ ] **SF-7** — Delete `emit_bb_stateful`, `emit_bb_stateful_int`, `emit_bb_stateful_text_data` (dead after SF-1..6). Clean up `emit_bb_xbrkx` IS_TEXT guards.
- [ ] **SF-8** — Broad corpus ≥160/163 PASS. Beauty gate ≥10/17. Commit.

> Closed history: `git log -p .github/GOAL-MODE4-EMIT.md`

- [~] **M5** — Raku/Prolog/Rebus SM_SUSPEND/RESUME. ⛔ Hold until GOAL-CHUNKS M4 closes. Icon cancelled (pure-BB path instead).

---

## Watermark

**HEAD** one4all `8a63e515` · .github TBD · Gates: smoke_snobol4 7/7, jit_emit_x64 11/13 (em7c runtime pre-existing open).

**Next:** SF-7 — Delete `emit_bb_stateful`, `emit_bb_stateful_int`, `emit_bb_stateful_text_data` (dead). Clean up `emit_bb_xbrkx` IS_TEXT guards.

**Next session must:** Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md, GOAL-MODE4-EMIT.md, ARCH-EMITTER.md. Confirm one4all HEAD `8a63e515`.
