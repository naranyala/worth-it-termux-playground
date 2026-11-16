# Constraints

Android is the operating system underneath everything here. This page collects every constraint it enforces in one
place, what it means for an experiment, and what to do about it. Other pages link here rather than restating it.

- [The constraint matrix](#the-constraint-matrix)
- [Phone-first design rules](#phone-first-design-rules)
- [Safety and maintenance](#safety-and-maintenance)

## The constraint matrix

| Constraint | What Android enforces | What to do about it | Affects |
| --- | --- | --- | --- |
| No root | Protected data, the kernel, interfaces, and privileged ports are out of reach | Stay inside the app sandbox; use Termux:API for Android features instead of poking at them | Everything privileged |
| App sandbox | Termux runs as an ordinary app with a private home | Keep source, databases, and caches in `~` | File layout, storage |
| Shared storage | `~/storage` needs explicit permission and may not support Unix permissions, symlinks, or executable bits | Use shared storage for exchange files only; keep repositories and databases in `~` | File layout |
| Background execution | Android reclaims memory, and swiping the app away ends its processes | Use `tmux` for long sessions, `termux-job-scheduler` for tolerant jobs, and Termux:Boot for startup | Services, automations |
| Vendor battery managers | Aggressive OEMs suspend background work aggressively | Verify scheduled jobs actually run after a reboot; keep jobs idempotent and logged | Automations |
| No systemd | No service supervision, no conventional `/etc`, no boot-time daemon start | Use `termux-services` or `tmux` instead of systemd units | Local services |
| Bionic, not glibc | Desktop binaries do not run; Debian binaries fail with missing-symbol errors | Install a Termux package or compile the source in Termux | Dependencies, builds |
| No emulator or hardware lab | Android SDK emulator and most device instrumentation need a host machine | Use a desktop, a remote CI runner, or a physical second device for final builds | Android development |
| Process lifetime | Long compiles and servers can be killed at any moment | Make work resumable, checkpointed, and cheap to restart | Builds, servers |
| Heat and battery | Sustained CPU work throttles and drains the battery | Monitor with `termux-battery-status`, avoid unnecessary parallel jobs, stop servers when done | Builds, inference |
| Screen width | Terminal output is narrow and scrollback is awkward | Prefer narrow output, add `--brief` and `--json` modes, use `tmux` for panes | Every script |
| Storage quotas | Shared storage can be revoked; removable storage can vanish mid-write | Write to a temp file, then `mv` into place; never depend on external storage for state | Automations |
| Permissions per add-on | Each companion app grants a slice of Android capability | Install only the add-ons you use, grant the minimum, revoke later | Termux:API and friends |
| Clipboard is text only | The Android clipboard API cannot carry images into a terminal | Paste images by saving them to a file and referencing the path | Editor workflows |

## Phone-first design rules

- Treat Termux as a user application, not a server operating system; design for restarts and interrupted sessions.
- Keep output readable on a narrow screen; provide `--brief` or `--json` modes.
- Expect interruptions, battery limits, Android process killing, and changing networks.
- Store source code in `~/`, and use shared storage only when Android apps need access.
- Make scripts idempotent, resumable, and safe to stop with Ctrl-C.
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

See [`security.md`](security.md) for the trust rules that apply to code you install and to networks you touch.
