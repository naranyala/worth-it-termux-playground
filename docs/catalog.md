# The playground catalog

Experiments ordered from quick, phone-native ones to larger systems. Most are intentionally small: the goal is to learn
by finishing, then extend the experiment with an agent or your own code.

The same five experiments are implemented in [`playground/`](../playground/INDEX.md) if you would rather run one than
read about it.

Columns used below:

- **Time** — a realistic estimate for one sitting.
- **Level** — Easy, Medium, or Hard for someone comfortable with a shell.
- **Offline** — whether the experiment works with no network at all.

## 1. Make the terminal yours

| Experiment | What to explore | Why it is worth it | Time | Level | Offline |
| --- | --- | --- | --- | --- | --- |
| ★ Personal shell | Bash and Zsh aliases, functions, history, `$PATH`, prompt themes | Learn the interface you will use for everything else | 20 min | Easy | Yes |
| ★ `tmux` workspace | Persistent panes for notes, logs, and a server | Makes a small screen surprisingly productive | 20 min | Easy | Yes |
| Terminal editor | Vim, Helix, Emacs, or `micro` | Edit code anywhere, even offline | 1 hour | Medium | Yes |
| Dotfiles repository | Keep `.bashrc`, editor settings, and scripts in Git | Reproducible setup and a real version-control habit | 1 hour | Medium | Yes |
| Keyboard laboratory | Try a hardware keyboard, extra keys, Termux shortcuts, and gesture navigation | Discover a comfortable mobile workflow | 30 min | Easy | Yes |

Useful packages: `zsh`, `fish`, `starship`, `fzf`, `ripgrep`, `fd`, `bat`, `eza`, `tree`, `jq`.

## 2. Learn programming by building tiny tools

| Project | Suggested stack | First milestone | Time | Level | Offline |
| --- | --- | --- | --- | --- | --- |
| ★ CLI habit tracker | Python or JavaScript + SQLite | Add, complete, and list habits offline | 30 min | Easy | Yes |
| ★ Expense or inventory tracker | Python + CSV or SQLite | Import data and print a useful report | 1 hour | Medium | Yes |
| Markdown journal | Shell or Python + `git` | Create dated entries and search them with `rg` | 30 min | Easy | Yes |
| File organizer | Python or shell | Sort Downloads by extension, with a dry-run mode | 45 min | Medium | Yes |
| Static website | HTML and CSS + a local server | Build a one-page site and view it on the phone | 45 min | Easy | Yes |
| Log analyzer | `awk`, Python, or `jq` | Summarize a web or server log into counts and tables | 1 hour | Medium | Yes |
| Terminal game | Python, Lua, or C | Make a small roguelike, quiz, or word game | 2 hours | Medium | Yes |
| API client | Python `requests` or `curl` + `jq` | Call a public API, handle errors, cache results | 1 hour | Medium | No |
| Package a script | `pip`, `npm`, or a shell installer | Turn a useful script into a repeatable command | 1 hour | Medium | Yes |

Good practice: write a README, include `--help`, validate input, and keep experiments in a Git repository.

## 3. Explore Android from the command line

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
- A one-command "focus mode" that changes brightness and opens a workspace.
- A spoken reminder using `termux-tts-speak`.
- A photo and file workflow using `termux-camera-photo`, `termux-media-scan`, and `termux-share`.
- A local dashboard displaying battery, storage, network, and task status.

The available Android integrations depend on the companion app and Android version. Check each command with
`command -v` and its `--help` output.

Time: 1 hour for the first integration, then 30 minutes per additional idea. Level: Easy. Offline: yes, for anything
that does not call a remote API.

## 4. Build useful automations

- **Daily backup:** archive selected folders and copy them to a trusted destination; verify the archive before deleting
  anything.
- **Inbox triage:** find large or old files in `~/storage/downloads` and produce a review report.
- **Photo pipeline:** resize, rename, strip or preserve metadata intentionally, and generate contact sheets with
  ImageMagick.
- **RSS and news digest:** fetch feeds with `curl`, parse XML, and render a plain-text digest.
- **Reminder bot:** schedule a script and send a notification through Termux:API.
- **Personal command center:** a `menu.sh` script that launches common tasks and shows device status.

Useful packages: `python`, `imagemagick`, `ffmpeg`, `rsync`, `sqlite`, `cronie`, `termux-services`.

Time: 1 to 2 hours each. Level: Medium. Offline: yes for the ones that only read local files.

