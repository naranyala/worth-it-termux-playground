# TODOS

A working plan for turning this repository from a single long readme into a maintained,
runnable playground — while keeping the voice and honesty of the current text.

Status legend: `[ ]` todo · `[~]` in progress · `[x]` done · `[-]` dropped (with reason)

Last updated: 2026-11-16

---

## 0. Ground rules

These rules apply to every task below.

- **Verify before asserting.** Any claim about a package, a flag, or a path must be checked against upstream sources
  (Pi docs, Termux package `build.sh` files, Termux wiki) before it is written into the docs. Record the
  verification in the PR description or a note in the task.
- **No orphan links.** Every URL added or changed must resolve. The link checker in WS4 is the gate.
- **Voice.** Keep the existing tone: calm, concrete, honest about limits, no hype, no "amazing", no emoji
  beyond the existing `★` marker.
- **Phone-first.** Every example must be runnable on a phone: no root, `127.0.0.1` unless LAN is intended,
  `--dry-run` for destructive work, narrow-screen-friendly output.
- **One task, one commit.** Group by workstream, not by file.
- **Do not silently delete content.** If content is consolidated or dropped, note it in `docs/changelog.md`
  and keep the wording reachable from the new location so external links and muscle memory still work.

### Verified facts (as of 2026-11-16) — re-verify before editing

| Fact | Source | Note |
| --- | --- | --- |
| Pi docs live under `packages/coding-agent/docs/`, not `docs/` | `GET api.github.com/repos/earendil-works/pi/contents/packages/coding-agent/docs` | Root `docs/` path returns 404 |
| Pi Termux guide path | `packages/coding-agent/docs/termux.md` | Use this, not `docs/termux.md` |
| Pi requires Node.js ≥ 22.19 | Pi repository README | Check with `node -v` on device |
| Termux `nodejs` = 26.13.1 and **no longer bundles npm** | `termux-packages/packages/nodejs/build.sh` (`preinst`: "npm is no longer bundled", since v25.3.0-1) | `npm` arrives only via `TERMUX_PKG_RECOMMENDS` |
| Pi has **no built-in permission system** | Pi repository README, "Permissions & Containerization" | Everything runs with Termux permissions by default |
| `codemode` and `tool_search` are **off by default** | `packages/coding-agent/docs/cli.md` | Enable with `--tools +codemode` or `defaultTools` in `~/.pi/agent/settings.json` |
| Pi CLI flags in use | `packages/coding-agent/docs/cli.md` | `--print`, `--mode json\|rpc\|text`, `--continue`, `--resume`, `--tools`, `--exclude-tools`, `--approve`, `--no-approve`, `--offline`, `--export`, `--model`, `--thinking`, `--api-key` |
| Pi update / package commands | `packages/coding-agent/docs/cli.md` | `pi update`, `pi update --extensions`, `pi install npm:@scope/package`, `pi list`, `pi config`, `pi auth login` |
| Project trust gating | `packages/coding-agent/docs/cli.md`, `security.md` | `-a/--approve`, `-na/--no-approve`; project `.pi/mcp.json` only read for trusted projects |
| Pi resource layout | `packages/coding-agent/docs/configuration.md`, upstream Termux guide | `~/.pi/agent/AGENTS.md`, `~/.pi/agent/settings.json`, `~/.pi/agent/mcp.json`, project `.pi/`, `AGENTS.md`/`CLAUDE.md` discovery |

---

## WS1 — Correctness fixes (Tier 1, low risk, do first)

Goal: remove statements that are wrong today. Target: < 1 hour, one commit.

- [x] **1.1 Fix the three broken Pi links.** `README.md` lines 95, 564, 565.
  - `https://github.com/earendil-works/pi/blob/main/docs/termux.md` →
    `https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/termux.md`
  - `https://github.com/earendil-works/pi/tree/main/docs` →
    `https://github.com/earendil-works/pi/tree/main/packages/coding-agent/docs`
  - Prefer `https://pi.dev/docs/latest` as the canonical entry point; keep the GitHub paths as deep links.
- [x] **1.2 Fix the Node/npm install steps.** `README.md` §"Install it".
  - `pkg install nodejs git` → `pkg install nodejs npm git`
  - Add `node -v` and state the Pi minimum (Node ≥ 22.19) next to `pi --version`.
  - Note that `npm` is no longer bundled with Termux `nodejs` since v25.3.0-1, so it must be installed explicitly.
  - Keep `npm install -g --ignore-scripts @earendil-works/pi-coding-agent` (matches upstream) and mention the
    alternative `curl -fsSL https://pi.dev/install.sh | sh` installer, noting that the npm route does not pin
    transitive dependencies and the installer does.
