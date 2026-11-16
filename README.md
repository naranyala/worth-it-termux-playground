# Termux Playground

A catalog of Android experiments, tools, and tiny projects that are genuinely worth trying from a **terminal on a smartphone**.

Termux turns an Android device into a pocket-sized Linux environment: useful for learning, automation, local services,
scripting, networking, and creative tinkering—without root.

> **Guiding idea:** prefer experiments that are useful on a phone, finish in an afternoon, and teach a transferable skill.

## Contents

- [Start here](#start-here)
- [What this repository contains](#what-this-repository-contains)
- [The playground catalog](#the-playground-catalog)
- [Pi coding agent on Termux](#pi-coding-agent-on-termux)
- [Phone-first constraints](#phone-first-constraints)
- [Safety and maintenance](#safety-and-maintenance)
- [A good experiment template](#a-good-experiment-template)
- [Further reading](#further-reading)

## Start here

Install Termux from [F-Droid](https://f-droid.org/packages/com.termux/) or the official
[GitHub releases](https://github.com/termux/termux-app/releases). Avoid mixing APKs from different sources. Optional
companion apps such as **Termux:API**, **Termux:Widget**, and **Termux:Boot** should come from the same source.

```sh
pkg update && pkg upgrade
pkg install git curl wget nano vim tmux man termux-tools
termux-setup-storage
```

Useful first checks:

```sh
uname -a
termux-info
df -h
command -v termux-battery-status && termux-battery-status
```

The battery command is available after installing Termux:API; the conditional keeps the basic setup usable without it.

Or run the bootstrap script in this repository, which installs the same package set idempotently and supports a dry run:

```sh
git clone https://github.com/naranyala/worth-it-termux-playground.git
cd worth-it-termux-playground
bash scripts/bootstrap.sh --dry-run
bash scripts/bootstrap.sh
```

## What this repository contains

| Path | Purpose |
| --- | --- |
| [`docs/termux-basics.md`](docs/termux-basics.md) | What Termux is, installation, filesystem, packages, background execution, remote development |
| [`docs/catalog.md`](docs/catalog.md) | The full playground catalog, from shell tweaks to weekend projects |
| [`docs/pi-on-termux.md`](docs/pi-on-termux.md) | Running the Pi coding agent on a phone: install, modes, workflows, limits |
| [`docs/constraints.md`](docs/constraints.md) | One table of everything Android enforces, and what to do about it |
| [`docs/security.md`](docs/security.md) | Trust model for tools, extensions, packages, secrets, and networks |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Symptom-to-check map, including recovery from a broken installation |
| [`playground/INDEX.md`](playground/INDEX.md) | Runnable experiments you can clone and try today |
| [`templates/experiment/`](templates/experiment/) | The scaffold used to start a new experiment |
| [`scripts/`](scripts/) | Bootstrap, package snapshot, restore, and documentation checks |

The documentation is split into several files because each part ages at a different rate. The Termux basics and the
catalog change slowly; the Pi section changes whenever Pi ships a release. See
[`docs/changelog.md`](docs/changelog.md) for what moved where.

## The playground catalog

The full catalog, with time, difficulty, and offline notes for each experiment, lives in
[`docs/catalog.md`](docs/catalog.md). It is ordered from quick, phone-native experiments to larger systems. Most
entries are intentionally small: the goal is to learn by finishing, then extend the experiment with Pi or your own code.

Five of them are now implemented and tested in [`playground/`](playground/INDEX.md):

| Experiment | Skill taught | Time | Difficulty | Offline |
| --- | --- | --- | --- | --- |
| [habit-tracker](playground/habit-tracker/) | Python and SQLite on a phone | 30 min | Easy | Yes |
| [rss-digest](playground/rss-digest/) | Fetching and parsing feeds with the standard library | 45 min | Easy | Cached |
| [battery-notify](playground/battery-notify/) | Termux:API and scheduled jobs | 30 min | Easy | Yes |
| [file-organizer](playground/file-organizer/) | Safe bulk file operations with a dry run | 45 min | Medium | Yes |
| [local-dashboard](playground/local-dashboard/) | A loopback-only service on a phone | 45 min | Medium | Yes |

## Pi coding agent on Termux

[Pi coding agent](https://github.com/earendil-works/pi) is particularly interesting on Android because it is a
terminal-native, extensible agent rather than a desktop IDE. It can use the tools already available in Termux, so a
phone can become a real coding workspace: inspect a repository, run commands, edit files, test changes, and keep
working from a resumable session.

Pi still needs an AI model through a configured provider or API. Termux provides the execution environment; Pi does
not make the model local or remove API and network costs by itself.

```sh
pkg update && pkg upgrade
pkg install nodejs npm git
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
node -v
pi --version
cd ~/projects/my-repository
pi
```

`npm` is a separate package in current Termux builds: since Node.js v25.3.0 the `nodejs` package no longer bundles it.
Pi also requires Node.js 22.19 or newer, so check `node -v` before installing.

The full guide, including print and JSON modes, session handling, extension patterns, and the limits Android imposes,
is in [`docs/pi-on-termux.md`](docs/pi-on-termux.md). The upstream guide for Pi on Termux lives at
[`packages/coding-agent/docs/termux.md`](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/termux.md).

## Phone-first constraints

Termux is excellent for development, learning, automation, scripting, local services, and portable tools. It is a poor
substitute for a full desktop Linux host, a secure always-on server, or a hardware lab. Android remains in control: no
root, a sandboxed filesystem, background processes that can be killed at any moment, and binaries that only run on
Android's own C library.

The complete set of constraints, and what to do about each one, is in [`docs/constraints.md`](docs/constraints.md).

## Safety and maintenance

- Do not run random install scripts as root or paste commands you do not understand.
- Keep Termux and companion apps updated from one trusted source.
- Back up important files before experimenting with storage, databases, or automation.
- Do not put API keys, tokens, private photos, or passwords in Git.
- Review permissions and revoke any that an experiment no longer needs.
- Some Android vendors aggressively suspend background work; verify scheduled jobs actually run.

Trust rules for third-party code, extensions, packages, and networks are in [`docs/security.md`](docs/security.md).

## A good experiment template

Every new playground project benefits from:

```text
README.md       purpose, setup, usage, limitations
bin/            executable commands
src/            implementation
tests/          checks and sample data
.env.example    names of configuration values, never secrets
```

Copy [`templates/experiment/`](templates/experiment/) to get the scaffold, and fill in the sections it asks for.
Document the goal, the exact setup commands, a safe cleanup command, and one screenshot or sample output. Then share the
result—or turn the failed experiment into notes. Both are worthwhile.

## Further reading

- [Termux Wiki](https://github.com/termux/termux-app/wiki)
- [Termux packages](https://github.com/termux/termux-packages)
- [Termux:API](https://github.com/termux/termux-api)
- [PRoot Distro](https://github.com/termux/proot-distro)
- [Pi coding agent documentation](https://pi.dev/docs/latest)
- [Pi coding agent Termux guide](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/termux.md)
- [Termux community](https://github.com/termux/termux-app/discussions)

Have an experiment that belongs here? Add a short description, the skill it teaches, phone-specific caveats, and a
safe way to try it. See [`CONTRIBUTING.md`](CONTRIBUTING.md).
