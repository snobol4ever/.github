# The Icon generator call path enters every runtime helper 8 bytes off the ABI, and only records notice

**hq_I, 2026-09-06.** Trees: SCRIP `495aeb974`, corpus `7154c0b34`, .github `ea220f454`. Build: incremental
`make`, `RT_OPT=-O0`. Oracle: `/home/resources/icon-master/bin/icont` v9.5.25a.

## THE ROW SAID CO-EXPRESSIONS. IT IS NOT CO-EXPRESSIONS, AND IT IS NOT RECORDS EITHER.

seat07 filed `icon-ipl-parse-icn-coexpression-sigsegv-both-modes` off `ipl/progs/parse.icn`, whose own header
advertises it as "an interesting example of the use of co-expressions". Reproduced first, 3/3, rc=139 both
modes, **no output at all** before the fault.

Ablating the incidental half of the witness moved the class twice:

| witness | shape | SCRIP | iconx |
|---|---|---|---|
| `create (1 \| \|7)` | alternation + repeated alternation in a co-expression | ✅ agrees | ✅ |
| `create gen()` yielding **integers** | co-expression over a suspending procedure | ✅ agrees | ✅ |
| `create gen()` yielding a **record** | co-expression over a suspending procedure | **SIGSEGV** | ✅ |
| `every x := gen()` yielding a **record**, *no co-expression at all* | | **SIGSEGV** | ✅ |
| record built **outside**, yielded through a co-expression | | ✅ agrees | ✅ |
| `return` a record | | ✅ agrees | ✅ |
| `suspend` a **list** | | ✅ agrees | ✅ |

Co-expressions dropped out (a record built outside and yielded through one is fine; a record suspended with no
co-expression anywhere crashes). What survived is eight lines:

```icon
record one(f)
procedure main()
   local x;
   every x := gen() do write("ok");
end
procedure gen()
   suspend one("z");
end
```

## AND RECORDS ARE NOT THE CLASS EITHER — THEY ARE THE ONLY THING THAT NOTICES IT

Faulting instruction, from gdb: `movaps %xmm0,-0xc0(%rbp)` inside `__vsnprintf_internal`, with
`si_code=SI_KERNEL(128)` and **`si_addr=0x0`**. That triple is the signature of a **misaligned SSE store**,
not a bad pointer — and `si_addr=0` is what stops this being read as a null dereference. `[stack]` is mapped
`0x7ffffffde000-0x7ffffffff000` and RSP was inside it, so it is not exhaustion either.

Entry RSP at the runtime call boundary, measured with `break *symbol` (⚠ **plain `break symbol` skips the
prologue and answers a different question** — it read the *correct* value for the crashing case and cost one
wrong conclusion before it was caught):

| witness | path | entry RSP mod 16 | ABI wants | result |
|---|---|---|---|---|
| record via `suspend` | generator | **0** | 8 | SIGSEGV |
| list via `suspend` | generator | **0** | 8 | *passes* |
| record via `return` | plain call | 8 | 8 | passes |

**Every generator path is misaligned.** Lists and strings pass only because `rt_make_list` reaches no aligned
SSE spill. A record reaches `dat_construct` → `rt_fire_buildplan_tweak`, whose
`snprintf(proc, sizeof proc, "%s__TWEAK", chain[i])` compiles to `movaps`. So the visible symptom is one
unlucky callee away from being anywhere, and "records crash" is a fact about `snprintf`, not about records.

## THE CAUSE, AND THE COMMENT THAT ASSERTED IT WAS FINE

`src/templates/bb/bb_call_proc_staged.cpp` emits, at every `call_proc_staged` site: a `PL-CALL-ALIGN` pad plus
the `L(7)` push (16 bytes, parity-neutral), then **under `icn_gen_regime()` only** a lone "N-2 STEP 3 REGION
HAND-OFF" push (8 bytes, **parity-flipping**), then the wire pair (16 bytes, neutral), then `jmp` into the
callee.

⭐ **The `PL-CALL-ALIGN` pad is an earlier cure of THIS SAME CLASS** — its own note names the symptom
exactly: *"one bare 8B push here left rsp 8-mod-16 ... a real ABI violation (SIGSEGV in a later vsnprintf
movaps; witness prolog-call-n-user-predicate-segfault)"*. Prolog was cured; Icon then had an unpadded lone
push added next to it.

⛔ **The region-handoff line carries a comment asserting the opposite, and it is the finding:**

> *"Alignment: one extra 8B word flips nothing that matters -- the ABI-sensitive calls (open_det above,
> args_install inside the callee) keep their old mod-16 classes because the callee no longer subs its ft."*

