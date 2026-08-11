# FINDING 2026-08-11 — CONSOLIDATED (Opus 5) — FF-0 CLOSED: BLOB γ/ω/res NEVER RESTORE RBP; EVERY DEFER SUSPENSION LEAKS THE ARBNO VIEW INTO THE INVOKER; THE 2/15 BOARD IS THIS ONE DEFECT

**Fingerprint:** SCRIP `69e5f380` (parent `4b48dbb9`) · corpus `5da04e78` · oracle `/home/claude/x64/bin/sbl` · canonical paths · `RT_OPT=-O0` · `ulimit -s unlimited`.

## THE CONVICTION CHAIN (each step measured this session)
1. **Witness** `treebank-match.sno < treebank.input` (327 B) rc=139 m3; oracle `matched bytes=327`.
2. **gdb (handler off, two-stage breakpoint — see §METHOD):** crash `mov 0x48(%rbp),%eax` with **rbp=0x1f=31, a cursor value**, in the chain-arm as sequence (count++ then `mov %r14d,0x44(%rbp)`), immediately after the view restore `mov rbp,[rbp+88]` — the element's prev-view slot held 31.
3. **Writer census (m4 asm):** the ONLY rbp writers inside pattern code are the chain-arm view dance (`mov rbp,rsp` · `mov rbp,[rbp+N]` · `lea rbp,[rax-88]` clusters ×3 sites) + licensed statement-side keepers. Survivor claws5 carries one chain cluster too.
4. **Route diag (`SCRIP_ARBNO_DIAG=1`):** all three treebank sites route **legacy via sq=0** (alternation bodies) — the entrance MECH s38 scoped as the later K16 rung; not reachable by the kk==0 body-cell retirement.
5. **The keystone (m4 blob disasm, `proc_PAT$0_γ/ω/res`):** the CLASS-D suspension protocol **never saves or restores rbp** — γ pops ctx, pushes {res,base}, jumps the consumer wire; res re-pushes ctx; ω drains absolutely. rbp crosses every activation boundary carrying whatever the interior left. Pre-DEL-T1 this was accidentally consistent (resume restored the blob frame, which WAS the view root). **DEL-T1 (`1af93e3a`) broke VIEW CONTINUITY, not merely root placement.**
6. **Blast-radius unification:** SEGV set = exactly the defer-carrying programs (treebank ×2, json ×2, calculator-1, treebank-list/array — recursive `*` patterns); survivor set = the defer-free (claws5 ×2). One defect, whole board.

## STRANDED-REPAIR RECOVERY (corrects MECH s38b's record)
The six "concurrent seat" hashes (SCRIP `7dfb803a`/`560c63e4`, corpus `0affc04e`/`e707f815`/`091d45cc`/`d24999fa`) are **MISSING from origin** — but the CONTENT is at HEAD under rebased hashes: `bb_match_arbno.cpp:45` carries the TWO-CALCULATORS-RETIRED β-pop deletion (`SCRIP_ARBNO_FPRPOP`, default 0). The fix was not lost; the s38b hash citations are dead. Do not attempt to fetch them.

## EXPERIMENT: ROOT-SPINE α (landed as dormant scaffold `69e5f380`)
`SCRIP_ARBNO_ROOTSPINE=1`: chain-arm α carves a 48 B spine root record {anchor,yield,count,chainhead,exhaust,saved-rbp}, view0=root−op_off so every FR(op_off+X) spelling resolves [root+X] unchanged; exhaust stores pre-carve rsp so L(2)'s pointer restore self-releases the record — the FORTH way.
- **Correct-half proof:** witness crash signature persisted but the corrupted slot moved from the (formerly shared) frame header to the ELEMENT's prev-view slot — root aliasing eliminated, continuity defect remains.
- **Insufficiency proof:** claws5-match (defer-free survivor) **SEGV under =1** — every yield exit (ε-γ and each PAIR(2) prev-view restore) terminates the view chain at root−op_off instead of the statement frame, leaking a view into downstream FR readers. The complete arm must restore true rbp from [root+32] at every γ exit.
- **Default 0, byte-identity proved:** m4 md5 equal to parent on claws5-match (`8ef0cf77…`) and treebank-match (`e80364d3…`); survivors IDENT vs oracle.

## ⛔ THE FORK — LON RULING NEEDED (blocks FF-1 completion; both shapes zero-new-frames)
**(a) Arm-local:** ARBNO root carved inside the OWNING activation's kt region (blob) / statement claim (main); as/af re-derive the view from ctx base (`g_zctx[8]`) + static offset; every γ exit restores true rbp from the root. Touches only bb_match_arbno + zls layout; leaves the activation protocol untouched; per-arm instruction cost at every entry/exit.
**(b) Protocol bracket:** the activation header (s37(A) shape, hdr+0..32) grows one word = saved invoker rbp; γ/ω/res restore it. One bracket repairs EVERY future interior rbp customer; arbno arms then need only the root-spine α (already scaffolded). Touches emit.cpp CLASS-D protocol — the header Lon shaped in s37(A); smallest total instruction count.
Recommendation: **(b)** — it is the licensed-keeper pattern (save/restore at the boundary, rbp never re-pointed, pass-thru preserved), it makes the invariant "rbp is ALWAYS the statement frame inside pattern code" true by construction, and it is one mechanism instead of N arm repairs. But (b) touches the protocol, so it is Lon's call, not this seat's.

## METHOD (reusable)
- JIT-slab breakpoints: plant only AFTER emission completes (first-hit on a MATCH-time rt symbol, e.g. `rt_defer_get_pat_fn`), never at registration time — the emitter overwrites earlier-planted INT3s (measured: zero hits, crash 4 bytes past the trap).
- Slab addresses are stable across gdb runs in this container — cross-run address reuse is sound.
- ARCH-ICON.md's register contract still shows flat_pat as rbp-pinning — STALE post-DEL-T1; the FF manifest supersedes.

## GATES FOR THE NEXT SEAT (in order)
witness 327B byte-equal → D12/D13 → claws5 pair IDENT → `board_sno15_ident.sh` ≥9/15 both modes → probe suite both modes (m4 with `SCRIP_RTCC=0`) vs REGRESSION {D12,D13} → regen ×3 → speed board vs the s34b bars (claws5 1.61×/1.68×, treebank 1.05×/1.57×, calc-1 1.33×/0.98×).
