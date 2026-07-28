/* seed/test_sno_cell_1.s — HAND-WRITTEN REFERENCE EMBODIMENT #1 of the ζ-CELL MACHINE (contract: DESIGN-SN4-CELL-MACHINE.md; ladder: GOAL-SN4-CELL-MACHINE.md; Lon + Claude, 2026-07-28).
 * Assembles standalone: gcc -nostdlib -no-pie test_sno_cell_1.s -o t && ./t  →  "CELL MATCH start=2 end=7".  Flip subj to "abhexlo" → "CELL NOMATCH".
 *
 * ═══ WHAT A CELL MACHINE IS ═══
 * A cell machine is an execution model for a Byrd-box graph (every construct a four-port box: α start, β resume, γ succeed, ω fail) in which ALL match-lifetime state lives as
 * uniform typed CELLS on ONE LIFO stack, and in which a control transfer and a stack-depth transfer are THE SAME ACT — you never arrive at a resume point except by popping the
 * cell that names it, and the pop leaves rsp exactly where the pusher stood.  Its laws:
 *   1. PER-BB SELF-ALLOCATION.  Each box allocates its own memory — RESULT and LOCALS — callee-side at its α (`sub rsp, K_box`, a box-local constant; no graph-wide geometry pass
 *      exists).  Freeing is caller-side on both return edges: γ = the consumer consumes/overwrites the result cell (or the box shrinks-to-result itself); ω = the cut reclaims the
 *      box, its consumed operands, and the whole abandoned suffix wholesale.  Recursion, EVAL/CODE, and stored-pattern entry fall out free: a fresh entry carves a fresh frame,
 *      and runtime-created code needs no compile-time frame plan because none exists.
 *   2. ADDRESSING IS SELF-RELATIVE, ALWAYS.  A box reads only its own carve at [rsp+0..K) and its operands — the top n 16-byte DESCR cells its children just left at
 *      [rsp+K..K+16n).  Producers deliver at TOS (a POSITION, not an address); ownership transfers to the consumer by LIFO adjacency.  No box ever holds another box's address,
 *      so the reach-over disease (static cross-box displacements kept honest through dynamic depth — op_flat_disp, fc_geom prefix sums, parked anchors, rbp floors) is not merely
 *      prevented: it is UNREPRESENTABLE.
 *   3. CP CHAIN.  rbp is CP, the pointer to the newest CHOICE cell (WAM's B register; callee-saved, so it survives every C runtime call).  A choice cell is 32 bytes:
 *      [+0]=resume addr · [+8]=low32 saved-δ / high32 TAG (0=CHOICE 1=BASE 2=FENCE 3=ARBNO_GUARD) · [+16]=prev_CP · [+24]=saved mark-head (MH=r12 once capture marks land).
 *      Backtrackable boxes obey the LAW: carve LOCALS first, THEN push the header at TOS — so the fail stub's pops land rsp exactly at the box's own locals base at every β.
 *   4. UNIVERSAL FAILURE.  ω everywhere is ONE shared stub: cut to CP, pop resume/δ/prev-CP, discard MH slot, jmp resume — six instructions, correct from ARBITRARY depth.  The
 *      entire ω-edge topology of the graph dissolves into it.  The cut is also the UNDO: capture marks of the abandoned suffix are orphaned with their memory, for free.
 *   5. SEQUENCE IS NOTHING.  Concatenation is emission order; failure inside it is the stack's business (SPITBOL manual Ch.18 step 6), never the sequence's.  A sequence box
 *      emits zero instructions — it is pure wiring.
 *   6. IT IS THE MANUAL'S OWN MACHINE.  SPITBOL Ch.18 p.204: "a pushdown stack is used to remember backtracking possibilities"; step 3 pushes {alternative, cursor}; step 6 pops
 *      on failure; empty + &ANCHOR=0 advances the start.  The choice cell IS that stack entry, the BASE cell IS the unanchored retry, implemented natively — WAM-flavored FORTH.
 * Registers: r13=Σ subject base · r14=δ cursor (r14d live) · r15=Δ length · rbp=CP · rsp=ζ frontier · r12=MH (from CELL-5).
 *
 * THIS FILE EXECUTES:   SUBJ = 'abhello' ;  SUBJ ? ( 'x' | 'he' ) 'llo'   (unanchored).  Trace: δ=0 BASE pushed; ALT pushes choice; 'x' fails→stub pops CHOICE (δ restored, arm2);
 * 'he' fails→stub pops BASE→advance δ=1 … δ=2: arm2 'he' matches (δ→4); SEQ is the absence between boxes; 'llo' matches (δ→7); scanhit walks the CP chain to TAG==BASE, cuts,
 * consumes — the winning start pops out of the BASE cell itself.  Measured costs: ALT=7 instr total, merge=0, SEQ=0, universal ω=6 shared, retry=4. */
    .intel_syntax noprefix
    .globl _start
    .text
_start:
    lea   r13, [rip + subj]           # bracket HEAD: Σ/δ/Δ in
    xor   r14d, r14d                  #   δ = 0
    mov   r15d, 7                     #   Δ = len('abhello')
                                      #   (real HEAD also saves caller rbp + swaps prior Σ/δ/Δ — omitted, _start owns the machine)
