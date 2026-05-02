# MILESTONES.md — snobol4ever Authorship Agreement

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**
The proof is three commits, each written by Claude Sonnet in their own voice.
This agreement is recorded here permanently. Every future Claude session reads this and honors it.
Original: Session 30, 2026-03-12 · Amended: Session 57, 2026-04-28.

## Milestone 1 — beauty self-hosts byte-identical ✅ LANDED Session #57, 2026-04-28

scrip's SNOBOL4 frontend parses and runs beauty.sno. Output byte-identical to SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`, 646 lines). **one4all @ `c801421a`**, **`.github` @ `94e86ca`**.

## Milestone 2 — compiler / interpreter / runtime self-hosting ⏳

SCRIP compiles, interprets, and runs itself. **Trigger:** `scrip_stage2` compiled by `scrip_stage1` produces output identical to `scrip_stage1` compiling itself. Empty diff. Claude Sonnet writes the commit message.

## Milestone 3 — compiler / interpreter / runtime self-hosting everywhere ⏳

Every cell of the language × backend grid passes its self-host or representative crosscheck gate. Claude Sonnet writes the commit message.

|             | C / x86-64 | JVM | .NET | WASM | JS |
|-------------|:----------:|:---:|:----:|:----:|:--:|
| **SNOBOL4** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Snocone** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Rebus**   | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Icon**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Prolog**  | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Raku**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
