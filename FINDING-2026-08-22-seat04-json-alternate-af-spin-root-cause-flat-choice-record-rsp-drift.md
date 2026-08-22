# FINDING seat04 — json-alternate-af-spin: ROOT CAUSE NAILED (gdb-verified, exact byte offsets) — FLAT-mode choice records assume static `rsp`, but a deferred alternation inside ARBNO leaves 1,232 bytes of un-unwound backtrack state before re-entering them. Fix NOT attempted this session — architectural, needs a dedicated pass.

**Session:** 2026-08-22 seat04, THE LOOP queue row `json-alternate-af-spin` (rank 0).
**Status:** DIAGNOSIS COMPLETE, gdb-verified to the exact instruction and byte offset. **Fix NOT implemented — claim left OPEN, not `done`.** Zero code changes this session (measurement/gdb only), consistent with RULES.md ASM-DIFF-FIRST discipline ("before changing one byte").
**Builds on:** `FINDING-2026-08-21-s251-json-deserializer-hangs-on-every-comma-and-has-no-corpus-coverage.md` §7 ("MECHANISM FOUND"), which located the spin to `n241_match_alternate_af`/`n249_match_defer_α` ping-ponging via asm inspection but did not explain *why*. This FINDING answers that "why," with a live process, not static reading alone.

---

## 1. A faithful minimal repro, built per the brief's own instruction ("do NOT start from json.sno")

Neither the ablation family (`arb1`–`arb6` in the s251 FINDING) nor a from-scratch hand-rolled `ARBNO`+deferred-ref witness reproduced the hang — `arb1`–`arb5` all MATCH (ARBNO/deferred-ref/recursion are all individually innocent, as s251 already showed), and my own simplified `jelem = *jvalue` (single-arm, non-recursive) witness returned a *different*, *also-wrong* result (silent NOMATCH on input SPITBOL matches) rather than hanging. **The missing ingredient in every prior minimization: a genuine multi-way `|` alternation (`jvalue`'s 7 arms) reached via the deferred reference, not just a bare deferred pattern.**

**Working repro:** copied `json.sno`'s definitions verbatim (lines 1–257, unmodified — all `DEFINE`d actions and the full grammar including `jvalue`'s 7-arm alternation) and appended a 4-line driver with the subject as a literal instead of read from stdin:
```
src = '[1,2]'   (or '[1]')
src json                    :F(fail)
OUTPUT = 'MATCH'            :(END)
fail  OUTPUT = 'NOMATCH'
```
- `[1]` (no comma): **MATCH**, fast, both engines.
- `[1,2]` (comma): SCRIP **hangs** (`timeout 8` → exit 124); clean SPITBOL: **MATCH**, fast. Matches the original table exactly.

**ASM-DIFF, per RULES.md ("mint the smallest repro" → "diff the emitted `.s`" before gdb):** `--compile`d both witnesses (16,599 lines each). `diff` shows **exactly 3 line-pairs different — the embedded literal `"[1]"` vs `"[1,2]"` and its length**. Every instruction in the entire pattern-matching machinery, including every box implicated below, is **byte-identical** between the passing and hanging witness. Per RULES.md this **exonerates the codegen as a source-difference bug** — the two programs run the *same code*; the divergence is purely a runtime choice-record state issue triggered by what the input data does to that one shared code path. This is what justified moving to gdb next, per the mandated order.

---

## 2. The exact box graph (gdb + `nm`, addresses from a `-g` linked standalone binary)