- [x] **1.3 State that Pi has no built-in permission system.** In §"Security, privacy, and trust" and in
  §"What Pi cannot overcome on Android".
  - Phrase: tools run with the full permissions of the Termux process; approval gates are something you build
    (via extensions), not something Pi provides.
  - Cross-reference `packages/coding-agent/docs/security.md` and `containerization.md`.
- [x] **1.4 Document how to enable Codemode and `tool_search`.** In §"Extend Pi into a mobile development platform".
  - `pi --tools +codemode` for one run; `{"defaultTools": ["+codemode"]}` in `~/.pi/agent/settings.json` for all sessions.
  - Same one-liner treatment for `tool_search`.
- [x] **1.5 Correct the filesystem table.** `README.md` §"Understand the Termux filesystem".
  - Replace `.pi/` and `.agents/` with the real Pi paths: `~/.pi/agent/` (global) and project `.pi/`.
  - Add a row for `~/.pi/agent/settings.json` and `~/.pi/agent/mcp.json`.
  - Note that project-local `.pi/` resources are trust-gated (`--approve`).
- [x] **1.6 Add the missing Pi maintenance commands** to §"Deeper Termux explorations" → "Installation, updates, and recovery":
  - `pi update` (self-update), `pi update --extensions`, `pi list`, `pi install npm:@scope/package`, `pi config`.
  - Mention `pi --offline` for metered or unreliable connections.
- [x] **1.7 Add the project-trust concept.** Short subsection in §"Security, privacy, and trust":
  - `pi -a` / `--approve` trusts project-local config for one run; `-na` ignores it.
  - Project `.pi/mcp.json` and project resources are only read for trusted projects.
  - Practical consequence: do not run `pi` in an unfamiliar repository without `-na`.
- [x] **1.8 Verify every remaining external link** in `README.md` by hand once (F-Droid, GitHub releases, Termux wiki,
  Termux:API, PRoot Distro, Pi docs) before closing WS1. Verified: F-Droid package page, termux-app releases,
  termux-app wiki, termux-api, proot-distro, pi.dev, and the Pi docs deep links all resolve.

**Done when:** no 404s, no `npm` install ambiguity, no claim that Pi provides sandboxing it does not provide.

---

## WS2 — Structure, deduplication, and metadata (Tier 2)

- [x] **2.1 Decide the information architecture and write it down** in `README.md` as the new Contents list.

  Proposed layout:

  ```text
  README.md                    umbrella: what this is, quick start, catalog index, links
  docs/termux-basics.md        what Termux is, install, filesystem, packages, background execution
  docs/catalog.md              the 9-category playground catalog (moved out of README)
  docs/pi-on-termux.md         Pi install, modes, workflows, limits (moved out of README)
  docs/security.md             security/privacy/trust, shared by every tool in the repo
  docs/troubleshooting.md      symptom to first-checks table
  docs/changelog.md            what moved where, per release
  ```

  Keep `README.md` readable in under five minutes; it becomes an index, not the whole manual.
- [x] **2.2 Move sections without rewriting them.** Cut/paste first, improve second. Preserve headings so anchor
  links from outside the repo keep resolving via `docs/changelog.md` redirects table.
- [x] **2.3 Consolidate the duplicated constraint material into one table.**
  - Sources to merge: §"What is different from a desktop Linux distribution" (L43), §"What Pi cannot overcome on
    Android" (L198), §"Phone-first constraints" (L524), §"Safety and maintenance" (L535), §"Background execution and
    reliability" (L412).
  - Output: a single *Constraints* table with columns `Constraint | What Android enforces | What you do about it | Affects`.
  - Keep the prose that is genuinely non-duplicated; delete the rest.
- [x] **2.4 Improve the catalog tables.** Replace the `★ / offline / safe` legend with explicit columns:
  `Time | Difficulty | Needs network | Works offline | Notes` (or a compact `Time · Level · Offline` cell).
  Keep `★` for "especially good on a phone" only if it still earns its place.
- [x] **2.5 Add version and verification metadata.**
  - A short "Tested on" block: Termux version, Android version, device arch, date.
  - Per-section "Last verified" markers for anything version-sensitive (packages, Pi CLI, Android APIs).
