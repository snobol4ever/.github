# ARCH-index.md — Full ARCH Catalog

All deep reference docs. Open on demand — never speculatively.
Each entry: what's in it, when you need it.

---

## By Topic

### Shared Architecture
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-overview.md` | Byrd box α/β/γ/ω model, shared IR, calling conventions | Fundamental design questions |
| `ARCH-decisions.md` | Design decisions log (append-only) | Why was X decided? |

### SNOBOL4 Frontend
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-sno2c.md` | sno2c compiler: parser, IR lowering, emit pipeline | sno2c internals |
| `ARCH-snobol4-beauty.md` | beauty.sno two-stack engine, TDD protocol, bug history | beauty sprint deep work |

### Icon Frontend
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-icon-jcon.md` | JCON + icon-master deep analysis; four-port templates | Icon emitter design, rung36 oracle |
| `ARCH-icon-jvm.md` | Icon×JVM milestone history, session findings IJ-32..56 | Reviewing completed IJ work |

### Prolog Frontend
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-prolog-x64.md` | Prolog×x64 historical session notes (F-212..F-214) | Early Prolog design decisions |
| `ARCH-prolog-jvm.md` | Prolog×JVM milestone history (PJ-1..77) | Reviewing completed PJ work |
| `ARCH-jvm-prolog.md` | JVM Prolog runtime: term encoding, trail, clause dispatch | PJ emitter design |

### x64 Backend
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-x64.md` | Technique 2 (mmap+relocate) sprint plan; M-X64-FULL plan | x64 deep implementation work |
| `ARCH-backend-c-dead.md` | C backend (dead) — archived for reference | Historical only |

### JVM Backend
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-jvm-prolog.md` | JVM Prolog runtime design (shared with Prolog Frontend above) | JVM term/trail design |

### Testing & Infrastructure
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-testing.md` | Four-paradigm TDD protocol, crosscheck harness | Setting up tests |
| `ARCH-harness.md` | snobol4harness double-trace monitor | Monitor/trace debugging |
| `ARCH-corpus.md` | snobol4corpus structure, rung ladder | Corpus questions |
| `ARCH-monitor.md` | Five-way sync-step monitor | Monitor implementation |

### Project-Level
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-scrip-vision.md` | Scrip platform executive vision | Strategic/product questions |
| `ARCH-grids.md` | Comparison tables (placeholder numbers) | Benchmark/positioning |
| `ARCH-status.md` | Test baselines across all repos | Cross-repo status snapshot |

