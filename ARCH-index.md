# ARCH-index.md — Full ARCH Catalog

All deep reference docs. Open on demand — never speculatively.

## By Topic

### Shared Architecture
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-overview.md` | Byrd box α/β/γ/ω, shared IR, calling conventions | Fundamental design questions |
| `ARCH-decisions.md` | Design decisions log (append-only) | Why was X decided? |
| `ARCH-sil-heritage.md` | SIL `xxxTYP` lineage for all E_ IR node names | Where did E_VART, E_QLIT etc come from? |

### SNOBOL4 Frontend
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-sno2c.md` | sno2c compiler: parser, IR lowering, emit | sno2c internals |
| `ARCH-snobol4-beauty.md` | beauty.sno two-stack engine, TDD protocol, bug history | beauty sprint deep work |
| `ARCH-snobol4-beauty-testing.md` | beauty.sno 19-subsystem testing plan, milestone map, driver format | beauty testing protocol |

### Icon Frontend
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-icon-jcon.md` | JCON + icon-master analysis; four-port templates | Icon emitter design, rung36 |
| `ARCH-icon-jvm-history.md` | Icon×JVM milestone history IJ-1..56 | Reviewing completed IJ work |

### Prolog Frontend
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-prolog-x64.md` | Prolog×x64 historical notes F-212..F-214 | Early Prolog design decisions |
| `ARCH-prolog-jvm-history.md` | Prolog×JVM milestone history PJ-1..78 | Reviewing completed PJ work |
| `ARCH-prolog-jvm.md` | JVM Prolog runtime: term encoding, trail, clause dispatch | PJ emitter design |

### x64 Backend
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-x64.md` | Technique 2 sprint plan; M-X64-FULL | x64 deep implementation |
| `ARCH-backend-c-dead.md` | C backend (dead) | Historical only |

### Testing & Infrastructure
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-testing.md` | Four-paradigm TDD protocol | Setting up tests |
| `ARCH-harness.md` | snobol4harness double-trace monitor | Monitor/trace debugging |
| `ARCH-corpus.md` | snobol4corpus structure, rung ladder | Corpus questions |
| `ARCH-monitor.md` | Five-way sync-step monitor | Monitor implementation |

### Project-Level
| Doc | Contents | Open when |
|-----|----------|-----------|
| `ARCH-scrip-vision.md` | Scrip platform executive vision | Strategic/product questions |
| `ARCH-grids.md` | Comparison tables | Benchmarks/positioning |
| `ARCH-status.md` | Test baselines across all repos | Cross-repo status snapshot |
