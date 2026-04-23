# About ProofMark Studio

ProofMark Studio is a working hub for proofing, converting, signing, and transforming PDFs. It composes independent sibling apps behind a single catalog UI, so every tool keeps its own repo, test suite, and release cadence while the hub stays thin.

## What ships today

- A React catalog of 49 tool tiles across Organize, Convert, Edit, Sign, Proof, AI, and Workflow groups.
- Per-tile feature flags (`TOOL_<SLUG>_ENABLED=false`) that demote a live tile to a paused stub in under a minute — no redeploy required.
- A structured `/api/tools` contract that the React catalog reads at runtime, so the UI can never drift from the registry.

## Philosophy

- **Composition over monolith.** ProofMark PDF, Text Inspection, and future siblings are independent FastAPI processes; the hub routes and redirects, nothing more.
- **Small verifiable steps.** Every phase has a failing test first, a promotion commit, and a tag when the exit gate is met.
- **Observability over cleverness.** Every decision point logs `[tag] message` so silent failures have nowhere to hide.

See the [changelog](/changelog) for what shipped most recently, or jump straight to the [tool catalog](/#tools).
