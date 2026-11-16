# Troubleshooting

Start with the symptom you have. When nothing in the table fits, collect the diagnostics in
[Collecting diagnostics](#collecting-diagnostics) before changing anything.

- [Symptom map](#symptom-map)
- [A broken installation](#a-broken-installation)
- [Collecting diagnostics](#collecting-diagnostics)

## Symptom map

| Symptom | First checks |
| --- | --- |
| `pi` or another command is missing | `command -v name`, `$PATH`, `npm prefix -g`, then open a new shell |
| `npm` is missing after installing Node.js | Install `npm` explicitly: `pkg install npm`. Since Node.js v25.3.0 the `nodejs` package no longer bundles it |
| `pi` refuses to start on an old Node.js | `node -v`; Pi needs Node.js 22.19 or newer. `pkg upgrade nodejs` |
| `permission denied` in shared storage | Run `termux-setup-storage`; move active work into `~` |
| Package cannot be found | `pkg update`, check the package name, and verify the repository source |
| Repository unreachable | `termux-change-repo` for an alternate mirror; check `pkg update` output for the URLs it tried |
| Desktop binary will not run | Install a Termux package or rebuild for Android; do not assume glibc compatibility |
| Process disappears | Check battery optimization, `tmux`, logs, wakelock use, and vendor restrictions |
| Scheduled job does not run | Test the command manually, inspect Android permissions, and verify the scheduler after reboot |
| Build runs out of memory or storage | Check `free -h` and `df -h`; reduce parallelism or move heavy work to SSH or CI |
| Extension or skill fails | Read startup diagnostics, run `/reload`, inspect dependencies, and test it in isolation |
| Clipboard integration fails | Install both the Termux:API app and the `termux-api` package from the same source |
| Network service is unreachable | Check bind address, port, local firewall or network, and whether Android killed the process |
| `pi` ignores a project config | The project may not be trusted; use `pi --approve` for one run, or `pi --no-approve` to ignore it |
| A codemode script does nothing | Codemode is off by default: `pi --tools +codemode`, or set `"defaultTools": ["+codemode"]` in `~/.pi/agent/settings.json` |

## A broken installation

If Termux itself is unusable:

1. Export what matters first, while the app still opens. The private home lives in the app data directory, so removing
   app data destroys it.
2. Reinstall Termux from one source: F-Droid or the official GitHub releases. Never mix sources.
3. Restore selectively. Configuration lives in `~`: `~/.bashrc`, `~/.ssh`, `~/.gitconfig`, `~/.pi`, and your projects.
4. Rebuild the package set from a snapshot, if you took one:

   ```sh
   bash scripts/restore.sh ~/termux-snapshot --dry-run
   bash scripts/restore.sh ~/termux-snapshot
   ```

5. Re-check with `termux-info`, `df -h`, and `free -h`.

## Collecting diagnostics

```sh
termux-info
df -h
free -h
command -v pi && pi --version
node -v && npm -v
pkg list-installed | head -50
```

`termux-info` reports the Termux version, Android version, device, and architecture. Include it when asking for help
anywhere, because most problems are architecture- or version-specific.

Android may also log Termux activity; with the Termux:API app installed you can read recent system logs from Termux
itself. Read the app's own error output first, though: it is usually more specific.