- [x] **2.6 Add the missing topic coverage** (one concise subsection each):
  - Android 14/15 background-execution and vendor battery-manager reality.
  - `pkg` vs `apt` vs `pacman` vs `tur-repo` — which to use and when.
  - Mirrors and blocked networks: `termux-change-repo`, F-Droid mirrors, GitHub reachability.
  - `termux-api` app requirements (Android version) and what fails without it.
  - Energy and thermal cost as a first-class design constraint (measure with `termux-battery-status`).
- [x] **2.7 Update the "Further reading" list** with the corrected Pi paths and add: Pi `cli.md`, `sessions.md`,
  `security.md`, `mcp.md`, `extensions.md`, `codemode.md`; Termux `pkg` man page; Termux:API command list.

**Done when:** `README.md` is an index, no constraint is stated twice, and every version-sensitive claim carries a date.

---

## WS3 — Make it a playground (Tier 3, the actual differentiator)

Nothing in this repo is currently executable. That is the gap between "catalog" and "playground".

- [ ] **3.1 Publish the experiment schema as a template** — `templates/experiment/README.md`,
  `templates/experiment/bin/`, `templates/experiment/src/`, `templates/experiment/tests/`, `templates/experiment/.env.example`,
  matching the layout the README already recommends.
  - Required fields per experiment: goal, skill taught, time, difficulty, setup, usage, phone caveats, cleanup command,
  - safety notes, sample output.
- [ ] **3.2 Build 5 starters, each under ~150 lines and genuinely phone-appropriate.**
  1. `habit-tracker` — Python + SQLite, offline, `--brief` output.
  2. `rss-digest` — `curl` + XML parse + plain-text digest, scheduled with `termux-job-scheduler`.
  3. `battery-notify` — `termux-battery-status` + `termux-notification`, idempotent.
  4. `file-organizer` — dry-run by default, operates on `~/storage/downloads`, never deletes without `--apply`.
  5. `local-dashboard` — `python -m http.server` bound to `127.0.0.1`, battery/storage/uptime in one page.
  - Each starter: a README with the experiment metadata from 3.1, a `--help`, input validation, tests that run on a phone.
- [ ] **3.3 Build `scripts/bootstrap.sh`.** Idempotent installer for the base package set, with:
  - `--dry-run` and `--with-pi` / `--without-pi` flags, non-interactive, safe to re-run.
  - `scripts/snapshot-packages.sh` — writes `termux-packages.txt` and `termux-manual-packages.txt` (automates the
    manual instructions currently in the README).
  - `scripts/restore.sh` — documented restore path (currently missing from the repo, only described in prose).
- [ ] **3.4 Ship an `AGENTS.md` at the repo root** that describes *this* repository — build/test commands, the
  experiment schema, the voice rules, and the boundaries. Dogfood the pattern the docs recommend.
- [ ] **3.5 Add a `playground/INDEX.md`** listing every experiment with time, difficulty, and the skill it teaches,
  so the catalog has a single source of truth that both `README.md` and `playground/` link to.

**Done when:** a reader can clone, run one command, and have a working experiment on a real phone.

---

## WS4 — Automation and hygiene (keeps WS1–WS3 from rotting)