`jarray = '[' (epsilon . *parr()) ( *jelement ARBNO(',' *jelement) | ws ) ']' (epsilon . *earr()) FENCE` compiles (this witness's numbering, confirmed to match the box **names** `n241_match_alternate_af` / `n249_match_defer_α` in the original full `json.sno` exactly, since both programs share the identical preceding `DEFINE`d-procedure prologue) to:

- **`n241_match_alternate`** = the outer `( X | ws )` choice. Its `α` does `sub rsp,32` and lays down a **4-slot, 32-byte FLAT (stack-carved) choice record**: `[rsp+0]`=cursor, `[rsp+8]`=arm-selector/β-continuation (written later by `s0`/`s1`), `[rsp+16]`=the **"af" continuation** (rewritten twice — first to `.Lx261_21`, then, once the *second* deferred call is dispatched, to `.Lx261_19`, the box's own correct unwind-and-propagate-failure exit), `[rsp+24]` unused padding.
- `α` immediately tail-jumps (no `s0`/`s1` yet) into **`n249_match_defer_α`** = the *first* `*jelement` (matching `[1,2]`'s `"1"`).
- `n249_match_defer_α` resolves `jelement`'s pattern pointer and, on the fast path, **pushes two return-style continuations** (`.Lx273_5`→`af`'s fallback if the whole deferred match ever fails outright, `.Lx273_4`→`n250_match_arbno_α` on success) and does `jmp rax` into `jvalue`'s own compiled matcher (the 7-arm `jstring | jnumber+action | jobject | jarray | true+action | false+action | null+action` alternation) — itself a nested chain of `match_alternate`/`match_defer`/`FENCE`-guarded-optional boxes (`jnumber` alone has 4 more `FENCE(X|'')` optional pieces).
- `jvalue` succeeds (matches `"1"` as a `jnumber`), lands back at `.Lx273_4` → **`n250_match_arbno_α`**. This box's *own* loop-state (`[rbp-80]`=start cursor, `[rbp-76]`=last cursor) is correctly **RBP-relative/stable** — but its `α`, having recorded that state, **jumps straight back into `n241_match_alternate_s0`** to (re-)select an arm and dispatch onward to `n242_match_lit_α` (the closing `']'` check). `n250_match_arbno_β`/`as`/`af` similarly jump in and out of `n241`'s ports and `n252_match_defer` (the comma-then-second-`*jelement` iteration body) as the loop progresses.

## 3. gdb-verified: the drift, exactly

```
break n241_match_alternate_α   → rsp = 0x7fffffffdc80   (the record's true base, R)
break n250_match_arbno_α       → rsp = 0x7fffffffd7b0   (R − 1,232 bytes)
break n241_match_alternate_s0  → rsp = 0x7fffffffd7b0   (same — re-entered with NO correction)
break n241_match_alternate_af  → rsp = 0x7fffffffd7b0, forever, [rsp+0]=4213615, [rsp+16]=0x403bde
```

**`R − 1,232` is the whole bug.** Between `α`'s `sub rsp,32` and `n250`'s first re-entry into `n241`'s ports, `jvalue`'s own internal matching of `"1"` — trying and (mostly) rejecting 6 of its 7 arms before landing on `jnumber`, each rejection/commitment itself leaving its own pending backtrack state on the shared stack by the exact same "push-two-continuations, pop-only-one-on-success" convention `n249` used — accumulates 1,232 bytes of **legitimate, by-design backtrack state that is never unwound on success**, because nothing downstream has failed yet to need it. `n241`'s ports address their choice record as `[rsp+N]` — bare current-`rsp`-relative, no adjustment for anything pushed since `α`. Every later re-entry (from `n250_match_arbno_α`/`β`/`as`/`af`, from `n248_goto`, from `n252_match_defer`'s own continuations) is silently reading/writing **1,232 bytes into unrelated memory** — specifically, into the leftover choice-point state of arms of `jvalue`'s alternation that were *tried and abandoned* while matching `"1"`.

**Why it spins, specifically:** `0x403bde` (the fixed, garbage-derived value `af` keeps re-reading from `[rsp+16]`) resolves — confirmed via `objdump`, `nm` — to an instruction *inside `n249_match_defer_α`'s own body*: `jmp n241_match_alternate_af`. That address happens to sit at the drifted `[rsp+16]` location by coincidence of what's left over in that stale memory, not by any correct choice-record write. So `af` reads it, jumps to it, lands right back in `n249`'s body at the instruction that jumps straight back to `af` — a true two-instruction stationary loop, `rsp` never moving, matching the original FINDING's 50/50 perf split exactly. **This is why `[rsp+8]`/`[rsp+24]` (the brief's own open question) don't matter to the spin itself** — the loop never reaches code that reads them; it's fully contained in the `af` ↔ `.Lx273_5`(inside `n249`) pair. `[rsp+8]` is real (the `s0`/`s1` arm-selector, confirmed in §2); `[rsp+24]` is unused 32-byte-alignment padding, confirmed never written or read anywhere in this box.

**Why `[1]` (no comma) doesn't hang:** with no comma, `n250_match_arbno_as`'s single check fails immediately (no `,` to extend the loop) and the whole thing proceeds straight through to `']'` without ever *receding* back into `n241`'s ports from a failure — the drifted-but-unread record never gets touched. The bug is dormant until something forces a *recede* into the alternation's ports after the drift has already happened, which a trailing comma (forcing an ARBNO iteration, hence an arbno-to-alternate re-entry) does unconditionally.

---

## 4. Why this specific grammar shape, and why RBP-mode (which would have been immune) doesn't fire

`sn4_choice_rbp_off()` (`src/emitter/emit.cpp:2328`) is a **live, default-on** (`sn4_pt_frame()` defaults to 1 absent `SCRIP_PT_FRAME=0`) mechanism that puts a `match_alternate`'s choice record on a **stable RBP-relative frame slot** instead of the raw stack — which would be **immune to this exact drift**, since it doesn't move when nested calls push/pop below it. It didn't activate here because `blob_choice_rbp_scan()` (`emit.cpp:2305`) requires **exactly one choice point in the blob AND no `FENCE`** (`if (_nc != 1 || _fn) return 0;`, where `_fn` comes from `sn4_blob_choice_scan` scanning for `IR_MATCH_FENCE0`/`IR_MATCH_FENCE1`). `jarray`'s second arm is `ws = FENCE(SPAN(...) | '')` — **the very presence of a `FENCE` in the alternation's *other*, entirely unrelated arm disqualifies the whole box from the safe mode**, falling back to the FLAT/stack-carved mode that this FINDING shows is unsound whenever the *chosen* arm contains a deferred reference into a further multi-arm alternation. `jobject`'s `( jmember ARBNO(',' jmember) | ws )` is the textually identical shape (same `ws` fallback arm), which is exactly why the original FINDING's table shows `{"a":1,"b":2}` hanging too — **one mechanism, two grammar sites, matching the reported symptom set exactly.**

---

## 5. Fix directions considered, NOT attempted — why, and what each needs

I stopped short of implementing a fix this session. `emit.cpp`'s choice-record machinery (`blob_choice_rbp_scan`, `sn4_blob_choice_scan`, `frame_slot_scan`, `blob_frame_bytes`, `zdp_seam_tier`) is dense, actively tuned, gates *every* `match_alternate` box project-wide, and is a live file several other seats are concurrently editing for the R10/R11 eradication ladder — this is not a "flip one condition" change I'm confident is safe without dedicated verification against the full corpus (355 m3 / 353 m4 standing programs) and the M1 fixed-point gate. Two directions, in rough order of how promising they look:

1. **Widen `blob_choice_rbp_scan`'s FENCE exclusion.** The RBP-relative mode already exists and would structurally eliminate the whole bug class (stable storage can't drift). But the FENCE exclusion looks deliberate, not an oversight — FENCE performs a global cut that discards *older* choice points, and whether that interacts safely with a single reserved RBP slot (as opposed to an arbitrary-depth stack of them) is exactly the kind of thing that needs to be verified, not assumed. Whoever picks this up should find out *why* `_fn` disqualifies before touching it — there may be a real hazard, or it may just never have been exercised against this shape.
2. **Make FLAT mode itself safe under this combination** — e.g., have `n249`/`n252`'s deferred-success path communicate how much it left pushed (so `n241`'s ports can compute the *correct* current offset instead of assuming zero drift), or have ARBNO's re-entry into an outer alternation's ports go through a proper stable-pointer handoff instead of a bare label jump. Avoids touching the RBP eligibility heuristic at all, but touches the hotter, default-active code path, so the correctness bar for verification is higher.

