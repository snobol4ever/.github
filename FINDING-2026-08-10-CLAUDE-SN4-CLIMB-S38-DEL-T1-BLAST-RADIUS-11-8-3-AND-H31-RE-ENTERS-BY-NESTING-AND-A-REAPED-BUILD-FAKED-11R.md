# FINDING 2026-08-10 s38 (Fable 5) — DEL-T1 blast radius 11→8→3 · H31 re-enters by NESTING · a reaped background build faked 11R

**Trees:** SCRIP `a5533659` · corpus `f728c278` · zero code landed. Convergent with the 08-10b seats + CLIMB s37 (independent bisect, same conviction `1af93e3a`); this FINDING records only the deltas.

## 1. Blast radius: 11 broken → 8 repaired → 3 residual

Method: clean private-OBJ foreground builds (`make OBJ=/tmp/objs_* -j1 scrip`, exit-checked) at three commits; all 11 candidate witnesses run `--run </dev/null`, rc + full-output compare vs `.ref`.

| Commit | D06 | D09 | D10 | D11 | D12 | D13 | H20 | H21 | H31 | X07 | X08 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `930539c0` (parent) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `1af93e3a` (DEL-T1 D-1) | 139 | 139 | 139 | 139 | 139 | 139 | 139 | 139 | 139 | 139 | 139 |
| `a5533659` (HEAD, post D-2/D-3) | ✅ | ✅ | ✅ | ✅ | **139** | **139** | ✅ | ✅ | **139** | ✅ | ✅ |

One commit broke eleven; D-2 `1f96143c` ("partial repair", its own words) + D-3 `ef8a3052` restored eight; the 3R are the remainder. Consequence for **M-1b acceptance**: `{D12,D13,H31}` green both modes AND `{D06,D09,D10,D11,H20,H21,X07,X08}` stay green — GLOBAL-EXECUTE deletes the layer D-2 built, so the repaired eight are its regression guard, not background.

## 2. H31 answers s37's open question: same class, second species

s37: "H31 … NO recursion, yet it fails identically — either re-enters by a path worth naming or is a second class hiding in the same rc."

Named. Emitted-asm census (`--compile`, grep `proc_PAT$` / `g_blob_ctx`):

| Probe | blobs | ctx refs | activation shape | HEAD |
|---|---|---|---|---|
| D06 | 2 | 12 | SEQUENTIAL — two statements, never co-live | ✅ |
| D09 | 1 | 6 | single | ✅ |
| D12/D13 | 2 | 12 | RECURSIVE — `*LIST` re-enters in one statement | 139 |
| H31 | 7 | 42 | NESTED — `pair` live → `value` enters → `bool` enters (FENCE-in-FENCE) | 139 |

`g_blob_ctx[5]` is ONE global cell; each blob α overwrites it; any outer activation still live then reads the inner's cells. **Discriminator, sharpened: >1 simultaneously-live blob activation.** Recursion and nesting are the two species of the one class; static blob count is not the predictor (D06's 2 pass, D12's 2 crash). The 3R witness set spans both species by construction — no fourth acceptance witness needed.

## 3. Exoneration sweep (do not re-run these)

At HEAD on D12: `SCRIP_{PAT_INLINE,RTCC,AB,ARBNO_LATCH,CALL2BB,STMT_FRAME}` × {0,1} — all 12 arms crash · `ulimit -s 65536` — same · `setarch -R` — same · 5/5 deterministic. No killswitch or environment rescue exists; structural only, consistent with the s36c delete-the-global ruling.

## 4. Revert is mechanically dead (fact under s37's policy bar)

`git revert 1af93e3a` on `a5533659` CONFLICTS in `src/emitter/emit.cpp`: D-2 did not patch the deleted region, it REPLACED the design — interior readers now speak `rsp+op_flat_disp`, the β res-stub refills ctx from the carve header. Resurrecting the pin breaks HEAD's readers even for the owner. Moot under M-1b forward deletion; recorded so nobody spends a build testing it. (Revert aborted; tree verified clean.)

## 5. My land mine: a reaped background build faked 11R at HEAD

Mid-session this seat reported m3 **125/15/11R** at `a5533659` and hypothesized stale parallel-seat builds. Wrong on both counts, and the mechanism is the build-side twin of s37's container lesson (background jobs are reaped between tool calls):

- First build launched `nohup make -j1 &`; reaped between tool calls; log came back EMPTY; absent `make` process misread as completion.
- The suite ran ~20:0x against a partially-linked binary; the finished binary's mtime is **20:22:52** — postdating the measurement.
- Verified clean rebuild (`make clean; make -j1`, 263 compile lines, foreground, exit 0) reproduces **133/15xf/0/3R** exactly. s35/s36/MECH watermarks were right; the tree was innocent; the false number was retracted before any commit or cursor carried it.
- Second hazard found while correcting: Makefile `OBJ := /tmp/si_objs` is one shared object dir across every checkout and worktree — a bisect or worktree build inheriting another checkout's objects would silently mis-measure. Every bisect step here used a private `OBJ=`.

Both hazards → CLIMB METHOD item 8 (s38): a watermark requires a verified binary — foreground, exit-checked, mtime predating the measurement; private `OBJ=` for bisect/worktree builds.

## Lon items

1. s37's park question, +1 with a reason: three seats have independently re-proved the same 3R; park as XFAIL tagged `M-1b` (removal in the repair commit per RULES §4) so a real regression is visible against green. Lon rules.
2. Protocol suggestion (HQ, not landed here): a DELIBERATELY-BREAKING commit should cross-post one line into each concurrent goal's cursor at land time — s36 spent a session calling this trio "unowned" while the owner had declared itself in the commit message.