- [ ] **4.1 Add `LICENSE`** (MIT, matching the Pi project's licence and the tone of the repo).
- [ ] **4.2 Add `CONTRIBUTING.md`** built from the closing line of the README: description, skill taught, phone
  caveats, safe way to try it — plus the review checklist and the "one experiment per PR" rule.
- [ ] **4.3 Add link checking in CI.**
  - `lychee` over `README.md` and `docs/**` on a schedule (weekly) and on demand.
  - Deliberately allow `github.com/earendil-works/pi` deep links if upstream moves them again — better: pin the
    links to `pi.dev/docs/latest` and check the GitHub paths as a non-blocking job.
- [ ] **4.4 Add Markdown linting** (`markdownlint` with a config matching the existing style: ATX headings,
  fenced code blocks with language tags, one H1 per file).
- [ ] **4.5 Add a docs snippet checker.** Extract every fenced `sh`/`bash` block from the docs and run `bash -n`
  (syntax only) on it; block CI on syntax errors. Optionally run `shellcheck` at `info` severity.
- [ ] **4.6 Add an "upstream drift" job.** A scheduled job that re-checks the volatile facts listed in §0 and opens
  an issue (or a failing CI run) when Pi's CLI or Termux's Node packaging changes. This is the highest-value
  automation for a doc that tracks a fast-moving upstream.
- [ ] **4.7 Add a `.gitignore`** for `node_modules/`, `*.db`, `.env`, `termux-packages.txt`, and any local artifacts.
- [ ] **4.8 Pin external tools by version** and record the versions used in `docs/changelog.md`.

**Done when:** a broken link or a stale CLI flag fails CI instead of reaching a reader.

---

## WS5 — Polish and consistency

- [ ] **5.1 Terminology pass.** Fix the `.agents/` → `.pi/` leftover; use "phone" vs "device" consistently; use
  "Termux:API" (add-on app) vs `termux-api` (package) correctly everywhere.
- [ ] **5.2 Accessibility and readability.** Ensure tables are not the only carrier of meaning; check code blocks
  wrap sanely on a narrow screen; add a `plain`/`no-tables` friendly summary at the top of the catalog.
- [ ] **5.3 Localisation readiness.** Keep wording in short declarative sentences and avoid idioms; this makes a
  translated edition cheap later. Record the decision in `docs/changelog.md`.
- [ ] **5.4 Decide the repo's identity.** The repo is named `worth-it-termux-playground` but a quarter of the
  content is Pi-specific. Either (a) keep the name and make the Pi scope explicit in the tagline, or (b) rename and
  record the rename + redirects in `docs/changelog.md`.
- [ ] **5.5 Write a short "How this repo is maintained" section** — who updates it, how often, and what the
  contribution bar is. A doc with no maintenance policy silently rots.

---

## Execution order

```text
WS1  ──▶ WS2  ──▶ WS4.1/4.2/4.7 (minimal hygiene, early)
                │
                ├──▶ WS3.1 (template) ──▶ WS3.2 (starters) ──▶ WS3.5
                │                              └──▶ WS3.3 (bootstrap)
                └──▶ WS4.3–4.6 (CI) after docs/ exists
WS5 last, as a continuous pass
```

Rationale: correctness first (WS1) because it is the only work that fixes facts a reader can act on today;
structure next (WS2) so that later additions land in the right file; CI after structure, because the checks must
know the final layout; real code last (WS3), because building starters against a moving README wastes effort.

## Branching

One branch per workstream, PR per task group:

```text
ws1/correctness
ws2/restructure
ws3/playground
ws4/automation
```

WS2 depends on WS1 landing first. WS3 and WS4 can proceed in parallel once WS2 merges.

## Out of scope

- Publishing to a package registry or app store.
- Anything requiring root, a rooted device, or an Android SDK build on the phone.
- Android application development with Gradle/SDK on-device (documented as impractical; see README).
- Local model inference benchmarks (mentioned as an option in the docs; benchmarking belongs in a separate repo).

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Pi upstream moves again (it already did once) | Stale links and flags | Prefer `pi.dev/docs/latest`; WS4.6 drift job; pin nothing that upstream owns |
| Termux package set changes without notice | Install instructions fail | State the tested Termux version; `pkg` failures are usually a missing package, not a broken doc |
| Splitting the README breaks external links | Lost readers / bad citations | Keep a redirect table in `docs/changelog.md`; announce the split; keep the umbrella README complete enough to stand alone |
| The repo becomes a code project and loses its voice | Identity drift | AGENTS.md carries the voice rules; WS5.4 settles scope explicitly |
| Scope creep into "Termux admin guide" | Unbounded maintenance | Out-of-scope list above; link to upstream wikis instead of restating them |

## Definition of done

- [ ] All WS1 tasks closed; every factual claim re-verified against upstream.
- [ ] `README.md` is an index under ~150 lines with a clear path into `docs/`.
- [ ] No constraint, warning, or instruction is stated in two places.
- [ ] Five runnable starters, each verified on a real phone, each with a README and tests.
- [ ] `scripts/bootstrap.sh` runs idempotently and non-interactively on a fresh Termux install.
- [ ] CI: link check, markdown lint, shell syntax check, upstream drift check — all green.
- [ ] `LICENSE`, `CONTRIBUTING.md`, `AGENTS.md`, `.gitignore` present.
- [ ] `docs/changelog.md` records every move, rename, and dropped item.
- [ ] A reader who clones the repo and follows the README top to bottom never hits a broken link, a missing package,
  or an instruction that cannot work on an unrooted phone.