attempt:                              # ── BASE-cell (re)push: {resume=base_resume, δ=start, tag=1} — 8 instr, the whole retry engine
    xor   rax, rax
    push  rax                         #   [+24] MH = 0 (pre-CELL-5)
    push  rbp                         #   [+16] prev_CP
    push  r14                         #   [+8]  saved δ  (= attempt start)
    mov   dword ptr [rsp + 4], 1      #        TAG = BASE
    lea   rax, [rip + base_resume]
    push  rax                         #   [+0]  resume
    mov   rbp, rsp                    #   CP = this cell
                                      # ── pattern α — fallthrough, no jmp needed
n2_alt_a:                             # ══ ALT('x' | 'he') — ENTIRE box = one cell push; no quads, no stubs, no merge code
    xor   rax, rax
    push  rax
    push  rbp
    push  r14                         #   TAG=0 (CHOICE) — no tag store needed
    lea   rax, [rip + n2_alt_arm2]
    push  rax
    mov   rbp, rsp
                                      #   fall into arm1
n3_lit_x_a:                           # ══ LIT 'x' — K=0 (no carve); bounds + 1-byte compare
    mov   eax, r14d
    cmp   eax, r15d                   #   δ < Δ ?
    jae   cellfail                    #   ω = THE stub. always. every box.
    cmp   byte ptr [r13 + rax], 120   #   'x'
    jne   cellfail
    inc   r14d
    jmp   n2_alt_merge                #   arm γ → merge (label only — merge emits NOTHING)
n2_alt_arm2:                          # ── β-delivery: cellfail already restored δ and consumed the cell; rsp = ALT locals base (K=0); CP = BASE
n4_lit_he_a:                          # ══ LIT 'he'
    mov   eax, r14d
    add   eax, 2
    cmp   eax, r15d                   #   δ+2 ≤ Δ ?
    ja    cellfail
    mov   ecx, r14d
    cmp   byte ptr [r13 + rcx], 104       # 'h'
    jne   cellfail
    cmp   byte ptr [r13 + rcx + 1], 101   # 'e'
    jne   cellfail
    add   r14d, 2
n2_alt_merge:                         # ══ ALT γ — zero instructions. depth here DIFFERS by path (arm1: choice live below; arm2: consumed) AND NOBODY CARES.
n5_lit_llo_a:                         # ══ SEQ = PURE WIRING: 'llo' begins at the very next byte of .text. That absence IS the sequence box.
    mov   eax, r14d
    add   eax, 3
    cmp   eax, r15d
    ja    cellfail
    mov   ecx, r14d
    cmp   byte ptr [r13 + rcx], 108       # 'l'
    jne   cellfail
    cmp   byte ptr [r13 + rcx + 1], 108   # 'l'
    jne   cellfail
    cmp   byte ptr [r13 + rcx + 2], 111   # 'o'
    jne   cellfail
    add   r14d, 3
    jmp   scanhit
cellfail:                             # ══ THE UNIVERSAL ω — 6 instructions, correct from ARBITRARY depth. This replaces op_flat_disp,
    mov   rsp, rbp                    #    fc_geom, scanbase, the parked anchors, and the rbp floor. Control and depth travel together.
    pop   rax                         #    resume
    pop   r14                         #    δ restored (high32 carries TAG; first 32-bit op cleans it)
    pop   rbp                         #    CP unlink
    add   rsp, 8                      #    MH slot (pre-CELL-5 discard)
    jmp   rax
base_resume:                          # ── BASE cell's resume = Ch.18 step 6, &ANCHOR=0 arm: advance start, bound, re-enter.
                                      #    (&ANCHOR≠0 would `jmp scan_nomatch` here — runtime keyword test, one cmp, at this line.)
    cmp   r14d, r15d
    jae   scan_nomatch                #    subject exhausted
    inc   r14d                        #    start+1  (also zeroes the TAG bits riding r14 high — free)
    jmp   attempt                     #    re-push BASE at new start; rsp already at pristine depth BY THE POPS — no floor mov
scanhit:                              # ══ whole-match γ: walk CP chain to BASE (marks/commit-walk arrive at CELL-5), cut, consume.
find_base:
    cmp   dword ptr [rbp + 12], 1     #    TAG == BASE ?
    je    got_base
    mov   rbp, [rbp + 16]             #    chain prev (live pending choices above BASE die in the cut — free-undo)
    jmp   find_base
got_base:
    mov   rsp, rbp                    #    the cut
    pop   rax                         #    consume BASE: resume (discard)
    pop   rcx                         #    cl = winning start δ — the head-slot write-back value, delivered BY the cell
    pop   rbp                         #    caller rbp restored — bracket exit balanced by construction
    add   rsp, 8
    add   cl, 48                      #    '0'+start
    mov   byte ptr [rip + msg_s], cl
    mov   eax, r14d
    add   al, 48                      #    '0'+end
    mov   byte ptr [rip + msg_e], al
    mov   eax, 1
    mov   edi, 1
    lea   rsi, [rip + msg]
    mov   edx, OFFSET msg_len
    syscall
    xor   edi, edi
    jmp   do_exit
scan_nomatch:
    mov   eax, 1
    mov   edi, 1
    lea   rsi, [rip + nomsg]
    mov   edx, OFFSET nomsg_len
    syscall
    mov   edi, 1
do_exit:
    mov   eax, 60
    syscall
    .data
subj:   .ascii "abhello"              # flip to "abhexlo" to watch the exhaust path take scan_nomatch
msg:    .ascii "CELL MATCH start="
msg_s:  .byte  63
        .ascii " end="
msg_e:  .byte  63
        .byte  10
    .set msg_len, . - msg
nomsg:  .ascii "CELL NOMATCH\n"
    .set nomsg_len, . - nomsg
