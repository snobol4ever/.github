# FINDING 2026-08-19 s172 (seat4 `/home/claude4`, Claude Opus 5, queue row `claws5-sig11` = HQ board D-2) — **THE claws5 SIG11 ×3 IS TWO DEFECTS, NOT ONE. THE FIRST IS THE s130/s131 LEAF-SUSPENSION CLASS WEARING A NEW, *DYNAMIC* FACE — THE ζ SLOT ADDRESS DESCENDS 48 BYTES PER ARBNO ITERATION, SO THE SAME PROGRAM IS GREEN AT k=4 AND SIG11 AT k=5. THE SECOND IS m4-ONLY AND SURVIVES THE CURE.**

**Tree:** SCRIP `c0efe346` · corpus `74fe5ff4` (this seat's four witnesses, `probe/claws5/`) · RT_OPT **-O0** (FACT RULE O0-DEV) · oracle `x64/bin/sbl -b` present and alive. Method: ASM-DIFF-FIRST per RULES.md — ablate → diff the `--compile` `.s` → gdb last.

---

## 1. THE DISPOSITION, UP FRONT — AND IT CORRECTS AN INHERITED CLAIM

`SCRIP_SPAN_FRAME=1` (built and disarmed at s130; seat8's s170 cursor) is measured here against all three board programs, **both modes**, full `claws5.input` (1077 bytes):

| program | default arm m3 | default arm m4 | `SCRIP_SPAN_FRAME=1` m3 | `SCRIP_SPAN_FRAME=1` m4 |
|---|---|---|---|---|
| `claws5-match.sno` | SIG11 | SIG11 | **matched bytes=1077** | **matched bytes=1077** |
| `claws5-match-fence.sno` | SIG11 | SIG11 | **matched bytes=1077** | **matched bytes=1077** |
| `claws5.sno` | SIG11 | SIG11 | **matched bytes=1077** | **SIG11** |

Oracle is `matched bytes=1077` for all three.

⛔ **CORRECTION TO THE INHERITED s170 LINE.** That cursor states *"claws5 m4 still crashes under BOTH arms — a second, different defect, still D-2's."* Measured here, that is true of **`claws5.sno` only**. `claws5-match.sno` and `claws5-match-fence.sno` — two of the board's three SIG11 rows — are cured by `SCRIP_SPAN_FRAME=1` in **both** modes. The s170 seat measured `demo_claws5` (the m3 row) and was right about it; the generalisation to all three programs in m4 does not hold. **Two of the three D-2 rows need no new fix at all — only Lon's pending flip grant on `SCRIP_SPAN_FRAME`.**

---

## 2. DEFECT A — THE ζ-SPINE SLOT DRIFTS 48 BYTES PER RETAINED ARBNO ITERATION

**Witness pair (self-contained, no input file, sub-second, oracle-differential):**
`corpus/probe/claws5/claws5_spine_drift_k4_green.sno` (PASS both modes) · `claws5_spine_drift_k5_red.sno` (**SIG11 both modes**).
The two files differ **only in the number of tokens in the subject literal** — 4 vs 5. Same pattern, same graph, same emitted `.s` modulo the string.

**The pattern, ablated down from `claws5-match.sno`:**
```
p = POS(0) ARBNO((SPAN('0123456789') | SPAN('ab') SPAN('_A0')) SPAN(' ')) RPOS(0)
```

**Required ingredients, exactly two** (ladder run this seat, each ingredient removed in isolation):
1. an `IR_MATCH_ALTERNATE` **whose taken arm is a ≥2-element CONCATENATION**. Single-element arms pass at every k tested (to 32). `NOTANY`/`BREAK`/`ANY`/`&UCASE`/inner parens are all **exonerated** — removing them changes nothing; replacing the two-element arm with a one-element `SPAN` covering the same characters turns the crash off.
2. **enough ARBNO iterations.** This is the new part — see §3.

**The asm diff is one extra slot and two severed wires.** Label-normalised `--compile` diff of the 2-element witness against its 1-element twin, whole file:
- the 2-element arm mints a **third** ζ save slot: the twin has `[rsp+452]` and `[rsp+468]`; the witness has `[rsp+452]`, `[rsp+468]` and **`[rsp+484]`** — a 16-byte stride, the third one being the new element's.
- `n21_match_arbno_af` loses its conditional recede: twin emits `cmp r14d, eax; jne n26_match_span_β` then `jmp n20_match_pos_β`; the witness emits `cmp r14d, eax; jmp n20_match_pos_β` — **a dead compare and no path back into the body's last node.**
- the arm's resume wire `.LxN_41` points at a `n27_goto` stub whose **α and β both `jmp n25_match_alternate_af`** (concede), instead of at `n29_match_span_β`, the arm's last element. `n26_match_span_β` and `n29_match_span_β` are both **emitted and referenced by nobody.**

Stated honestly: those two severed wires are a real second-order emitter defect (they make the unwind path unreachable), **but they are not what kills the process** — the SIGSEGV is on the forward, matching path, and is fully explained by what follows.

---

## 3. THE MECHANISM, MEASURED — "A BOX COMPENSATES FOR EXACTLY WHAT *IT* CARVED" IS THE BUG WHEN A SIBLING BOX CARVES PER ITERATION

`x86_frame_off` (`src/templates/x86_asm.h:583`) is **THE ONE OFFSET FUNCTION, RSP-ONLY**: `off + _.op_zdepth`, and its own comment states the contract — *"a box compensates for exactly what IT carved."* Under `ZC_STORAGE_CELL_STACK` (the compiled default) the ζ-SPINE cursor **is rsp**.

An ARBNO whose body matched **retains** its choice-point frames across the iteration — that is what makes the iteration resumable. Measured per iteration on the witness: `n25_match_alternate_α` carves 32 bytes, `n26_match_span_α` carves 16 — **48 bytes per iteration, released only on recede.** That depth is a *runtime* quantity: it is the iteration count, which no compile-time constant can express. `op_zdepth` never sees it, because it is not this box's own carve.

**So the "standing" slot does not stand. It walks.** gdb trace, one line per ARBNO iteration, breakpoint on `n26_match_span_α` (mode-4 image, `k=9` subject):

```
iter rsp=0x7fffffffe020  slot452=0x…e1e4  slot468=0x…e1f4  slot484=0x…e204   casmark_at=0x7fffffffe080
iter rsp=0x7fffffffdff0  slot452=0x…e1b4  slot468=0x…e1c4  slot484=0x…e1d4   casmark_at=0x7fffffffe080
iter rsp=0x7fffffffdfc0  …                                  slot484=0x…e1a4
iter rsp=0x7fffffffdf90  …                                  slot484=0x…e174
iter rsp=0x7fffffffdf60  …                                  slot484=0x…e144
iter rsp=0x7fffffffdf30  …                                  slot484=0x…e114
iter rsp=0x7fffffffdf00  …                                  slot484=0x…e0e4
iter rsp=0x7fffffffded0  …                                  slot484=0x…e0b4
iter rsp=0x7fffffffdea0  …                                  slot484=0x7fffffffe084   ← casmark_at + 4
Program received signal SIGSEGV
```

`rsp` descends by exactly **0x30 = 48** per iteration; `rbp` never moves; the slots ride rsp down with it. On **iteration 9** the third slot lands on `casmark + 4` — the **upper 4 bytes of the saved `cas_mark` pointer** — and the 32-bit store `mov dword ptr [rsp+484], r14d` writes the cursor there.

**The corruption is exactly that, byte for byte.** At the fault:
```
mark = 0x00000032f25ff030      top = 0x00007ffff25ff030      (mode 4, r14d = 50 = 0x32)
mark = 0x00000034f25ff030      top = 0x00007ffff25ff030      (mode 3, claws5-match, r14d = 52 = 0x34)
```
Low 32 bits identical to `top`; high 32 bits replaced by a **cursor position**. `rt_match_end_all` (`pattern_match.c:743`) then hands that pointer to `c_rt_dcap_end_ok_open` → `rt_dcap_pump` (`:691`/`:721`) and the process dies. **m3 and m4 produce the identical signature** — the m3≡m4 design invariant holds through the defect.

⭐ **THIS IS THE s130/s131 LEAF-SUSPENSION CLASS, PLUS A DIMENSION THE EXISTING WITNESSES DO NOT HAVE.** s170's `probe/cn` family reaches the wild write **statically** — twenty ordinary assignments push the flat ZLS coordinate past the live frame, so the coordinate is large and the crash is a property of the *program text*. This witness reaches it **dynamically**: the coordinate is small (+484), the program is nine lines, and the crash is a property of the *subject string* at run time. Consequence worth stating plainly: **no amount of source inspection bounds this class, and a program that passes its test corpus can SIG11 on a longer input.** The 1077-byte real input and the 30-byte minimal witness are the same defect.

**Corroboration already in the tree:** `zeta_choices.h:280`'s own `#error` names *"the SNOBOL4 ARBNO-family bench crashers … (pattern_bt, string_pattern, roman)"* as a pre-existing documented set, and `x86_asm.h:583`'s PIN-REBASE note describes the sibling incident in the same words this seat measured — *"caught by software watchpoint as a dword cursor store zeroing environ[0]'s high half."* Same store width, same victim shape, different victim.

### 3b. THE FOUR-CONFIG ζ SELECTOR DOES NOT CONTAIN IT — IT ONLY MOVES THE WALL
`claws5-match.sno`, m3, iteration count k (`.` = matched, `X` = SIG11):

| `--zeta-storage=` | k8 | k9 | k10 | k12 | k16 | k24 | k40 |
|---|---|---|---|---|---|---|---|
| `cell-stack` (default) | . | **X** | X | X | X | X | X |
| `frame-rsp` | . | . | . | . | **X** | X | X |
| `cell-heap` | **X** | X | X | X | X | X | X |

⛔ **`frame-rsp` is NOT a fix and must not be reported as one** — it moves the wall from k=9 to k=16, and on the full 1077-byte input all three configs SIG11. It also *regresses* `treebank-match.sno`, which passes at the default and SIG11s under `frame-rsp`. The wall's *location* is a layout accident; its *existence* is config-independent.

### 3c. THE CURE THAT DOES WORK
`SCRIP_SPAN_FRAME=1` gives the leaf a stable rbp-relative slot (`leaf_frame_slot`, `emit.h:674`; `sn4_span_frame`, `emit.cpp:2312`) — depth-immune, so drift cannot occur. It turns **both** witnesses of Defect A green in **both** modes, and cures `claws5-match` + `claws5-match-fence` on the real input in both modes. This seat adds no new fix: **the cure exists, it is measured, and what it is waiting on is Lon's flip grant** (s170's NEXT-SEAT item 1, still owed).

---

## 4. DEFECT B — THE m4-ONLY RESIDUE: A DEFERRED CAPTURE CALL ON AN ALT ARM

**Witness pair:** `corpus/probe/claws5/claws5_dcap_call_green.sno` · `claws5_dcap_call_red.sno`. **Run with `SCRIP_SPAN_FRAME=1`** so Defect A is out of the way. The two files differ by **one ablation: the presence of `. *token()`.**

Ablating `claws5.sno` proves the ingredient is that and only that: deleting ` . *token()` alone (keeping `. num`, `. wrd`, `. tag`, the `DEFINE`, the `TABLE()`s) makes the armed m4 run green on the real 1077-byte input. Deleting the plain `.` captures as well changes nothing further.

**Signature (m4 image, `SCRIP_NO_SEGV_HANDLER=1`):**
```
#0  0x0000000000000036 in ?? ()          ← control transferred to address 0x36 = 54 = SIZE(src)
#1  n55_lit_string_α ()
#4  rt_call_proc_descr (name="token", nargs=0)   rt/rt.c:908
#5  rt_dcap_pump ()                               pattern_match.c:700
```
`rt_dcap_pump` reaches the SNOBOL-defined target through `rt_call_proc_descr`'s **by-name dyn transfer** (`p->jmp_entry` / `rt_proc_enter` / `rt_dyn_alpha_fn`), and in a mode-4 image the transfer lands on a bogus address — the failure mode `rt_dyn_alpha_fn`'s own comment calls the *"rip=5 crash class"*. **This is consistent with the s156 by-name→SNOBOL-defined dispatch class in m4** (`FINDING-…-s156-B1-root-cause-byname-dispatch-cannot-reach-snobol-defined-targets-in-m4.md`, board rung **D-18**), reached here through the deferred-capture path rather than through `$FN(X)`. Stated as attribution, not as proof: this seat did not bisect Defect B to `core_call_registered_fn`, and D-18 owns that.

**No fix attempted** — it does not fit behind a killswitch at this rung, and the brief makes investigation-only a complete deliverable.

---

## 5. THE WITNESS MATRIX — every cell measured this seat

`PASS` = byte-identical to the SPITBOL `.ref`.

| witness | `SPAN_FRAME` | mode 3 | mode 4 | `.ref` |
|---|---|---|---|---|
| `claws5_spine_drift_k4_green` | 0 | PASS | PASS | `matched bytes=24` |
| `claws5_spine_drift_k4_green` | 1 | PASS | PASS | |
| `claws5_spine_drift_k5_red` | 0 | **SIG11** | **SIG11** | `matched bytes=30` |
| `claws5_spine_drift_k5_red` | 1 | PASS | PASS | |
| `claws5_dcap_call_green` | 0 | PASS | **SIG11** | `matched bytes=54 n=0` |
| `claws5_dcap_call_green` | 1 | PASS | PASS | |
| `claws5_dcap_call_red` | 0 | **SIG11** | **SIG11** | `matched bytes=54 n=9` |
| `claws5_dcap_call_red` | 1 | PASS | **SIG11** | |

(`claws5_dcap_call_green` at arm 0 is m4-red because it still carries Defect A there; arm 1 is the isolating cell, which is why the file header names the arm.)

**Reproduce Defect A in three commands, no input file:**
```bash
W=$S4E/corpus/probe/claws5; S=$S4E/SCRIP/scrip
$S $W/claws5_spine_drift_k4_green.sno < /dev/null   # matched bytes=24
$S $W/claws5_spine_drift_k5_red.sno   < /dev/null   # SIG11 (oracle: matched bytes=30)
SCRIP_SPAN_FRAME=1 $S $W/claws5_spine_drift_k5_red.sno < /dev/null   # matched bytes=30
```

---

## 6. WHAT THE NEXT SEAT SHOULD DO, IN ORDER

1. ⛔ **The `SCRIP_SPAN_FRAME` default flip is now worth more than s170 priced it.** s170 justified it with one m3 gain; this seat adds **two of the three D-2 board rows cured in BOTH modes** on the real input. The 527-program demo/feature/benchmark artifact sweep that s170 did not run is still the missing receipt, and the ruling is still Lon's.
2. **Defect A's severed unwind wires (§2) are unfixed and untracked** — `n21_match_arbno_af`'s dropped conditional recede and the `n27_goto` concede stub. `SCRIP_SPAN_FRAME=1` cures the *crash* without touching them, so arming the killswitch will **hide** them. They are a wrong-answer risk on the ARBNO-retreat path and deserve their own witness (an ARBNO over a multi-element ALT arm that must *fail* and retreat).
3. **Defect B routes to D-18**, not to a new rung.
4. **The dynamic face generalises beyond SPAN.** s170's item 3 already flags that `ARB`/`BAL` are declined by `leaf_frame_candidate()` and have **no cure on either arm**; §3 shows the coordinate need not be large to be fatal, so an `ARB`/`BAL` ALT arm under a long-running ARBNO is the next witness worth minting and it has no killswitch behind it.
