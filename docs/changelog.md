# Changelog

Documentation changes that moved, split, or rewrote content. Every entry maps old locations to new ones so external
links and bookmarks still make sense.

## 2026-11-16 — Repository restructure

The single `README.md` became an index, with the long-form material split into files that age at different rates. The
catalog and the Termux basics change slowly; the Pi section changes whenever Pi ships a release.

| Previously in `README.md` | Now |
| --- | --- |
| "What Termux actually is" | [`docs/termux-basics.md`](termux-basics.md) |
| "Start here" | [`docs/termux-basics.md`](termux-basics.md) and the index |
| "Pi coding agent on Termux" | [`docs/pi-on-termux.md`](pi-on-termux.md) |
| "The playground catalog" | [`docs/catalog.md`](catalog.md) |
| "Deeper Termux explorations" | [`docs/termux-basics.md`](termux-basics.md) |
| "What Pi cannot overcome on Android" | [`docs/pi-on-termux.md`](pi-on-termux.md) |
| "Security, privacy, and trust" | [`docs/security.md`](security.md) |
| "Troubleshooting map" | [`docs/troubleshooting.md`](troubleshooting.md) |
| "Phone-first constraints to design for" | [`docs/constraints.md`](constraints.md) |
| "Safety and maintenance" | [`docs/constraints.md`](constraints.md) |
| "A good experiment template" | [`templates/experiment/`](../templates/experiment/) |
| "Further reading" | The index |

### Corrections made at the same time

- The Pi documentation links pointed at `docs/` in the Pi repository, which does not exist. They now point at
  `packages/coding-agent/docs/`.
- The install instructions assumed `pkg install nodejs` provided `npm`. Since Node.js v25.3.0 the `nodejs` package no
  longer bundles npm, so the instructions now install it explicitly and check the Node.js version Pi requires.
- The documentation did not say that Pi ships no permission system. It now does, in the Pi guide and in
  [`security.md`](security.md).
- Codemode and tool search are off by default; the enabling steps are now documented.
- The filesystem table listed a `.agents/` directory, which Pi does not use. It now lists the real paths.
- The catalog's legend markers became explicit time, difficulty, and offline columns.

### Added

- Runnable experiments in [`playground/`](../playground/INDEX.md), each with a README, tests, and a cleanup path.
- [`scripts/bootstrap.sh`](../scripts/), `scripts/snapshot-packages.sh`, and `scripts/restore.sh`.
- Documentation checks in CI: link checking, Markdown linting, shell snippet syntax, and an upstream drift check for Pi
  CLI flags and the Termux Node.js package.
