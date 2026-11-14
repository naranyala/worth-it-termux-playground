# Termux Playground

A catalog of Android experiments, tools, and tiny projects that are genuinely worth trying from a **terminal on a smartphone**.

Termux turns an Android device into a pocket-sized Linux environment: useful for learning, automation, local services, scripting, networking, and creative tinkering—without root.

> **Guiding idea:** prefer experiments that are useful on a phone, finish in an afternoon, and teach a transferable skill.

## Contents

- [What Termux actually is](#what-termux-actually-is)
- [Start here](#start-here)
- [Pi coding agent on Termux](#pi-coding-agent-on-termux)
- [The playground catalog](#the-playground-catalog)
- [Deeper Termux explorations](#deeper-termux-explorations)
- [A suggested progression](#a-suggested-progression)
- [Phone-first constraints](#phone-first-constraints)
- [Safety and maintenance](#safety-and-maintenance)
- [A good experiment template](#a-good-experiment-template)
- [Further reading](#further-reading)

## What Termux actually is

Termux is an Android application that bundles a terminal, a shell, and a userspace package collection. It is **not a virtual machine and not a conventional Linux installation**. Your programs run as Android processes on the device's Linux kernel, usually through Android's application sandbox.

A useful mental model is:

```text
Android hardware / Linux kernel
        └── Android app sandbox
              └── Termux environment
                    ├── shell and Termux packages
                    └── your programs and files
```

### What feels like Linux

- Familiar shells, pipes, redirects, signals, permissions, processes, sockets, Git, compilers, interpreters, and many command-line utilities.
- A package manager and native builds for Android device architectures such as ARM64.
- Real access to the phone's CPU, filesystem area, network stack, and—through companion apps—selected Android features.
- A productive environment for Bash, Python, JavaScript, C/C++, Rust, Go, SQL, Git, SSH, and local web services.

### What is different from a desktop Linux distribution

- **Android is still in control.** There is no systemd desktop session, normal Linux boot process, conventional `/etc` layout, or unrestricted daemon management. Termux starts when its app is launched.
- **No normal root access.** You cannot access protected Android data, change the kernel, manage interfaces freely, mount arbitrary filesystems, or use privileged ports. Rooted devices are a separate, more complex case.
- **The filesystem is sandboxed.** Termux's private home is usually under its app data directory. `termux-setup-storage` exposes selected shared-storage paths under `~/storage`; shared storage has Android-specific permissions and limitations.
- **Android may suspend or kill work.** Background jobs, long-running servers, wakelocks, battery optimization, reboot, and vendor-specific task killers can affect reliability.
- **Linux binaries are not automatically portable.** Termux packages are built for Android and use Android's Bionic C library. A binary copied from Debian, Ubuntu, or a desktop Linux machine generally will not run directly; install a Termux package or compile it in Termux.
- **Hardware and GUI access are indirect.** Camera, notifications, sensors, speech, clipboard, and similar features are exposed through Termux:API commands. Desktop GUI applications are usually impractical unless using a separate display setup.
- **Storage is not a server disk.** Android can revoke access, external/shared storage may not support all Unix permissions, and removable storage can be slow or unavailable. Keep active repositories and databases in `~/` when possible.

This makes Termux excellent for **development, learning, automation, scripting, local services, and portable tools**, but a poor substitute for a full desktop Linux host, a secure always-on server, or a hardware lab.

## Start here

Install Termux from [F-Droid](https://f-droid.org/packages/com.termux/) or the official [GitHub releases](https://github.com/termux/termux-app/releases). Avoid mixing APKs from different sources. Optional companion apps such as **Termux:API**, **Termux:Widget**, and **Termux:Boot** should come from the same source.

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

## Pi coding agent on Termux

[Pi coding agent](https://github.com/earendil-works/pi) is particularly interesting on Android because it is a terminal-native, extensible agent rather than a desktop IDE. It can use the tools already available in Termux, so a phone can become a real coding workspace: inspect a repository, run commands, edit files, test changes, and keep working from a resumable session.

Pi still needs an AI model through a configured provider or API. Termux provides the execution environment; Pi does not make the model local or remove API/network costs by itself.

### Install it

Pi's Android instructions use the native Termux Node.js package:

```sh
pkg update && pkg upgrade
pkg install nodejs git
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
pi --version
cd ~/projects/my-repository
pi
```

Use the Pi version of the [Termux installation guide](https://github.com/earendil-works/pi/blob/main/docs/termux.md) for current details. Install Termux:API from the same source as Termux only if you want clipboard or Android API integration.

### What Pi can do in a Termux project

**Understand a codebase**

- Read source files, documentation, images, configuration, and test fixtures.
- Search with its tools or ask it to use Termux commands such as `rg`, `find`, `git`, and `jq`.
- Explain architecture, trace a bug, map dependencies, and identify likely risk areas.
- Review a diff, commit, pull request patch, log, or command output.

**Change and create software**

- Edit existing files with targeted changes.
- Create scripts, modules, tests, documentation, configuration, and project scaffolding.
- Refactor incrementally while preserving the surrounding conventions.
- Generate shell, Python, JavaScript/TypeScript, C/C++, Rust, Go, SQL, HTML, and other text-based projects supported by Termux.
- Work in multiple repositories or branches by starting Pi in the relevant directory.

**Run and verify work**

- Execute package managers, compilers, formatters, linters, test suites, migrations, and local servers through the `bash` tool.
- Diagnose failed commands and iterate on a fix.
- Inspect environment variables, ports, processes, Git status, and generated artifacts.
- Ask for a test plan when a complete test suite is too expensive on a phone.

**Use normal software workflows**

- Initialize repositories, create branches, write commits, inspect history, and prepare release notes.
- Review changes before committing; let Git remain the source of truth.
- Work over SSH with a remote computer, VPS, or Git host.
- Use `tmux` so the terminal workspace survives UI interruptions.
- Keep a session per project and resume it later with `pi --continue` or `/resume`.

### Pi modes that are especially useful on a phone

```sh
# Interactive coding session
pi

# Continue the latest session for this directory
pi --continue

# One-shot repository summary
pi --print 'Summarize this repository and identify the three best next tasks'

# Feed a diff to a non-interactive review
git diff | pi --print 'Review this diff for correctness, security, and missing tests'

# Machine-readable events for scripts and logging
pi --mode json 'Run a lightweight project health check' > pi-events.jsonl

# Include a file in the first prompt
pi '@README.md' 'Suggest improvements while preserving the project voice'
```

On a narrow screen, `--print` is useful for short tasks and shell pipelines; interactive mode is better for iterative edits. JSON mode is useful for automation, while RPC mode and the TypeScript SDK can turn Pi into a component of another Termux application.

### Make Pi Android-aware

Create `~/.pi/agent/AGENTS.md` with only the rules relevant to your device and projects:

```markdown
# Termux environment

- Pi runs in Termux on Android.
- Keep active repositories and databases under the Termux home directory.
- Shared Android storage is available under ~/storage when explicitly needed.
- Open URLs with `termux-open-url`; open files with `termux-open`.
- Use Termux:API for Android features instead of assuming desktop Linux APIs.
- Prefer commands that are resumable and safe to interrupt.
```

This lets Pi remember the environment without repeating it in every prompt. Project-local `AGENTS.md` files can describe build commands, conventions, and safety boundaries for individual repositories.

### Extend Pi into a mobile development platform

Pi is deliberately extensible. On Termux, this opens several playgrounds:

- **Skills:** reusable task knowledge such as Android builds, SQLite analysis, release checklists, or media workflows. A skill can include scripts and reference files.
- **Prompt templates:** repeatable prompts for code review, debugging, changelog generation, or repository onboarding.
- **Extensions:** TypeScript modules that add custom tools, slash commands, keyboard shortcuts, approval gates, status widgets, session state, event hooks, or custom UI.
- **Packages:** share extensions, skills, prompts, and themes through npm or Git.
- **MCP servers:** connect trusted external tools and data sources, such as a local database, documentation search, browser automation, or a personal service.
- **Codemode:** run JavaScript that orchestrates multiple tools, filters large command output, and performs parallel inspection.
- **RPC and SDK:** build a Termux dashboard, a notification-driven assistant, a local web UI, a scheduled code-review job, or another application that controls Pi programmatically.
- **Custom providers and models:** connect compatible remote or local model endpoints when the device and provider support them.

A phone-friendly extension could, for example, ask for confirmation before touching shared storage, create a Git checkpoint before edits, show battery status, open a URL through Android, or block dangerous commands. Extensions run with Pi's operating-system permissions, so review code and packages before loading them.

### Pi + Termux project ideas

1. **Repository doctor:** inspect Git status, dependency manifests, tests, disk space, and recent failures; print a compact report.
2. **Guided coding tutor:** a project-local skill that explains each command and requires the user to approve edits.
3. **Mobile issue triage:** turn copied issue text into reproduction steps, candidate files, and a test checklist.
4. **Android script builder:** describe a notification, clipboard, backup, or media workflow and have Pi create a safe Termux script.
5. **Commit companion:** summarize staged changes, detect secrets, suggest a commit message, and refuse to commit without confirmation.
6. **Local service operator:** start a server in `tmux`, inspect logs, run health checks, and explain failures.
7. **Learning lab generator:** ask for a topic and have Pi create a small repository with exercises, tests, and progressive hints.
8. **Remote development bridge:** use Termux as the mobile front end while SSH commands and heavy builds run on a more powerful machine.
9. **Session-to-documentation pipeline:** export a session, extract decisions, and update project notes or a changelog.
10. **Personal automation assistant:** combine Pi's reasoning with shell scripts and Termux:API, while keeping destructive actions behind explicit approval.

### What Pi cannot overcome on Android

Pi can only do what the Termux process and Android permissions allow. It cannot grant root, bypass Android sandboxing, guarantee background execution, turn a phone into an always-on server, or make desktop Linux binaries compatible with Android. It also cannot reliably perform visual Android UI automation without additional tooling. Large builds, huge repositories, long context windows, and local model inference may be limited by RAM, storage, heat, battery, and network quality.

Treat model output as proposed work: inspect the diff, run tests, protect secrets, and confirm commands that delete files, modify shared storage, publish code, change infrastructure, or spend money.

## The playground catalog

Legend: **★** especially good on a phone · **offline** works without a network · **safe** does not require root or privileged access.

The projects below are ordered from quick, phone-native experiments to larger systems. Most are intentionally small: the goal is to learn by finishing, then extend the experiment with Pi or your own code.

### 1. Make the terminal yours

| Experiment | What to explore | Why it is worth it |
|---|---|---|
| ★ Personal shell | Bash/Zsh aliases, functions, history, `$PATH`, prompt themes | Learn the interface you will use for everything else |
| ★ `tmux` workspace | Persistent panes for notes, logs, and a server | Makes a small screen surprisingly productive |
| Terminal editor | Vim, Helix, Emacs, or `micro` | Edit code anywhere, even offline |
| Dotfiles repository | Keep `.bashrc`, editor settings, and scripts in Git | Reproducible setup and a real version-control habit |
| Keyboard laboratory | Try a hardware keyboard, extra keys, Termux shortcuts, and gesture navigation | Discover a comfortable mobile workflow |

Useful packages: `zsh`, `fish`, `starship`, `fzf`, `ripgrep`, `fd`, `bat`, `eza`, `tree`, `jq`.

### 2. Learn programming by building tiny tools

| Project | Suggested stack | First milestone |
|---|---|---|
| ★ CLI habit tracker | Python or JavaScript + SQLite | Add, complete, and list habits offline |
| ★ Expense or inventory tracker | Python + CSV/SQLite | Import data and print a useful report |
| Markdown journal | Shell/Python + `git` | Create dated entries and search them with `rg` |
| File organizer | Python or shell | Sort Downloads by extension, with a dry-run mode |
| Static website | HTML/CSS + a local server | Build a one-page site and view it on the phone |
| Log analyzer | `awk`, Python, or `jq` | Summarize a web/server log into counts and tables |
| Terminal game | Python, Lua, or C | Make a small roguelike, quiz, or word game |
| API client | Python `requests` or `curl` + `jq` | Call a public API, handle errors, cache results |
| Package a script | `pip`, `npm`, or a shell installer | Turn a useful script into a repeatable command |

Good practice: write a README, include `--help`, validate input, and keep experiments in a Git repository.

### 3. Explore Android from the command line

Install [Termux:API](https://github.com/termux/termux-api) and its package:

```sh
pkg install termux-api
termux-battery-status
termux-brightness 80
termux-toast 'Hello from the shell'
termux-vibrate -d 200
termux-clipboard-get
```

Ideas:

- A battery notifier that uses `termux-job-scheduler`.
- A clipboard cleaner or formatter.
- A one-command “focus mode” that changes brightness and opens a workspace.
- A spoken reminder using `termux-tts-speak`.
- A photo/file workflow using `termux-camera-photo`, `termux-media-scan`, and `termux-share`.
- A local dashboard displaying battery, storage, network, and task status.

The available Android integrations depend on the companion app and Android version. Check each command with `command -v` and its `--help` output.

### 4. Build useful automations

- **Daily backup:** archive selected folders and copy them to a trusted destination; verify the archive before deleting anything.
- **Inbox triage:** find large or old files in `~/storage/downloads` and produce a review report.
- **Photo pipeline:** resize, rename, strip or preserve metadata intentionally, and generate contact sheets with ImageMagick.
- **RSS/news digest:** fetch feeds with `curl`, parse XML, and render a plain-text digest.
- **Reminder bot:** schedule a script and send a notification through Termux:API.
- **Personal command center:** a `menu.sh` script that launches common tasks and shows device status.

Useful packages: `python`, `imagemagick`, `ffmpeg`, `rsync`, `sqlite`, `cronie`, `termux-services`.

### 5. Run local services on your phone

Start with services designed for local-only use:

```sh
pkg install python
mkdir -p ~/www
printf '<h1>Hello from Termux</h1>\n' > ~/www/index.html
cd ~/www && python -m http.server 8080 --bind 127.0.0.1
```

Then explore:

- A local Markdown/wiki server.
- A SQLite-backed notes API.
- A personal file browser bound to `127.0.0.1`.
- A webhook receiver for experiments.
- A static site generator and preview server.
- SSH access from another device on your private network.

Use `127.0.0.1` unless you deliberately need LAN access. Android may stop background processes; `tmux`, wakelocks, and Termux:Boot can help, but do not treat a phone as an always-on server.

### 6. Linux distributions without root

Try [PRoot Distro](https://github.com/termux/proot-distro) for Debian, Ubuntu, Alpine, or Arch userspace:

```sh
pkg install proot-distro
proot-distro list
proot-distro install debian
proot-distro login debian
```

A PRoot distribution provides a more familiar filesystem layout and access to distribution-specific packages, which is useful for learning Debian/Ubuntu administration or testing software that expects glibc. It still runs inside the Termux Android process and does **not** become a real VM or grant real root privileges.

Expect trade-offs: filesystem translation can be slower, kernel features and hardware access remain Android-limited, services do not magically start at boot, and desktop packages may not be useful without a display environment. Use native Termux packages for everyday phone tooling; use PRoot when compatibility with a conventional Linux userspace is the thing you are specifically exploring.

### 7. Networking and security—ethically

Great learning projects:

- Inspect your own HTTP requests with `curl -v`.
- Learn DNS using `dig` and `nslookup`.
- Serve a test site and inspect headers with `curl -I`.
- Use `nmap` only against devices and networks you own or have explicit permission to test.
- Generate SSH keys and connect to your own computer or VPS.
- Capture and analyze your own application traffic in a controlled lab.
- Build a local password-strength checker without collecting passwords.

Never scan, exploit, brute-force, or intercept systems without authorization. Termux is a powerful terminal, not a license to access someone else’s device or network.

### 8. Data, media, and creative computing

| Exploration | Tools |
|---|---|
| Process JSON, CSV, and logs | `jq`, `awk`, Python, SQLite |
| Convert and inspect media | `ffmpeg`, ImageMagick, `exiftool` |
| Make ASCII art or terminal dashboards | `figlet`, `toilet`, `watch`, ANSI escape codes |
| Generate music or synth experiments | Python, SuperCollider packages where supported |
| Read offline documentation | `man`, `tldr`, downloaded Markdown, `pandoc` |
| Compile a small native program | `clang`, `make`, `cmake`, Rust or Go |
| Create a text-based RSS reader | Python, `curl`, SQLite |

### 9. Bigger projects for a weekend

1. **Offline-first personal knowledge base** — Markdown files, tags, full-text search, and a static export.
2. **Phone health dashboard** — battery, storage, connectivity, and notification history in one terminal view.
3. **LAN dropbox** — authenticated local upload/download with expiration and clear network boundaries.
4. **Backup appliance** — encrypted, versioned backups to a computer or cloud storage, with restore tests.
5. **Tiny CI runner** — clone a repository, run tests, and report results locally.
6. **Self-hosted status page** — monitor only your own services and display uptime/history.
7. **Interactive shell course** — a series of scripts that teach commands through small challenges.

## Deeper Termux explorations

The catalog above gives quick projects. These topics explain how to turn Termux into a more capable, reliable mobile development environment.

### Installation, updates, and recovery

- Use Termux and every add-on from the same source, normally F-Droid or the official GitHub releases. Do not mix F-Droid, GitHub, and deprecated Play Store builds.
- Update both the application and packages. A package update cannot repair an incompatible or outdated APK.
- Keep a bootstrap script or a package list so the environment can be rebuilt:

```sh
pkg list-installed > ~/termux-packages.txt
apt-mark showmanual > ~/termux-manual-packages.txt
```

- Back up `~/` and important configuration such as `~/.ssh`, `~/.gitconfig`, `~/.pi`, and project files. Never back up secrets to a public repository.
- If Termux becomes unusable, export important files first when possible, then reinstall from one source and restore selectively. Android app-data removal destroys the private Termux home.

### Understand the Termux filesystem

| Path | Meaning | Recommendation |
|---|---|---|
| `~` | Termux private home | Keep active source code, virtual environments, databases, and build trees here |
| `$PREFIX` | Termux installed packages, commonly `/data/data/com.termux/files/usr` | Do not edit manually; reinstall packages instead |
| `~/storage` | Links created by `termux-setup-storage` | Use when Android apps need to see files |
| `/storage/emulated/0` | Android shared storage | Expect limited Unix permissions and slower or unusual behavior |
| `.pi/` and `.agents/` | Project-local Pi resources | Review before trusting extensions or skills |

Shared storage is good for exported documents, photos, and exchange files. It is usually a poor location for Git repositories, databases, package installations, and builds because permissions, symlinks, file watching, and executable bits may not behave like a real Linux filesystem.

### Packages, compilers, and native builds

Termux uses `pkg` as a friendly wrapper around `apt`:

```sh
pkg search keyword
pkg show package-name
pkg install clang make pkg-config
pkg upgrade
```

Termux packages are compiled for Android and the phone's architecture. Prefer them over copying binaries from desktop Linux. For source builds, check available RAM, storage, compiler requirements, and whether the project assumes glibc, systemd, Docker, or privileged kernel features.

Useful explorations include compiling C with `clang`, building a Rust or Go CLI, creating a Python package with native dependencies, and cross-compiling an artifact for another machine. Build failures often describe a missing Android-compatible dependency rather than a problem with the source itself.

### Android integrations and add-ons

Termux can cooperate with Android through companion applications and intents:

- **Termux:API:** battery, clipboard, camera, notifications, sensors, speech, location, vibration, brightness, and media actions where supported.
- **Termux:Widget:** launch approved scripts from the home screen.
- **Termux:Boot:** run scripts after boot, subject to Android background restrictions.
- **Termux:Float:** use a floating terminal over another app.
- **Termux:GUI:** build richer Android-facing interfaces from supported Termux programs.
- **Intents:** use `termux-open`, `termux-open-url`, and Android intent tools to hand work to another application.

Install only the integrations you need and grant the smallest useful permissions. Android version, device manufacturer, and add-on version affect what works:

```sh
command -v termux-notification
command -v termux-location
termux-open-url 'https://termux.dev'
```

A productive pattern is to keep the core workflow in ordinary shell/Python code and use Termux:API only at the boundary where Android features are needed.

### Background execution and reliability

Termux processes are ordinary Android app processes. A long-running command may stop when Android reclaims memory, the app is swiped away, the phone reboots, or a vendor's battery manager intervenes.

For work that can be interrupted:

```sh
tmux new -s work
termux-wake-lock     # use only while needed
# run the task, then detach with Ctrl-b d
tmux attach -t work
termux-wake-unlock
```

Use `termux-job-scheduler`, Termux:Boot, or Android automation only for jobs that can tolerate delays and repeated execution. Make jobs idempotent, log their results, and test them after a reboot. A phone should not be assumed to provide production-grade uptime.

### Remote development

A phone can be either the client or the small server in a development setup:

- Use `ssh` to work on a desktop, home server, or VPS.
- Use `git`, `rsync`, or a private Git host to move source safely.
- Run a local service on `127.0.0.1` for phone-only access, or deliberately bind to the LAN after understanding the firewall and authentication implications.
- Use Pi in Termux as the conversational front end while heavy builds, tests, or model inference run over SSH on a stronger machine.
- Use SSH keys protected by a passphrase; avoid exposing an SSH server directly to the public internet.

This hybrid setup is often better than forcing a phone to compile a large project or host an always-on service.

### Android and mobile application development

Termux is useful for source control, code generation, scripting, testing APIs, and some native builds, but Android application builds have practical limits:

- Gradle and Android SDK builds consume substantial storage, RAM, CPU, and battery.
- SDK components, Java versions, NDK versions, and project plugins must match.
- Emulator-based testing is generally not available inside an unrooted phone's Termux environment.
- A physical Android device, remote CI runner, or desktop can provide the final build and test environment.

Worthwhile experiments include Kotlin/Java command-line exercises, Android project inspection, Gradle dependency analysis, APK metadata inspection, signing workflow documentation, and using Termux as a Git/SSH front end for a remote Android build machine. Never handle release signing keys casually or commit them to a project.

Cross-platform stacks such as Flutter, React Native, and web-to-mobile toolchains may require desktop GUI tools, SDK components, or native dependencies that are not practical on every phone. Verify the current toolchain requirements before committing to a phone-only workflow.

### Local AI and model endpoints

Pi normally sends requests to a configured model provider, but Termux can also be a client for a model running elsewhere:

- Connect Pi to a local OpenAI-compatible endpoint on the phone or LAN when a supported model server is available.
- Run small CPU-oriented inference experiments with compatible tools such as `llama.cpp` builds, if the device has enough RAM and storage.
- Use a desktop, home server, or VPS for larger models and let Termux provide the terminal interface.
- Keep model files outside shared storage when possible, monitor heat and battery use, and expect slower generation without acceleration.
- Compare local and hosted models for privacy, cost, latency, context size, and coding quality.

Local inference is an optional experiment, not a requirement for Pi. A model endpoint still needs configuration, sufficient memory, and a compatible provider interface.

### Pi workflows worth building

Pi is most useful when surrounded by small, explicit workflows rather than treated as an unrestricted command executor:

- Put project conventions, build commands, test commands, and boundaries in `AGENTS.md`.
- Use skills for repeatable domain procedures and prompt templates for recurring requests.
- Use extensions for confirmation gates, Git checkpoints, secret protection, Android notifications, and project dashboards.
- Use MCP only for trusted integrations, with the smallest useful tool exposure.
- Use `--print` for one-shot reports, JSON mode for scripts, RPC/SDK for applications, and sessions for iterative work.
- Have Pi explain a proposed change, make the smallest edit, run focused tests, then review the diff before committing.
- Export or summarize long sessions into project notes so important decisions do not remain trapped in chat history.

A useful mobile pattern is: **inspect → propose → approve → edit → test → review → commit**.

### Security, privacy, and trust

Pi, shell scripts, extensions, skills, MCP servers, and npm packages can all execute with the permissions available to the Termux process. Treat project resources as code:

- Read unfamiliar `AGENTS.md`, skills, extensions, and install scripts before trusting them.
- Use project-local resources only in repositories you recognize.
- Keep API keys in environment variables or a protected secret store, not prompts, source files, logs, or Git history.
- Restrict shared-storage access and avoid granting more Android permissions than necessary.
- Use separate test credentials and disposable directories for experiments.
- Review `git diff`, command output, network destinations, and file paths before approving consequential actions.
- Protect commands that delete, overwrite, publish, install, change infrastructure, or transfer private data.

Termux is not a security boundary against code you voluntarily run. The model is also not a security reviewer by itself.

### Troubleshooting map

| Symptom | First checks |
|---|---|
| `pi` or another command is missing | `command -v name`, `$PATH`, `npm prefix -g`, then open a new shell |
| `permission denied` in shared storage | Run `termux-setup-storage`; move active work into `~` |
| Package cannot be found | `pkg update`, check the package name, and verify the repository source |
| Desktop binary will not run | Install a Termux package or rebuild for Android; do not assume glibc compatibility |
| Process disappears | Check battery optimization, `tmux`, logs, wakelock use, and vendor restrictions |
| Scheduled job does not run | Test the command manually, inspect Android permissions, and verify the scheduler after reboot |
| Build runs out of memory or storage | Check `free -h` and `df -h`; reduce parallelism or move heavy work to SSH/CI |
| Pi extension or skill fails | Read startup diagnostics, run `/reload`, inspect dependencies, and test it in isolation |
| Clipboard integration fails | Install both the Termux:API app and `termux-api` package from the same source |
| Network service is unreachable | Check bind address, port, local firewall/network, and whether Android killed the process |

### Mobile ergonomics and performance

- A hardware keyboard, programmable extra keys, and `tmux` often improve productivity more than another package.
- Use narrow output, paging, color only when supported, and JSON modes for machine processing.
- Keep builds cool: avoid unnecessary parallel jobs, close unused processes, and stop servers when finished.
- Monitor `free -h`, `df -h`, `top`, and battery state during heavy work.
- Keep source and caches organized; large SDKs, model files, and build artifacts can silently consume storage.
- Prefer fast feedback: focused tests first, full builds on a remote machine or CI when appropriate.

## A suggested progression

- **Level 1:** files, pipes, `grep`/`rg`, Git, shell scripts, `tmux`.
- **Level 2:** Python, SQLite, JSON APIs, scheduled jobs, Termux:API.
- **Level 3:** local web services, SSH, backups, containers/userspaces, testing.
- **Level 4:** networking labs, native compilation, observability, and a polished open-source project.

## Phone-first constraints to design for

- Treat Termux as a user application, not a server operating system; design for restarts and interrupted sessions.
- Keep output readable on a narrow screen; provide `--brief` or `--json` modes.
- Expect interruptions, battery limits, Android process killing, and changing networks.
- Store source code in `~/`, and use shared storage only when Android apps need access.
- Make scripts idempotent, resumable, and safe to stop with `Ctrl-C`.
- Avoid destructive commands by default; support `--dry-run` and confirmations.
- Prefer small dependencies and offline-friendly documentation.
- Test restores, not just backups.

## Safety and maintenance

- Do not run random install scripts as root or paste commands you do not understand.
- Keep Termux and companion apps updated from one trusted source.
- Back up important files before experimenting with storage, databases, or automation.
- Do not put API keys, tokens, private photos, or passwords in Git.
- Review permissions and revoke any that an experiment no longer needs.
- Some Android vendors aggressively suspend background work; verify scheduled jobs actually run.

## A good experiment template

Every new playground project benefits from:

```text
README.md       purpose, setup, usage, limitations
bin/            executable commands
src/            implementation
tests/          checks and sample data
.env.example    names of configuration values, never secrets
```

Document the goal, the exact setup commands, a safe cleanup command, and one screenshot or sample output. Then share the result—or turn the failed experiment into notes. Both are worthwhile.

## Further reading

- [Termux Wiki](https://github.com/termux/termux-app/wiki)
- [Termux packages](https://github.com/termux/termux-packages)
- [Termux:API](https://github.com/termux/termux-api)
- [PRoot Distro](https://github.com/termux/proot-distro)
- [Pi coding agent Termux guide](https://github.com/earendil-works/pi/blob/main/docs/termux.md)
- [Pi coding agent documentation](https://github.com/earendil-works/pi/tree/main/docs)
- [Termux community](https://github.com/termux/termux-app/discussions)

Have an experiment that belongs here? Add a short description, the skill it teaches, phone-specific caveats, and a safe way to try it.