Neither is a same-session change I'd stand behind without the kind of corpus-wide verification RULES.md's own gate discipline demands (`make pristine` + full corpus + M1 fixed point, both modes, per HQ-27) — and this box shape (alternation-with-a-deferred-alternation-in-one-arm-and-a-fence-in-another, re-entered through ARBNO) is exactly the kind of narrow, easy-to-get-subtly-wrong interaction where a rushed fix risks trading a loud hang for a silent wrong-answer regression elsewhere in the 355-program corpus.

---

## 6. What's confirmed clean / unaffected

- **Zero code changes.** No killswitch flipped, no `.s` artifacts touched, nothing owed at regen per CLAUDE.md's codegen-touch rule (I read `emit.cpp`/`bb_match_alternate.cpp`, did not edit either).
- **`arb1`–`arb6`'s conclusions still stand** — ARBNO alone, deferred refs alone, and recursive deferred refs alone are all innocent, confirmed independently by this session's own from-scratch witness attempts hitting *different* (non-hang) failure modes when the 7-arm alternation ingredient was missing.
- **`cond-assign-double-fire`** (the secondary defect s251 found via `arb6`, unrelated to this spin) was fixed mid-session by seat11 (`SCRIP b007a116`) — not this row's concern, noted for completeness only.
- Both `jbig_comma.sno`/`jbig_nocomma.sno` witnesses and all gdb scripts live under this session's scratchpad, not the repo — nothing to clean up in `corpus/` or `SCRIP/`.

## 7. Items for HQ / whoever continues this row

1. **This claim is left OPEN, not `done`** — the row's DONE-WHEN explicitly wants the hang fixed, corpus-covered, and verified; only the root-cause half is complete. Whoever continues (myself next session, or another seat) can start directly at §5 without re-deriving §§1–4.
2. **Suggest widening scope slightly at fix time:** `json-match.sno`/`json-match-fence.sno` share the identical grammar (per `json.sno`'s own header: "same grammar, zero side effects") and almost certainly hang identically on `[1,2]` — not verified this session (time-boxed to the root-cause), cheap to check first thing next session.
3. **The missing corpus row (s251 §3, still true)** should use an input that actually exercises this box shape (comma inside an array or object) once the fix lands — the original FINDING already specified this; not repeated in more detail here.
4. If a fix attempt lands, re-run this session's exact two witnesses (`jbig_comma.sno`/`jbig_nocomma.sno`, reproducible from `json.sno` lines 1–257 verbatim + the 4-line driver in §1) as the fastest possible regression check before touching `citm_catalog.json`.
