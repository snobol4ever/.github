# FINDING — s190 (seat7, `/home/claude7`, Claude Opus 5) — row `alt-tail-resume-surface`
## AN ALTERNATIVE'S RESUME SURFACE IS ITS RIGHTMOST BOX, AND THE ARM HEAD IT AIMED AT WAS A DEAD SENTINEL

**Landed:** SCRIP `21819132` (one accessor + one line in `src/lower/lower_snobol4.c`), **default OFF** behind `SCRIP_ALT_TAIL`.
**Measured at:** `make pristine` EXIT=0 at SCRIP `b12cb82e`; re-proved after a rebase onto `7d5ebaaf` (scripts-only, **zero `src/`**). RT_OPT `-O0`. Oracle `sbl -bf` verified alive. corpus tree clean.
**Provenance:** seat4 found and measured this at s188/s189 inside row `fuzz-segv-batch`, **refused to land it out of scope**, and filed it. This seat reproduced it from scratch and paid the row's price.

---

## 1. THE DEFECT — ONE WORD OF `SN4-NARY-ALT`'s OWN COMMENT WAS NEVER TRUE

`lower_snobol4.c`'s TT_ALT arm builds one `IR_MATCH_ALTERNATE` node `A` with 2N operands = `(entry_i, resume_i)` pairs, and its own comment states the contract:

> *A.β (right context resumes): dispatch on alt_i to resume_i's β — **the alternative's OWN inner resume**.*

`entry_i` was right. `resume_i` was **`g->all[before]` — the arm's FIRST-ALLOCATED node**, i.e. the arm HEAD. For a single-box arm head == tail and nobody noticed. For a **multi-box** arm the right context recedes into the head and **skips the β of every interior box**, so an inner generator never re-yields.

The cure is `ti` — the last node this very loop tags **σ** (γ exits the arm rightward) — which is the arm's rightmost box **by construction**. Single-box arms have `ti == head`, so a single-box corpus is byte-identical.

**This is s187's SEQ-TAIL-RESUME, one construct over.** `sno_seq_tail()` already names the identical false accept for the SEQ element. The sibling was never swept for.

## 2. THE WITNESS

`corpus/crosscheck/patterns/160_pat_alt_inner_gen_resume.sno` — `'aXb' ? ('a' ARB . V | 'q') 'b'`

| arm | m3 `--run` | m4 `--compile` |
|---|---|---|
| default (OFF) | **rc=139 SEGV** | **rc=139 SEGV** |
| `SCRIP_ALT_TAIL=1` | **rc=0 `V=[X]`** | **rc=0 `V=[X]`** |
| live oracle `sbl -bf` | `V=[X]` | — |

Oracle-identical in **both** modes, and m3 ≡ m4.

## 3. ⭐ THE HEAD WAS NOT MERELY THE WRONG BOX — IT WAS A BOX WITH NOTHING IN IT

The asm diff is the whole story, and it is **two lines plus a deletion**. Fully normalized (`.L*`/node numbering/whitespace) on `probe/earn0/earn0_pend_alt_first_arm.sno`:

```
< .LxN_40:              jmp  nN_goto_β                        <- resume aimed at the arm HEAD
> .LxN_40:              jmp  nN_match_lit_β                   <- resume aimed at the arm TAIL
< nN_goto_α:            jmp  nN_match_alternate_af            <- and the head box is now
< nN_goto_β:            jmp  nN_match_alternate_af               unreachable: DELETED
```

The arm head was an `IR_GOTO` sentinel **whose α and β both jump to the alternation's own fail-glue `af`**. Resuming into it could only ever mean *"give up on this alternative and take the next one"* — the exact opposite of *"let this alternative's inner generator yield again."* Once nothing aims at the head, the head is dead-code-eliminated.

**So the bug had a shape worth naming: a resume surface pointing at a box that cannot resume.** The head sentinel is why the failure mode was a SEGV rather than a wrong answer — the right context resumed onto a box that had carved nothing and returned into a frame that was not there.

## 4. BLAST RADIUS — 144 PROGRAMS, BUT **ONE MECHANISM REPEATED 478 TIMES**

Instrument: `util_s_md5_sweep.sh` over **1838** programs (`corpus/programs/lon/` excluded **by construction**, per RULES). s189's hygiene guard applied to every arm: `wc -l` == `cut -f2|sort -u|wc -l` == 1838, no truncated file.

- **Noise floor MEASURED, not cited:** same arm swept twice = **1 row** (`programs/snobol4/parser/unary_not.sno`, the s172 flaky).
- **Default arm vs a stashed-patch rebuild of HEAD: 1 mover — and it is that same flaky row.** The default arm is byte-identical to HEAD.
- **Armed arm vs default: 144 movers.**

144 sounds like a resume-surface change moving half the corpus again (the row priced 52/106). **It is not.** Fully label-normalized, the 144 diffs total **5050 lines** and decompose **exactly**:

| lines | what |
|---:|---|
| **478** | `.Lx*: jmp n*_goto_β` → `jmp n*_match_{assign_cond 172, defer 133, lit 92, span 26, alternate 22, any 10, pos 10, …}_β` — **the retarget, one per arm** |
| **956** | = 478 × 2 — the dead arm-head `goto` sentinel boxes (α + β) deleted |
| **478** | the `#---` separator that preceded each deleted box |
| 248 | frame carve sizes (`sub rsp, N`) |
| 2234 | rbp slot offsets |

**The 478 / 478 / 956 / 478 internal consistency IS the argument.** Every changed line is one of four faces of the same deletion; the carve sizes and slot offsets are the ζ *consequence* of removing 478 boxes, not an independent change. **The radius is 478 alternation arms, not 144 unrelated moves.**

⭐ **A method note worth reusing: a raw `.s` mover count over-reported this by an order of magnitude.** The raw diff of one small witness was 205 lines; the real delta was 4. Deleting one box renumbers every node and every `.L*` label after it, and the label-column padding changes with the label width. **A mover count is a screening instrument; the mechanism only appears after the numbering is normalized away.**

## 5. BOARDS — EVERY ONE BETTER, NONE WORSE BY NAME

| board | default | `SCRIP_ALT_TAIL=1` |
|---|---|---|
| corpus 337 | m3 **333/4** · m4 **326/10** SKIP 1 | m3 **334/3** · m4 **327/9** SKIP 1 |
| crosscheck | m3 **313/4** · m4 **309/7** · DIVERGE 3 | m3 **314/3** · m4 **310/6** · DIVERGE **3, same names** |
| passthru 182 | m3 **170** · m4 **156** | m3 **176** (+6) · m4 **160** (+4) |
| beauty self-host | 259 bytes rc=1 | **259 bytes rc=1 — unmoved** |

corpus fail-set diff is `160_pat_alt_inner_gen_resume` **and nothing else**, both modes. passthru cures: `ptw_min_arbno_altrec_falsereject`, `ptw_min_arbno_bodyplain_wrong`, `ptw_min_arbno_mutualrec_wrong`, `ptw_min_argpat_arbno` (both modes) + `ptw_min_opsyn_elem`, `ptw_min_opsyn_evalpat` (m3 only). **Zero new reds by name on any board.**

⭐ **`beauty.sno` IS a `.s` mover and its behaviour is byte-identical in both arms.** A `.s` mover is not a behaviour mover — the s189 lesson restated from the other side.

## 6. ⛔ THE ONE THING BLOCKING A DEFAULT FLIP, AND IT IS NOT A BOARD ROW

**The armed arm introduces an `m3 != m4` divergence on `ptw_min_opsyn_elem` / `ptw_min_opsyn_evalpat`.** Measured directly, not read off a board (the board's `rc=1` was its own diff exit, not the program's):

```
oracle sbl -bf : "DoReduce(A, 1)" / "R(q,1)"  then  match
default  m3/m4: nomatch / nomatch      <- both WRONG, but m3 == m4
armed    m3    : DoReduce(A, 1) match  <- the oracle answer, exactly
armed    m4    : nomatch               <- unmoved
```

`m3 ≡ m4` is a design invariant of record. The flag buys **+10 net greens across three boards** and breaks that invariant on **2** programs. **That trade is HQ's call, not this seat's** — hence default OFF, which is also what the row required.

Note the direction: the armed arm makes **m3 correct** and leaves m4 where it already was. This is not a regression that the flag caused so much as a **pre-existing m4 gap that the flag exposes** — m4 was only "agreeing" with m3 by being wrong in the same way. Naming the next rung: *why does the m4 arm not take the retarget's benefit here?*

## 7. CLASS EXCLUSION, INHERITED AND NOT RE-DERIVED

seat4 reported and this seat did not re-measure: **it moves ZERO of the 11 `fz_segv_*` witnesses.** The fuzz SEGV batch is not the alt-arm resume-surface class.

## 8. NO NEW GLOBALS

`sno_alt_tail()` reads `getenv` with **no static cache** — unlike its `sno_seq_tail()` sibling, which memoizes into a file-scope `static int`. The patch adds **zero** file-scope state.

## 9. WHAT THE NEXT SEAT SHOULD TAKE

1. **`alt-tail-m4-gap`** — §6. The retarget cures `opsyn_elem`/`opsyn_evalpat` in m3 and not m4; that gap is the whole distance between this flag and a default flip.
2. **Sweep for the third sibling.** SEQ had it (s187), ALT had it (here). Any other construct whose lowering hands a *first-allocated* node to something that means *resume* is the same latent bug. `g->all[before]` is the grep.
3. **The dead arm-head sentinel is worth a look on its own** — 478 of them exist across the corpus today and every one is two instructions that can only concede. They vanish under this flag; under the default they are live code nothing needs.

**Gates green at pristine:** `emit_no_lang` · `template_medium_invisible` (0 sites, ceiling 0) · `icn_no_stack` · `icn_one_reg_frame` · `icn_semicolon_required`. **smoke 7/7 BOTH modes** (m4 hard gate). **RULES step-4 regens ×5: `changed=0` on 623 + 22 programs**, an independent second path to the default-arm byte-identity claim.
