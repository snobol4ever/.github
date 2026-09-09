# The tracer #GP is a compensating pad that OUTLIVED the push it compensated for — and behind it, a second, independent defect

**Measured 2026-09-09 by hq_U** · SCRIP `2197495bc` · corpus `29ac0f24a` · `RT_OPT=-O0` · incremental `make` · oracle `icont`/`iconx` v9.5.25a · all runs `setarch -R`.
**Row** CEO-452(a), the tracer #GP, routed to hq_U on hq_B's FINDING (`.github 936228e1`, re-measured by hq_B at `367b083e`). **DIAGNOSIS ONLY — NO CURE LANDED. Tree clean, binaries byte-identical to origin's.**

## The witness, reduced to seven lines

```icon
procedure main();
    &trace := -1;
    every write(g(1));
end
procedure g(x);
    suspend x;
end
```

SIGSEGV rc=139 in **both modes**, stderr stopping mid-argument at `| g(`. `iconx` prints five trace lines and exits 0.

## ⛔ DEFECT ONE: AN ABI VIOLATION, MEASURED AT THE CALL INSTRUCTION

hq_B's and hq_V's narrowing was *generator AND argument together*. **Measured, that is not a conjunction of two causes.** Breaking on `rt_trace_event_args`:

| witness | shape | rsp%16 | result |
|---|---|---|---|
| non-generator + argument | `return x` | **0** | passes |
| generator + NO argument | `suspend 1` | **8** | **passes anyway** |
| generator + argument | `suspend x` | **8** | SIGSEGV |

⭐ **The generator path is misaligned whether or not there is an argument.** The argument is not a cause — it is what makes the misalignment *reachable*: with an argument, `trace_print_icon` calls `image` → `snprintf` → `__vsnprintf_internal`'s `movaps %xmm0,-0xc0(%rbp)`, and an SSE store on an 8-mod-16 frame faults. **`tgn` is a latent crash that happens to survive**, and any traced generator whose trace print reaches SSE code will hit it.

Proven at the instruction itself, not inferred — breaking on the `call` in the mode-4 binary:

```
non-generator path:  call rt_proc_call_open_det   rsp%16 = 0   (ABI requires 0)
generator path:      call rt_proc_call_open_det   rsp%16 = 8   (ABI VIOLATION)
```

### Where the 8 bytes come from, and why this is the interesting part

`bb_call_proc_staged.cpp`, two adjacent pads:

- **line 692, N-2 ABI WORD** (`IF(icn_gen_regime(), sub rsp,8)`, hq_I root-caused / hq_B authored) — its own note states its reason: *"the REGION HAND-OFF push below is a LONE 8B word and therefore PARITY-FLIPPING."*
- **line 693, PL-CALL-ALIGN** (unconditional `sub rsp,8` + `lea` + `push`) — added for a Prolog witness, and its note describes **this exact failure**: *"one bare 8B push here left rsp 8-mod-16 into rt_proc_call_open_det … a real ABI violation (SIGSEGV in a later vsnprintf movaps)."*

At the call the generator path has pushed **8 + 8 + 8 = 24**, i.e. 8 mod 16; the non-generator path has pushed **8 + 8 = 16**, i.e. 0.

⛔⭐ **And the reason is the thing worth carrying: line 704 (N-3, ceo 2026-09-07) REMOVED the region hand-off push** — *"no region is handed over — the callee carves its own frame below the entry words at its alpha"* — and put its replacement word **after** the call. **So N-2 is still compensating for a push that no longer happens before the call.** The compensating pad outlived the thing it compensated for. N-3's note says it keeps *"the parity … exactly as before"*, and that is true of the callee's **entry layout** and false of the **call-site alignment**, because the word moved to the other side of the `call`.

**Candidate cure, measured, NOT landed:** disabling the N-2 pad restores `rsp%16 = 0` at the call and all three witnesses exit 0. ⛔ It is **not** a one-line removal: N-2's own note records that dropping the word moves the caller's pre-pad `rsp0` from `[rsp+48]` to `[rsp+40]`, which needs matching constants in the alpha's ANCHOR `lea` and the beta re-creation. Landing it without those is how a green witness set hides a wrong frame.

## ⛔ DEFECT TWO, INDEPENDENT, AND ONLY VISIBLE BECAUSE hq_B TOLD ME NOT TO TRUST THE RUNG

hq_B warned that `ladder__rung03_…` (`procedure_write_265`) is red **only** through rc=139, and that `lib_ladder.sh` runs with `2>/dev/null` while Icon `&trace` writes only to stderr — so the moment the crash stops the rung goes GREEN regardless of whether the trace text is right. **That warning paid for itself immediately.** On the measurement build the crash is gone and the trace is still wrong:

| | `iconx` | SCRIP |
|---|---|---|
| `\| g(1)` | ✓ | ✓ |
| `\| g suspended 1` | ✓ | **missing** |
| `\| g resumed` | ✓ | **missing** |
| `\| g failed` | ✓ | **missing** |
| `main failed` | ✓ | ✓ |

⭐ **This is a second defect and it is not caused by the alignment.** The control proves it: `tgn` (generator, no argument) **never crashed**, and on the **unmodified** build it prints the same 2 of 5 lines. So the generator's `suspended` / `resumed` / `failed` trace events are simply never emitted — a defect that has been sitting behind the crash, and that curing the crash would have appeared to fix.

⛔ **Had I graded by the rung, I would have reported a cure and shipped a still-broken tracer.**

## NOT CLAIMED

- **No cure landed.** Tree clean at `2197495bc`; both binaries byte-identical to origin's after the measurement build was reverted.
- The N-2 removal is a **measurement**, not a proposal: the ANCHOR/beta constants were **not** adjusted, and the three witnesses passing does not prove the frame is right — that is exactly the shape N-2's own note warns about.
- **Defect two is not diagnosed at all** — only isolated and shown independent. I have not looked at where the suspend/resume/fail events should be emitted.
- I did **not** re-run the Icon master or Prolog boards: nothing landed. A cure here touches `bb_call_proc_staged.cpp`, which is shared with the Prolog call path (the PL-CALL-ALIGN pad is Prolog's), so it owes the Prolog ladder as a control arm.
- ⚠️ **CEO-447 tells hq_U to hold frame code until the cto's tier cut lands.** This is call-frame anchor arithmetic in the shared staged-call box, and N-2 is hq_B's while N-3 is the ceo's — so the cure wants coordination, not a unilateral edit mid-cut. That is why this is filed rather than built.
