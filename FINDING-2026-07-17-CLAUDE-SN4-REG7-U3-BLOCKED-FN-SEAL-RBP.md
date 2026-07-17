# FINDING 2026-07-17 (s82, Claude, attended) — U3 BLOCKED BY PRE-EXISTING FENCE-SEAL RBP WOUND

**ONE LINE:** U3's consumer flip greens build+smokes but segfaults 067_pat_fence_fn_vs_kw (m3 303→302); the root cause is a pre-existing fence-seal abandon that restores rbp from a slot whose value is zero — U3 makes rbp load-bearing and detonates it. U3 patch preserved; fix the wound first, then `git apply` the patch.

## WHAT LANDED THIS SESSION (s82)

| Commit | Rung | Content |
|--------|------|---------|
| `aa5d7249` | U1 | Outer-graph rbp seed BOTH twins (`48 89 E5` / `mov rbp,rsp`) beside REG-4b/REG-6 seeds |
| `b59bcdf5` | U2 | Non-pat jmp-entry blobs: caller-rbp save at `[rsp+kt-8]`, `mov rbp,rsp` seed, restores on BOTH exit edges |
| `552cb02a` | U2b | Blob restores flip to self-referential `[rbp+kt-8]` (`48 8B AD`) — depth-immune, FRQ-restore discipline |

All three watermark-exact: **m3 303/4 · m4 293/13/1 · DIVERGE=10 identical names**.

## U3 PATCH LOCATION

`SCRIP` is clean (U3 reverted). The patch is at:
`.github/PATCH-2026-07-17-SN4-REG7-U3-PARKED.patch`

To re-apply after FN-SEAL-RBP is fixed:
```bash
cd /home/claude/SCRIP && git apply /home/claude/snobol4ever-github/PATCH-2026-07-17-SN4-REG7-U3-PARKED.patch
```
Then rebuild, gate, commit with the U3 message.

## THE WOUND — FN-SEAL-RBP

**Symptom:** 067_pat_fence_fn_vs_kw segfaults in m3 post-U3 with `rbp=0` at the first frame store (`movq $0x1, 0x190(%rbp)`).

**Confirmed by gdb probe series:**
1. The slab IS correctly seeded at entry (`mov %rsp,%rbp` at `0x7ffff5e00023`) — U1 lands.
2. The statement-2 head save fires twice (`mov %rbp,0xc8(%rsp)` at slab+0xa6), rsp identical both hits, **rbp=0 at both arrivals** — the seed is correct but something resets rbp to 0 before stmt-2 even runs.
3. The sole rbp-writer between the prologue seed and stmt-2's head is the **stmt-2 abandon-restore** at slab+0x155: `mov 0xc8(%rbp),%rbp` — self-referential, reads from a slot that holds 0 because rbp was 0 when the save executed at stmt-1's release/abandon.
4. The stmt-1 release (`bb_match_release`) restores rbp from `FRQ(op_off+40)` — i.e. `[rbp+200]` — on the success edge. That slot is saved by stmt-1's own head via `mov %rbp,0xc8(%rsp)` (= `[rsp+200]`). The divergence: **the save spells `[rsp+200]` but the restore spells `[rbp+200]`** — these are the same address ONLY if rbp==rsp at save time.

**Working hypothesis:** stmt-1 is a `&FENCE` keyword match. The fence-keyword class is in the pre-existing DIVERGE list. Under m3, when `&FENCE` aborts and the seal-cut exit fires, rsp may be displaced (cells pushed), so `[rsp+200]` saves at a different address than `[rbp+200]` reads. After restore, rbp = whatever was at `[rbp+200]` = zero (zeroed frame memory). U3 then exposes every subsequent `[rbp+off]` write as a null deref.

**Next probe (one gdb command):**
```bash
gdb -batch -ex "break *SLAB+0xa6" -ex run \
  -ex "printf \"stmt1save rsp=%p rbp=%p rsp+200=%lx\\n\", $rsp, $rbp, *(long*)($rsp+200)" \
  -ex "continue" \
  -- ./scrip --run 067_pat_fence_fn_vs_kw.sno
```
If `rsp+200 != 0`: save is correct, wound is in restore or the fence-seal unwind.
If `rsp+200 == 0`: stmt-1 head never ran (seal bypass) or ran at wrong depth.

**Fix class:** the rbp save in `bb_match_head` for the NON-flat_pat case currently spells `rspq40(op_off+40)` — explicit rsp-relative — and the restore in `bb_match_release` spells `FRQ(op_off+40)` — now rbp-relative post-U3. One of those must become consistent with the other. The right answer is `FRQ` (= `[rbp+off]`) at BOTH sites — then the save/restore pair is always self-referential through rbp, depth-immune. `rspq40` is an s79 artifact written before the universal rbp seed existed; it can now be replaced.

## NEXT RUNG FOR FRESH SESSION

**FN-SEAL-RBP** (before U3 re-apply):
- [ ] Confirm the `rspq40` / `FRQ` mismatch diagnosis with the one-shot probe above
- [ ] Fix `bb_match_head` save site: `rspq40(op_off+40)` → `FRQ(op_off+40)` (both arms: flat_pat already uses `FRQ`; the non-flat_pat arm is the wound)
- [ ] Rebuild, gate: expect 067 greens in m3 and the pre-existing m4 fence DIVERGE family may move
- [ ] `git apply` the U3 patch, rebuild, crosscheck — expect clean or a smaller residue
- [ ] If clean: proceed to U4 (deletions) per the FINDING ladder

## LADDER STATUS AFTER s82

- [x] **U1** — Outer seed `aa5d7249`
- [x] **U2 + U2b** — Non-pat blob protocol `b59bcdf5` + `552cb02a`
- [ ] **FN-SEAL-RBP** — Fix the rspq40/FRQ save-restore mismatch (NEW — gates U3)
- [ ] **U3** — Consumer flip (patch ready; re-apply after FN-SEAL-RBP)
- [ ] **U4** — Deletions (op_anchored/op_anchor_head + registrars + tail-grant — Lon decision on tail)
- [ ] **U5** — +40 reclaim + zr seal (Lon ruling on flat_pat arm)
