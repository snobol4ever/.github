# FINDING 2026-09-05 hq_P — DEFINE redefinition: the SNOBOL4 call site is STATICALLY BOUND, so re-registration never reaches it

⛔ **This SUPERSEDES §3 and §5 of `FINDING-2026-09-05-hq_P-define-redefinition-is-deduped-at-compile-time-so-the-last-define-wins-retroactively.md`.** That finding's §2 (the compile-time `defs[]` dedupe) is CONFIRMED and unchanged. Its §3 conclusion — *"the ordering machinery is already correct … the existing `rt_define_site` chain gives correct last-wins-at-execution-time semantics with no runtime change at all"* — is **WRONG**, and its §5 three-part cure is therefore incomplete: it would have produced two bodies that nothing ever dispatches to.

**Measured:** hq_P, 2026-09-05, SCRIP `23f342b4d` (incremental `make`), both modes, oracle `/home/resources/x64/bin/sbl -bf`.
**Row:** `define-redefinition-ordering` (rank 3, hq_P lane) — **released FREE, still RED, not cured.**
**Witnesses:** `user_function_replace_4`, `user_function_replace_7` (both re-verified red at fix time, both modes byte-identical wrong).

## 1. The correction, and how it was found

The previous sitting read the *registration* path and found it correct: both `rt_define_site` calls are emitted at their own statement in program order, and `rt_define_site` (`rt.c`) really does find the existing proc, set `p->redefined = 1` and repoint `p->fn`. All of that is true.

**It is not what the call consults.** The emitted call site is:

    n8_call_α:   sub  rsp, 16
                 lea  rcx, [rip + .Lcall_α_sig43z]
                 lea  rax, [rip + F_α];   jmp   rax        ← compile-time bound, no cell read

⭐ **`p->fn` is written by every DEFINE and read by nobody.** A dispatch mechanism that is correct, ordered, and firing twice is worthless if the call site was bound at compile time — and from the program's stdout the two situations are indistinguishable, which is why two sittings in a row certified the wrong layer as healthy.

⭐ **The transferable shape, and it is the second one this row has produced: VERIFYING THAT A MECHANISM IS CORRECT IS NOT VERIFYING THAT IT IS CONSULTED.** The first correction (a correct ordered mechanism fed a deduped table) and this one (a correct ordered mechanism nothing reads) are the same error wearing different clothes: both times the subsystem under the microscope was working, and both times the defect lived in what *fed* or *ignored* it. The cure for both was one `grep` of the emitted asm at the CALL site rather than the DEFINE site.

⛔ The killswitch `SCRIP_NO_TINY=1` does NOT expose this — measured, no change on either witness. With only one body emitted, no dispatch discipline can pick a different one, so the dynamic path reaches the same wrong code. **A killswitch that cannot change the answer is not evidence that the axis it gates is innocent.**

## 2. There are FOUR layers, not three

| # | layer | state on my tree | file |
|---|---|---|---|
| 1 | `defs[]` keyed by `fname` alone → the second DEFINE overwrites the first | **CURED** — key is now `(fname, entry)`; same-entry still overwrites (so the prescan/statement double-visit of ONE statement still merges, which a naive "append always" breaks) | `lower_snobol4.c` :2451 :2607 :2627 |
| 2 | one `proc_table` entry per name → one emitted body | **CURED** — each binding gets its own prologue-bearing stub; the LAST keeps the plain name, earlier ones are `<fname>$<k>` so alpha labels cannot collide, and runtime registration/result-name/single-DEFINE programs stay bit-identical | `lower_snobol4.c` proc loop |
| 3 | driver pairs a bind node to the first proc of that name | **CURED** — the k-th bind node for a name pairs with the k-th binding (`<fname>$k`, else the plain name) | `scrip.c` dentry loop |
| 4 | **the call site is statically bound** | **THE MISSING LAYER** — gated it on a new `bb_fn_multibound()` so a multi-bound name dispatches through `rt_proc_call_open_slim`; verified in the asm | `bb_call_proc_staged.cpp`, `bb_define.cpp` |

Layers 1–3 are what the superseded §5 proposed. **On their own they cure nothing** — they emit a second body that the statically-bound call never jumps to.

## 3. Where it stands — NOT cured, and what remains

Working tree **reverted to clean**; the defect was re-confirmed present and the single-DEFINE control arm green on the reverted tree, so nothing here was read off a modified binary. The four-layer patch is preserved verbatim at `.github/wip-patches/define-redefinition-ordering-hq_P-2026-09-05-three-of-four-layers.patch` (220 lines, 7 files).

With all four layers applied:
- ✅ single-DEFINE control arm green in **both** modes (`got:a` / `got:b`) — the general path is untouched.
- ✅ m4 emits both stubs (`F$0_α` → `LBL__F`, `F_α` → `LBL__G`), both bind sites register their own, call sites go dynamic.
- ⛔ **m4 SIGSEGV** on both witnesses at a `jmp *%rcx` inside the stub region. Suppressing the M4-ALPHA-SEAL was tried and is NOT the cause (re-pointing the seal per binding did not clear it).
- ⛔ **m3 unchanged (still wrong).** Root cause identified: the stub realization is role 5 in `emit.cpp`, gated on `g_is_text` — **it is a TEXT-only path, so the BINARY mode never emits a per-binding stub at all.** m3 needs its own realization, not a shared one.

⛔ **Do not treat the patch as nearly-done.** Two of four layers are proven end-to-end; the m4 fault and the m3 TEXT-only gate are unsolved, and the m3 half is a genuinely separate piece of work.

## 4. For whoever takes it next

1. **Re-verify at fix time, from the asm, at the CALL site** — not the DEFINE site, and not from stdout. Both of this row's corrections came from there.
2. The blast radius is unchanged and real: DEFINE dispatch is shared ground for every SNOBOL4 program with a function, so this lands with the full master both modes plus the Icon watermark — never the two witnesses alone.
3. The `(fname, entry)` key matters: "append always" double-counts, because one top-level `DEFINE(...)` statement is visited by BOTH `sno_prescan_expr` and the statement branch.
4. `$` in a proc name is already established (`fn_cell$F`, and `scrip.c:676` already guards on `strchr(pe->name, '$')`), so the `<fname>$k` naming needs no new convention.

## 5. Adopted from the ceo's 14:19 message, unrelated to this row but landing in my practice

seat15's `dfee908e` deleted 115 lines of `SCORE.md` under a FINDING commit — the rebase near-miss class, landed for real. **Standing check from here: after ANY conflicted rebase, `git diff --cached` against what you meant to change, before committing.**
