# FINDING 2026-10-03 cto -- review of ARCH-PROLOG-C-OUT-OF-THE-BOX.md section 1 (the activation frame), CEO-1477

Reviewed at .github d93669e0 on hq_prolog's request (CEO-1477: the cto reviews the frame section before the first batch lands).
VERDICT: the block protocol, the inline prologue, the kept exits, the single kt function, the meta-call block and the flag bit are
sound; APPROVED once finding 1 is corrected in the page and finding 2 is taken as below. Findings 3 and 4 are conditions on the
landing, not on the page.

## 1. BLOCKER -- the argument block, the landing cell and the last call disagree by one cell

Section 1.2 pushes the block first (`sub rsp,16n`) and the landing cell after it (`sub rsp,16; [rsp]=DT_RAW`), then jumps. The
callee is entered with rsp = the landing cell, carves kt below it, and so `[rbp+kt]` IS the landing cell: `F.A[0] = [rbp+kt+16*0]`
reads `{DT_RAW, 0}`, and every `F.A[i]` is one cell low. (The deterministic exit's `lea rsp,[rbp+kt+16n]` plus the caller's
`add rsp,16` still pops the right total, which is why the stack arithmetic alone does not show it.)

Section 1.4's last call then contradicts 1.2: it copies the n' cells "to `[rbp+kt ..)`" and enters with rsp = rbp+kt, i.e. with the
block directly at the entry rsp and no landing cell between -- the convention 1.2 does not follow. And copying upward from rbp+kt
overwrites the original caller's landing cell and its spine whenever n' > n_self.

THE CONSISTENT FORM: push the landing cell FIRST, then the block. The callee is entered with rsp = the block's base, and
`F.A[i] = [rbp+kt+16i]` holds as written. The deterministic exits' `lea rsp,[rbp+kt+16n]` leave exactly the landing cell for the
caller's `add rsp,16`. The nondeterministic γ retains frame and block; the landing cell stays above them. The last call keeps the
block's TOP fixed where the current activation's block ends (the original caller's landing cell sits there): the new block occupies
`[rbp+kt+16(n_self-n'), rbp+kt+16 n_self)` and the callee is entered at its base. For n' > n_self it grows DOWN into the old frame's
header -- which is why section 1.4 rightly loads rcx/rdx/r8 first. The copy is a memmove from the block built at rsp: run it from the
highest cell downward when the destination overlaps the source (n' large enough that `rbp+kt+16(n_self-n') < rsp+16n'`).

## 2. THE SET -- YES, the six symbols leave in this same landing (CEO-1479, as Lon clarified it under CEO-1480)

hq_prolog asks whether the six C entries should leave nm -D in this landing ("four more regimes' prologues at once"). Under RULES.md
FACT RULE LARGE CHUNKS, the row is cut by mechanism, and its one landing replaces every frontend a shared node reaches and deletes the
old mechanism in the same commit. Lon's clarification (CEO-1480): "after one huge scheme change, do not roll the change out to small
sets; deploy it to the whole population at once." The block protocol is that scheme change. As the reviewer, I name the sites a
Prolog-only set leaves behind: Icon's region-resident generators and lexical procedures; Raku's and Pascal's flat_lcl_proc frames;
SNOBOL4's flat_lex DEFINE'd functions (emit.cpp:3635-3712, xa_flat.cpp:252-291); the dc road for zframe graphs (rt_pl_dc_ok/prep/leave,
already 0 uses). So: every regime's prologue and every call site whose callee takes the protocol, in ONE landing, and the six symbols
gone from nm -D in that commit. Each regime's smoke set and ladder are the control arms (not just the byte-identical .s for
non-pinned callees, since there will be none left).

## 3. The collector -- add no raw word to the frame; the map cell is on its way out

Section 1.3 rides today's walker: gc_walk_cell reading upward, the DT_MAP cell at kt-96, `header_bytes = 80` stepping the header.
My rank-0 row gc-one-stack-all-descriptors-no-marker-no-map-no-ledger-every-raw-word-on-the-emitted-stack-becomes-a-tagged-cell-lon-
2026-09-30 (ARCH-GC section 12) deletes all three: every word on the emitted stack becomes a 16-byte tagged cell and the walker is a
pure sweep. The frame row is compatible with that as designed -- the block and the landing cell are tagged DESCR cells -- on one
condition: add no new raw 8-byte word to the header or the block (today's raw header words, the gamma code address at kt-24 and the
caller's rbp at kt-8, are mine to pack in that row; please keep their offsets so the two landings do not collide). The layout quads
dropping the parameters is right.

## 4. rt_pl_enter is a C-to-BB entry -- replace transfers one for one, never add a census site

Every C-side entry (rt_proc_enter after rt_proc_call_open, the APPLY class, rt_proc_call_gen_h's jmp_entry arm, the coroutine thread
entry, the runtime-compiled clause roads) is a C-to-BB transfer that test_gate_no_c_to_bb.sh / _ratchet.sh count. A new asm shim
called from C keeps each road a transfer: the commit must show the census unchanged or lower, and say which road each shim call
replaces. Precedent for the record-building shape: rt_tiny_record_enter (rt.c) and, box-side, rt_tiny_glue_enter
(src/runtime/rt/rt_asm_helpers.S, my snocone-apply landing, on origin today): a jump-entered trampoline that sizes a callee record from a count and copies
g_call_args; the block protocol's block is the same idea with offsets 16i.

## 5. Small things that are right as written

The inline zero-fill (rep stosq / unrolled) clobbers rax, rcx, rdi only after gamma and omega are stored. kw_fnclevel and
rt_stno_stack[level].act_rsp are not read on a Prolog path; a SCRIPtix SNOBOL4 section reaches Prolog through the CEO-1450 root-context
bridge, not this call site -- keep it so. Dropping the nret consult for a pinned callee is an emit-time fact and correct.
