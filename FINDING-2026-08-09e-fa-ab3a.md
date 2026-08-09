# FINDING — 2026-08-09e session (fA + AB-3a)

## 1. bc_chase LAST-HOP-WINS clobbers port tags → fB is a DEAD ARM at HEAD
`optimizer/branch_chain.c:30` — each threaded hop does `memcpy(sz, node->γ.sz, 4)`; a chain `X(β)→fJ(α)→fT` arrives at the emitter as `sz=α`.  MEASURED: SCRIP_OPT_TRACE on w_fa showed the minted fA pointers rewritten with `sz=α`; the tag applied by `lc_γ_tag_β` never reached any consumer (route-side counter: ZERO hits).  IMPLICATION: fB (match-exhaust, tag-only, "landed" with BY-SET-identical gates) is by the same mechanism byte-inert — BY-SET gates pass equally when an arm is dead; a positive control (armed-vs-unarmed byte delta on a definitive witness) is the only discriminator, per the ACCEPTANCE INVERSION law.  fA sidesteps by SINGLE-HOP redirect to the OWN sbeg.  bc_chase left unfixed deliberately; the correct semantics is the emit-chase's sticky-OR accumulation (emit.cpp:2516-2517) and belongs to the fB-lighting rung.

## 2. RPO collector never followed STATEMENT_BEGIN.ω (the 175 fossil's true home)
DRIVE_PAIR emits `β: jmp ω`, but the collection walk (RPO_PUSH_SUCCS) had no ω-push for IR_STATEMENT_BEGIN — a fail-target statement reachable ONLY via sbeg.ω was never collected and the wired label resolved to the `main_ω` fallback.  MEASURED on wl_1.sno: 6 begins pristine vs 5 armed; GT-statement failure exited silently (rc=1, zero bytes, both modes).  Fixed at the collector (`7f01817f`); byte-inert on pristine shapes (targets already γ-reachable → RPO_VISITED skip).

## 3. Membership oin suppressed the statement-exit residual for β-into-own-sbeg edges
`ot ∈ run` set oin=1 (intra) for the new own-sbeg landing class, suppressing the exit residual: MEASURED 16B/failure leak, 500k-failure witness dies at default stack, pristine passes.  Exemption conjunct `!(port_sz_beta(ω.sz) && beta_is_stmt_land(ot))` at both membership arms restores it; the deep witness then passes both modes at 4MB (release arithmetic balanced end-to-end).  OPEN: a `:F(SELF)` self-loop lands the own sbeg **α** (no β tag) and takes the same membership suppression — possibly a PRE-EXISTING leak class; probe candidate.

## 4. <FN>_act_γ undefined — every DEFINE-bearing m4 program failed to LINK at HEAD
The activation block's `x86_gamma()` references the fname-derived γ label; nothing defined it.  ld: undefined reference, exit 1 — rc=1 with zero output through any harness that swallows stderr.  Pristine denominator identical (pre-existing since AB-1/AB-2 era).  Invisible to the matrix (no matrix probe carried a DEFINE until X12's shape) and to the AB gates as run.  Fixed (`1c497d65`): `x86_deflabel(X86P_GAMMA)` twin beside the ω define.  X12 goes GREEN in m4 (watermark 143/7 → 144/6).  Likely the "rc=1 root cause" that made ab_board_sweep.sh (`a19a0258`) unsound — RE-VERIFY the board at AB-3b.

## 5. Encoder trap: bare 3-arg string operands are SILENTLY SWALLOWED
`x86("lea","rax",<std::string label>)` emitted NOTHING (no bomb, no bytes) — measured: both leas vanished from the .s, r11 stayed garbage, wild store, segv.  The sanctioned named-symbol spelling is the 5-arg `[rip + __]` / `[rip@got + __]` template form (name arg patches BINARY through the emit-label table, forward refs included).

## 6. IR_LIT is a UNION — sval clobbers ival
Role flags cannot ride ival beside sval.  MEASURED: the ival==2 guard sank every bind into drive_unowned FATAL.  Discriminator moved to structure (n_operands==0 = bind; ≥1 = block, fname operand always present).