## 5. Run local services on your phone

Start with services designed for local-only use:

```sh
pkg install python
mkdir -p ~/www
printf '<h1>Hello from Termux</h1>\n' > ~/www/index.html
cd ~/www && python -m http.server 8080 --bind 127.0.0.1
```

Then explore:

- A local Markdown or wiki server.
- A SQLite-backed notes API.
- A personal file browser bound to `127.0.0.1`.
- A webhook receiver for experiments.
- A static site generator and preview server.
- SSH access from another device on your private network.

Use `127.0.0.1` unless you deliberately need LAN access. Android may stop background processes; `tmux`, wakelocks, and
Termux:Boot can help, but do not treat a phone as an always-on server.

Time: 45 minutes for the first one. Level: Easy to Medium. Offline: yes.

## 6. Linux distributions without root

Try [PRoot Distro](https://github.com/termux/proot-distro) for Debian, Ubuntu, Alpine, or Arch userspace:

```sh
pkg install proot-distro
proot-distro list
proot-distro install debian
proot-distro login debian
```

A PRoot distribution provides a more familiar filesystem layout and access to distribution-specific packages, which is
useful for learning Debian or Ubuntu administration or testing software that expects glibc. It still runs inside the
Termux Android process and does **not** become a real VM or grant real root privileges.

Expect trade-offs: filesystem translation can be slower, kernel features and hardware access remain Android-limited,
services do not magically start at boot, and desktop packages may not be useful without a display environment. Use native
Termux packages for everyday phone tooling; use PRoot when compatibility with a conventional Linux userspace is the
thing you are specifically exploring.

Time: 1 hour to set up, then open-ended. Level: Medium. Offline: the install needs network, the session does not.

## 7. Networking and security, ethically

Great learning projects:

- Inspect your own HTTP requests with `curl -v`.
- Learn DNS using `dig` and `nslookup`.
- Serve a test site and inspect headers with `curl -I`.
- Use `nmap` only against devices and networks you own or have explicit permission to test.
- Generate SSH keys and connect to your own computer or VPS.
- Capture and analyze your own application traffic in a controlled lab.
- Build a local password-strength checker without collecting passwords.

Never scan, exploit, brute-force, or intercept systems without authorization. Termux is a powerful terminal, not a license
to access someone else's device or network. See [`security.md`](security.md) for the full trust model.

Time: 1 hour each. Level: Medium. Offline: partly.

## 8. Data, media, and creative computing

| Exploration | Tools | Time | Level | Offline |
| --- | --- | --- | --- | --- |
| Process JSON, CSV, and logs | `jq`, `awk`, Python, SQLite | 30 min | Easy | Yes |
| Convert and inspect media | `ffmpeg`, ImageMagick, `exiftool` | 1 hour | Medium | Yes |
| Make ASCII art or terminal dashboards | `figlet`, `toilet`, `watch`, ANSI escape codes | 30 min | Easy | Yes |
| Generate music or synth experiments | Python, SuperCollider packages where supported | 2 hours | Hard | Yes |
| Read offline documentation | `man`, `tldr`, downloaded Markdown, `pandoc` | 20 min | Easy | Yes |
| Compile a small native program | `clang`, `make`, `cmake`, Rust or Go | 1 hour | Medium | Yes |
| Create a text-based RSS reader | Python, `curl`, SQLite | 1 hour | Medium | Cached |

## 9. Bigger projects for a weekend

1. **Offline-first personal knowledge base** — Markdown files, tags, full-text search, and a static export.
2. **Phone health dashboard** — battery, storage, connectivity, and notification history in one terminal view.
3. **LAN dropbox** — authenticated local upload and download with expiration and clear network boundaries.
4. **Backup appliance** — encrypted, versioned backups to a computer or cloud storage, with restore tests.
5. **Tiny CI runner** — clone a repository, run tests, and report results locally.
6. **Self-hosted status page** — monitor only your own services and display uptime and history.
7. **Interactive shell course** — a series of scripts that teach commands through small challenges.

Time: a weekend. Level: Hard. Offline: mostly, once the dependencies are installed.

## A suggested progression

- **Level 1:** files, pipes, `grep` and `rg`, Git, shell scripts, `tmux`.
- **Level 2:** Python, SQLite, JSON APIs, scheduled jobs, Termux:API.
- **Level 3:** local web services, SSH, backups, containers and userspaces, testing.
- **Level 4:** networking labs, native compilation, observability, and a polished open-source project.
