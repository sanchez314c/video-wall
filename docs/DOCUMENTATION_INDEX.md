# VideoWall — Documentation Index

Comprehensive index of all VideoWall documentation. Last updated: 2026-04-17.

---

## Root-Level Documents

| File | Purpose |
|---|---|
| [README.md](../README.md) | Project overview, features, quick start |
| [CHANGELOG.md](../CHANGELOG.md) | Version history (canonical) |
| [LICENSE](../LICENSE) | MIT license |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Contribution guidelines |
| [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | Community guidelines |
| [SECURITY.md](../SECURITY.md) | Security policy + vuln reporting |
| [AGENTS.md](../AGENTS.md) | AI assistant guide (multi-tool: Claude, Copilot) |
| [CLAUDE.md](../CLAUDE.md) | Claude Code project-specific guidance |

## docs/ — Full Documentation

### Product / Specification
| File | Purpose |
|---|---|
| [PRD.md](PRD.md) | Product Requirements Document — current state |
| [TECHSTACK.md](TECHSTACK.md) | Tech stack inventory and versions |
| [TODO.md](TODO.md) | Roadmap, open tasks |
| [LEARNINGS.md](LEARNINGS.md) | Project insights, lessons learned |

### Architecture / Engineering
| File | Purpose |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture, component breakdown, data flow |
| [API-DOCS.md](API-DOCS.md) | Internal Python module API reference |
| [CHANGELOG.md](CHANGELOG.md) | Version history (mirror of root) |

### Setup / Operations
| File | Purpose |
|---|---|
| [QUICK_START.md](QUICK_START.md) | Fastest path to running the app |
| [INSTALL.md](INSTALL.md) | Full setup (Linux, macOS, Conda) + env vars + CLI args |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Dev environment setup, testing workflow |
| [BUILD_COMPILE.md](BUILD_COMPILE.md) | PyInstaller build process, all platforms |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Distribution: binaries, installers, system integration |
| [STREAMS_CONFIGURATION.md](STREAMS_CONFIGURATION.md) | M3U8 playlist format, stream sources |

### Workflow / Community
| File | Purpose |
|---|---|
| [WORKFLOW.md](WORKFLOW.md) | Dev workflow, branching, releases |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines (mirror) |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community guidelines (mirror) |
| [SECURITY.md](SECURITY.md) | Security policy (mirror) |

### Support
| File | Purpose |
|---|---|
| [FAQ.md](FAQ.md) | Frequently asked questions |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and fixes |

### Metadata
| File | Purpose |
|---|---|
| [PROJECT_MANIFEST.json](PROJECT_MANIFEST.json) | Machine-readable project metadata |

---

## Reading Path

**New User**:
1. [README.md](../README.md) — what this is
2. [INSTALL.md](INSTALL.md) — get it installed
3. [QUICK_START.md](QUICK_START.md) — first run
4. [STREAMS_CONFIGURATION.md](STREAMS_CONFIGURATION.md) — add your streams
5. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) / [FAQ.md](FAQ.md) — when stuck

**Developer / Contributor**:
1. [ARCHITECTURE.md](ARCHITECTURE.md) — system understanding
2. [API-DOCS.md](API-DOCS.md) — module interfaces
3. [DEVELOPMENT.md](DEVELOPMENT.md) — dev setup
4. [WORKFLOW.md](WORKFLOW.md) — process
5. [CONTRIBUTING.md](../CONTRIBUTING.md) — pull request guidelines

**Building / Releasing**:
1. [BUILD_COMPILE.md](BUILD_COMPILE.md) — build instructions
2. [DEPLOYMENT.md](DEPLOYMENT.md) — distribution
3. [CHANGELOG.md](../CHANGELOG.md) — what changed

**Project Lead / Reviewer**:
1. [PRD.md](PRD.md) — what we're building
2. [TODO.md](TODO.md) — what's left
3. [LEARNINGS.md](LEARNINGS.md) — what we learned
4. [TECHSTACK.md](TECHSTACK.md) — what we use

---

## Documentation Standards

- All paths are relative
- Each document has a single owner section in this index
- Mirrored docs (CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, CHANGELOG) live both at root (canonical) and in `docs/` (for browse-via-index ergonomics)
- Updates to root-level docs propagate to docs/ mirrors via the pipeline
