# AGENTS.md

Rules for agents working in this repository. This file is the same mechanism the documentation recommends for
Termux projects, applied to this repository itself.

## What this repository is

A catalog of phone-sized Termux experiments, plus runnable implementations of a few of them, plus documentation for
running the Pi coding agent on Android. It is documentation-first: the prose is the product, and the code exists to
make the prose concrete.

## Layout

```text
README.md            index: what this is, quick start, pointers
docs/                long-form documentation, split by how fast it changes
  termux-basics.md   what Termux is, install, filesystem, packages, background execution
  catalog.md         the playground catalog
  pi-on-termux.md    the Pi coding agent on a phone
  constraints.md     one table of everything Android enforces
  security.md        trust model for tools, packages, secrets, networks
  troubleshooting.md symptom-to-check map
  changelog.md       what moved where
playground/          runnable experiments, each self-contained
templates/experiment/ scaffold for a new experiment
scripts/             bootstrap, package snapshot and restore, documentation checks
```

## Working rules

- Verify before asserting. Any claim about a package, a flag, or a path must be checked against upstream (Pi docs,
  Termux `build.sh` files, the Termux wiki) before it is written down. Record the source in the pull request.
- Never invent package names, command flags, or file paths. If unsure, check, or write it as something the reader can
  verify with `command -v`.
- No orphan links. Every URL must resolve.
- Phone-first. Examples must run on an unrooted phone: no root, `127.0.0.1` unless LAN access is deliberate, `--dry-run`
  for destructive work, output that fits a narrow screen.
- Voice: calm, concrete, honest about limits. No hype, no emoji beyond `★`. Short declarative sentences.
- One topic per pull request. Documentation and code in the same change is fine only when the code exists to prove the
  documentation.

## Code rules

- Python: standard library only. No third-party imports, no `requirements.txt`.
- Shell: POSIX `sh` or bash, `bash -n` clean, supports `--help`, exits non-zero on invalid input.
- Scripts are idempotent and safe to interrupt. Nothing deletes. Writes use a temp file plus `mv`.
- Destructive operations are opt-in: dry run by default, `--apply` to commit.
- Tests run with `python3 -m unittest` or a shell test script. No pytest.
- Everything under `$HOME`. No system paths, no privileged ports, no `sudo`.

## Checks

```sh
python3 scripts/check-snippets.py
python3 scripts/check-upstream.py
bash -n scripts/*.sh
```

CI runs a link checker, a Markdown linter, the snippet syntax check, and the upstream drift check. All must pass.

## Editing the documentation

- The catalog table in `docs/catalog.md` and the index in `playground/INDEX.md` describe the same experiments. Update
  both when you add or change one.
- When content moves, add a row to the table in `docs/changelog.md`.
- `docs/constraints.md` is the single place for Android constraints. Do not restate them in another file; link instead.