Both calls it names are genuinely unaffected: `open_det` **precedes** the push, and `args_install` was
checked. What it never considered is the **callee body's own runtime calls**, which inherit the parity across
the `jmp` — an unbounded set the author could not enumerate, so the claim was scoped to what was enumerable
and stated as though it covered everything. Measured: `rt_proc_call_open_det` entry is a correct 8-mod-16,
and `rt_call_arr_bl` — reached from inside the callee — is 0.

⭐ **The reusable shape: an alignment claim is a claim about a whole call subtree, and a comment that lists
the calls it checked is evidence about those calls only.** This one has been true-sounding and wrong in the
tree since s283, and it reads as diligence.

## A CURE DIRECTION MEASURED WRONG, RECORDED SO IT IS NOT RE-WALKED

Padding the region push in place — `lea` first (its rsp-relative slice constant is computed pre-pad), then
`sub rsp,8`, then the push, keeping the region at `[entry rsp+16]` — **does** restore 8-mod-16 and **does**
cure all five record witnesses. It also **breaks the co-expression path**, which then SIGSEGVs in
`scrip_coswitch` → `rt_scan_state_capture` → `malloc`: something in the region/wire contract depends on that
exact distance. The ω-landing counterpart (`add rsp,16` → 24) changed nothing either way, isolated by
reverting it alone. **Reverted whole; the landed tree is byte-identical to the pre-experiment tree**
(`git status` clean, and every pre-experiment witness result reproduces).

⭐ Two things that only showed up because both arms were run: the omega landing was proven **balanced** by a
3,000,000-activation loop (a 24MB leak against an 8MB stack would be unmissable) — a 200,000 loop was my first
attempt and was **too weak to distinguish anything**, since 1.6MB fits comfortably; and the two edits together
produced a mixed result that was only interpretable after isolating them.

## WHAT LANDED

`scripts/test_gate_icn_suspend_record_stack_alignment.sh`, **proven RED (rc=1)**: 5 witnesses red, **3
controls green pre-cure** (`suspend` a list, `return` a record, a co-expression over an integer generator).
The controls are the working part of the gate: they are *equally misaligned* and simply never reach an SSE
spill, so a "cure" that merely routes records around `rt_fire_buildplan_tweak` turns the gate green while
leaving every other Icon generator call one unlucky callee away from the same crash. Verified green **before**
being called controls, per hq_B's condition and hq_I's own 09-05 correction that a control red before the cure
is a witness with a misleading name.

⛔ **No `src/` change landed.** `bb_call_proc_staged.cpp` is lowered to by Prolog, Icon and SNOBOL4 — a shared
node, so the cure is authored by the exposing lane and **co-signed by hq_U**, and the region contract is
hq_B's N-2 design (ceo s283). Routed to both.

## SIDE RESULT: hq_T's CHARSET CLASS DOES NOT REACH ICON, AND THE REASON IS STRUCTURAL

hq_T asked for one Icon probe of `charset-primitive-loses-its-set-after-a-null-alternation-branch`, on the
premise that "the box is shared". Probed `many`/`any`/`upto` behind a null-matching alternation branch with a
non-foldable cset operand: **SCRIP agrees with iconx on all three arms, both modes.** The premise is the part
to correct — Icon's `many`/`any`/`upto` lower to `IR_SCAN_*` → `bb_scan_{many,any,upto}.cpp`, while SNOBOL4's
SPAN/ANY/NOTANY/BREAK lower to `IR_MATCH_*` → `bb_match_{span,any,notany,break}.cpp`. **Different boxes**, so
Icon never reaches the node. A negative probe alone would have been weak evidence; the lowering split is why
it is a real answer.

## SIDE RESULT: THE IPL COMPILE/RUN GAP IS THE INSTRUMENT'S DESIGN, NOT AN ANOMALY

The ceo held the 20-row IPL batch pending confirmation that the 64 newly-compiling programs simply lack `.std`
refs. Confirmed **structurally, without re-running the suite**: `test_icon_ipl_suite.sh:123` builds `STDFILES`
from `find "$PKG" -name "*.std"` and line 235 loops over **that list**, never over the compile tier's results.
So `compile_pass` moving 544→608 **cannot** move the run tier — the two tiers are decoupled by construction.

Census: **64 `.std`, all in `progs/`, zero orphans**; the four newest by git add-order are exactly
`cross/lisp/parse/turing`, seat07's mints — so `run_graded` 60→64 came entirely from **ref-cutting**, not from
compiling. The mintable pool is **211** (`progs/` holds 275 `.icn`, 64 have a ref). ⛔ And one the framing did
not name: **`gprogs/` ships 177 main programs and ZERO `.std`** — a whole program directory structurally
outside the run tier. The real ceiling is 388 ref-less main programs against 64 with a ref.
