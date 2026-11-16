# Termux basics

What Termux actually is, how to install it, where its files live, how packages behave, and what changes when Android
gets involved.

- [What Termux actually is](#what-termux-actually-is)
- [Start here](#start-here)
- [Installation, updates, and recovery](#installation-updates-and-recovery)
- [Understand the Termux filesystem](#understand-the-termux-filesystem)
- [Packages, compilers, and native builds](#packages-compilers-and-native-builds)
- [Android integrations and add-ons](#android-integrations-and-add-ons)
- [Background execution and reliability](#background-execution-and-reliability)
- [Remote development](#remote-development)
- [Android and mobile application development](#android-and-mobile-application-development)
- [Local AI and model endpoints](#local-ai-and-model-endpoints)
- [Mobile ergonomics and performance](#mobile-ergonomics-and-performance)

## What Termux actually is

Termux is an Android application that bundles a terminal, a shell, and a userspace package collection. It is **not a
virtual machine and not a conventional Linux installation**. Your programs run as Android processes on the device's
Linux kernel, usually through Android's application sandbox.

A useful mental model is:

```text
Android hardware / Linux kernel
        └── Android app sandbox
              └── Termux environment
                    ├── shell and Termux packages
                    └── your programs and files
```

### What feels like Linux

- Familiar shells, pipes, redirects, signals, permissions, processes, sockets, Git, compilers, interpreters, and many
  command-line utilities.
- A package manager and native builds for Android device architectures such as ARM64.
- Real access to the phone's CPU, filesystem area, network stack, and—through companion apps—selected Android features.
- A productive environment for Bash, Python, JavaScript, C/C++, Rust, Go, SQL, Git, SSH, and local web services.

### What is different from a desktop Linux distribution

- **Android is still in control.** There is no systemd desktop session, normal Linux boot process, conventional `/etc`
  layout, or unrestricted daemon management. Termux starts when its app is launched.
- **No normal root access.** You cannot access protected Android data, change the kernel, manage interfaces freely, mount
  arbitrary filesystems, or use privileged ports. Rooted devices are a separate, more complex case.
- **The filesystem is sandboxed.** Termux's private home is usually under its app data directory. `termux-setup-storage`
  exposes selected shared-storage paths under `~/storage`; shared storage has Android-specific permissions and
  limitations.
- **Android may suspend or kill work.** Background jobs, long-running servers, wakelocks, battery optimization,
  reboot, and vendor-specific task killers can affect reliability.
- **Linux binaries are not automatically portable.** Termux packages are built for Android and use Android's Bionic C
  library. A binary copied from Debian, Ubuntu, or a desktop Linux machine generally will not run directly; install a
  Termux package or compile it in Termux.
- **Hardware and GUI access are indirect.** Camera, notifications, sensors, speech, clipboard, and similar features are
  exposed through Termux:API commands. Desktop GUI applications are usually impractical unless using a separate display
  setup.
- **Storage is not a server disk.** Android can revoke access, external and shared storage may not support all Unix
  permissions, and removable storage can be slow or unavailable. Keep active repositories and databases in `~/` when
  possible.

This makes Termux excellent for **development, learning, automation, scripting, local services, and portable tools**, but
a poor substitute for a full desktop Linux host, a secure always-on server, or a hardware lab. The full list of
constraints, and what to do about each one, is in [`constraints.md`](constraints.md).

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

This repository ships an equivalent bootstrap script:

```sh
bash scripts/bootstrap.sh --dry-run
bash scripts/bootstrap.sh
```

`scripts/bootstrap.sh` is idempotent, never deletes anything, and can optionally install Python or Pi:

```sh
bash scripts/bootstrap.sh --with-python
bash scripts/bootstrap.sh --with-pi
```

## Installation, updates, and recovery

- Use Termux and every add-on from the same source, normally F-Droid or the official GitHub releases. Do not mix F-Droid,
  GitHub, and deprecated Play Store builds.
- Update both the application and packages. A package update cannot repair an incompatible or outdated APK.
- Keep a bootstrap script or a package list so the environment can be rebuilt:

```sh
bash scripts/snapshot-packages.sh --out ~/termux-snapshot
```

That writes `termux-packages.txt` and `termux-manual-packages.txt`. To rebuild from a snapshot:

```sh
bash scripts/restore.sh ~/termux-snapshot --dry-run
bash scripts/restore.sh ~/termux-snapshot
```

- Back up `~/` and important configuration such as `~/.ssh`, `~/.gitconfig`, `~/.pi`, and project files. Never back up
  secrets to a public repository.
- If Termux becomes unusable, export important files first when possible, then reinstall from one source and restore
  selectively. Android app-data removal destroys the private Termux home.
- If F-Droid or GitHub is unreachable from your network, Termux supports alternate mirrors and can be pointed at a
  different repository with `termux-change-repo`. Check the Termux wiki for the current mirror list rather than copying
  an old one.

## Understand the Termux filesystem

| Path | Meaning | Recommendation |
| --- | --- | --- |
| `~` | Termux private home | Keep active source code, virtual environments, databases, and build trees here |
| `$PREFIX` | Termux installed packages, commonly `/data/data/com.termux/files/usr` | Do not edit manually; reinstall packages instead |
| `~/storage` | Links created by `termux-setup-storage` | Use when Android apps need to see files |
| `/storage/emulated/0` | Android shared storage | Expect limited Unix permissions and slower or unusual behavior |
| `~/.pi/agent/` | Global Pi resources: `AGENTS.md`, `settings.json`, `mcp.json` | Review before trusting; keep secrets out of Git |
| `.pi/` | Project-local Pi resources | Read them before running Pi in an unfamiliar repository |

Shared storage is good for exported documents, photos, and exchange files. It is usually a poor location for Git
repositories, databases, package installations, and builds because permissions, symlinks, file watching, and executable
bits may not behave like a real Linux filesystem.

## Packages, compilers, and native builds

Termux uses `pkg` as a friendly wrapper around `apt`:

```sh
pkg search keyword
pkg show package-name
pkg install clang make pkg-config
pkg upgrade
```

Termux packages are compiled for Android and the phone's architecture. Prefer them over copying binaries from desktop
Linux. For source builds, check available RAM, storage, compiler requirements, and whether the project assumes glibc,
systemd, Docker, or privileged kernel features.

Useful explorations include compiling C with `clang`, building a Rust or Go CLI, creating a Python package with native
dependencies, and cross-compiling an artifact for another machine. Build failures often describe a missing
Android-compatible dependency rather than a problem with the source itself.

## Android integrations and add-ons

Termux can cooperate with Android through companion applications and intents:

- **Termux:API:** battery, clipboard, camera, notifications, sensors, speech, location, vibration, brightness, and media
  actions where supported.
- **Termux:Widget:** launch approved scripts from the home screen.
- **Termux:Boot:** run scripts after boot, subject to Android background restrictions.
- **Termux:Float:** use a floating terminal over another app.
- **Termux:GUI:** build richer Android-facing interfaces from supported Termux programs.
- **Intents:** use `termux-open`, `termux-open-url`, and Android intent tools to hand work to another application.

Install only the integrations you need and grant the smallest useful permissions. Android version, device manufacturer,
and add-on version affect what works:

```sh
command -v termux-notification
command -v termux-location
termux-open-url 'https://termux.dev'
```

A productive pattern is to keep the core workflow in ordinary shell or Python code and use Termux:API only at the
boundary where Android features are needed.

## Background execution and reliability

Termux processes are ordinary Android app processes. A long-running command may stop when Android reclaims memory, the
app is swiped away, the phone reboots, or a vendor's battery manager intervenes.

For work that can be interrupted:

```sh
tmux new -s work
termux-wake-lock
# run the task, then detach with Ctrl-b d
tmux attach -t work
termux-wake-unlock
```

Use `termux-job-scheduler`, Termux:Boot, or Android automation only for jobs that can tolerate delays and repeated
execution. Make jobs idempotent, log their results, and test them after a reboot. A phone should not be assumed to
provide production-grade uptime.

## Remote development

A phone can be either the client or the small server in a development setup:

- Use `ssh` to work on a desktop, home server, or VPS.
- Use `git`, `rsync`, or a private Git host to move source safely.
- Run a local service on `127.0.0.1` for phone-only access, or deliberately bind to the LAN after understanding the
  firewall and authentication implications.
- Use Pi in Termux as the conversational front end while heavy builds, tests, or model inference run over SSH on a
  stronger machine.
- Use SSH keys protected by a passphrase; avoid exposing an SSH server directly to the public internet.

This hybrid setup is often better than forcing a phone to compile a large project or host an always-on service.

## Android and mobile application development

Termux is useful for source control, code generation, scripting, testing APIs, and some native builds, but Android
application builds have practical limits:

- Gradle and Android SDK builds consume substantial storage, RAM, CPU, and battery.
- SDK components, Java versions, NDK versions, and project plugins must match.
- Emulator-based testing is generally not available inside an unrooted phone's Termux environment.
- A physical Android device, remote CI runner, or desktop can provide the final build and test environment.

Worthwhile experiments include Kotlin and Java command-line exercises, Android project inspection, Gradle dependency
analysis, APK metadata inspection, signing workflow documentation, and using Termux as a Git and SSH front end for a
remote Android build machine. Never handle release signing keys casually or commit them to a project.

Cross-platform stacks such as Flutter, React Native, and web-to-mobile toolchains may require desktop GUI tools, SDK
components, or native dependencies that are not practical on every phone. Verify the current toolchain requirements
before committing to a phone-only workflow.

## Local AI and model endpoints

Agent tools such as Pi normally send requests to a configured model provider, but Termux can also be a client for a model
running elsewhere:

- Connect to a local OpenAI-compatible endpoint on the phone or LAN when a supported model server is available.
- Run small CPU-oriented inference experiments with compatible tools such as `llama.cpp` builds, if the device has enough
  RAM and storage.
- Use a desktop, home server, or VPS for larger models and let Termux provide the terminal interface.
- Keep model files outside shared storage when possible, monitor heat and battery use, and expect slower generation
  without acceleration.
- Compare local and hosted models for privacy, cost, latency, context size, and coding quality.

Local inference is an optional experiment, not a requirement. A model endpoint still needs configuration, sufficient
memory, and a compatible provider interface.

## Mobile ergonomics and performance

- A hardware keyboard, programmable extra keys, and `tmux` often improve productivity more than another package.
- Use narrow output, paging, color only when supported, and JSON modes for machine processing.
- Keep builds cool: avoid unnecessary parallel jobs, close unused processes, and stop servers when finished.
- Monitor `free -h`, `df -h`, `top`, and battery state during heavy work.
- Keep source and caches organized; large SDKs, model files, and build artifacts can silently consume storage.
- Prefer fast feedback: focused tests first, full builds on a remote machine or CI when appropriate.
