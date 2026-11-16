# Pi coding agent on Termux

[Pi coding agent](https://github.com/earendil-works/pi) is particularly interesting on Android because it is a
terminal-native, extensible agent rather than a desktop IDE. It can use the tools already available in Termux, so a
phone can become a real coding workspace: inspect a repository, run commands, edit files, test changes, and keep working
from a resumable session.

Pi still needs a model through a configured provider or API. Termux provides the execution environment; Pi does not make
the model local or remove API and network costs by itself.

- [Install it](#install-it)
- [What Pi can do in a Termux project](#what-pi-can-do-in-a-termux-project)
- [Pi modes that are especially useful on a phone](#pi-modes-that-are-especially-useful-on-a-phone)
- [Make Pi Android-aware](#make-pi-android-aware)
- [Extend Pi into a mobile development platform](#extend-pi-into-a-mobile-development-platform)
- [Pi plus Termux project ideas](#pi-plus-termux-project-ideas)
- [What Pi cannot overcome on Android](#what-pi-cannot-overcome-on-android)
- [Pi workflows worth building](#pi-workflows-worth-building)

## Install it

Pi's Android instructions use the native Termux Node.js package:

```sh
pkg update && pkg upgrade
pkg install nodejs npm git
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
node -v
pi --version
cd ~/projects/my-repository
pi
```

Two details worth knowing:

- `npm` is a separate package in current Termux builds. Since Node.js v25.3.0 the `nodejs` package no longer bundles
  npm, so install it explicitly. Pi requires Node.js 22.19 or newer; check `node -v` first.
- The npm install above does not pin transitive dependencies. The upstream installer does, and updates Pi in place:

```sh
curl -fsSL https://pi.dev/install.sh | sh
pi update
```

Use the version of the [Termux installation guide](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/termux.md)
for current details. Install Termux:API from the same source as Termux only if you want clipboard or Android API
integration.

## What Pi can do in a Termux project

### Understand a codebase

- Read source files, documentation, images, configuration, and test fixtures.
- Search with its tools or ask it to use Termux commands such as `rg`, `find`, `git`, and `jq`.
- Explain architecture, trace a bug, map dependencies, and identify likely risk areas.
- Review a diff, commit, pull request patch, log, or command output.

### Change and create software

- Edit existing files with targeted changes.
- Create scripts, modules, tests, documentation, configuration, and project scaffolding.
- Refactor incrementally while preserving the surrounding conventions.
- Generate shell, Python, JavaScript and TypeScript, C and C++, Rust, Go, SQL, HTML, and other text-based projects
  supported by Termux.
- Work in multiple repositories or branches by starting Pi in the relevant directory.

### Run and verify work

- Execute package managers, compilers, formatters, linters, test suites, migrations, and local servers through the `bash`
  tool.
- Diagnose failed commands and iterate on a fix.
- Inspect environment variables, ports, processes, Git status, and generated artifacts.
- Ask for a test plan when a complete test suite is too expensive on a phone.

### Use normal software workflows

- Initialize repositories, create branches, write commits, inspect history, and prepare release notes.
- Review changes before committing; let Git remain the source of truth.
- Work over SSH with a remote computer, VPS, or Git host.
- Use `tmux` so the terminal workspace survives UI interruptions.
- Keep a session per project and resume it later with `pi --continue` or `pi --resume`.

## Pi modes that are especially useful on a phone

```sh
# Interactive coding session
pi

# Continue the latest session for this directory
pi --continue

# Open the session selector
pi --resume

# One-shot repository summary
pi --print 'Summarize this repository and identify the three best next tasks'

# Feed a diff to a non-interactive review
git diff | pi --print 'Review this diff for correctness, security, and missing tests'

# Machine-readable events for scripts and logging
pi --mode json 'Run a lightweight project health check' > pi-events.jsonl

# Restrict the tool set for a narrow task
pi --tools read,grep,find,ls --print 'Review this project'

# Include a file in the first prompt
pi '@README.md' 'Suggest improvements while preserving the project voice'
```

On a narrow screen, `--print` is useful for short tasks and shell pipelines; interactive mode is better for iterative
edits. JSON mode is useful for automation, while RPC mode and the TypeScript SDK can turn Pi into a component of another
Termux application.

Two more flags worth knowing on a phone: `pi --offline` disables automatic network activity such as model-catalog
refreshes, and `pi --export` writes a session to HTML.

## Make Pi Android-aware

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

Run `/reload` after changing the file during an active session. This lets Pi remember the environment without repeating
it in every prompt. Project-local `AGENTS.md` files can describe build commands, conventions, and safety boundaries for
individual repositories.

Pi also reads a global `~/.pi/agent/settings.json` and a project `.pi/` directory, and it discovers `AGENTS.md` and
`CLAUDE.md` files. Project-local resources are trust-gated: see [`security.md`](security.md).

## Extend Pi into a mobile development platform

Pi is deliberately extensible. On Termux, this opens several playgrounds:

- **Skills:** reusable task knowledge such as Android builds, SQLite analysis, release checklists, or media workflows. A
  skill can include scripts and reference files.
- **Prompt templates:** repeatable prompts for code review, debugging, changelog generation, or repository onboarding.
- **Extensions:** TypeScript modules that add custom tools, slash commands, keyboard shortcuts, approval gates, status
  widgets, session state, event hooks, or custom UI.
- **Packages:** share extensions, skills, prompts, and themes through npm or Git.
- **MCP servers:** connect trusted external tools and data sources, such as a local database, documentation search,
  browser automation, or a personal service.
- **Codemode:** run JavaScript that orchestrates multiple tools, filters large command output, and performs parallel
  inspection.
- **RPC and SDK:** build a Termux dashboard, a notification-driven assistant, a local web UI, a scheduled code-review
  job, or another application that controls Pi programmatically.
- **Custom providers and models:** connect compatible remote or local model endpoints when the device and provider
  support them.

Codemode and tool search are off by default. Enable them per run with `pi --tools +codemode`, or for every session in
`~/.pi/agent/settings.json`:

```json
{
  "defaultTools": ["+codemode"]
}
```

A phone-friendly extension could, for example, ask for confirmation before touching shared storage, create a Git
checkpoint before edits, show battery status, open a URL through Android, or block dangerous commands. Extensions run
with Pi's operating-system permissions, so review code and packages before loading them.

## Pi plus Termux project ideas

1. **Repository doctor:** inspect Git status, dependency manifests, tests, disk space, and recent failures; print a
   compact report.
2. **Guided coding tutor:** a project-local skill that explains each command and requires the user to approve edits.
3. **Mobile issue triage:** turn copied issue text into reproduction steps, candidate files, and a test checklist.
4. **Android script builder:** describe a notification, clipboard, backup, or media workflow and have Pi create a safe
   Termux script.
5. **Commit companion:** summarize staged changes, detect secrets, suggest a commit message, and refuse to commit without
   confirmation.
6. **Local service operator:** start a server in `tmux`, inspect logs, run health checks, and explain failures.
7. **Learning lab generator:** ask for a topic and have Pi create a small repository with exercises, tests, and
   progressive hints.
8. **Remote development bridge:** use Termux as the mobile front end while SSH commands and heavy builds run on a more
   powerful machine.
9. **Session-to-documentation pipeline:** export a session, extract decisions, and update project notes or a changelog.
10. **Personal automation assistant:** combine Pi's reasoning with shell scripts and Termux:API, while keeping
    destructive actions behind explicit approval.

## What Pi cannot overcome on Android

Pi can only do what the Termux process and Android permissions allow. It cannot grant root, bypass Android sandboxing,
guarantee background execution, turn a phone into an always-on server, or make desktop Linux binaries compatible with
Android. It also cannot reliably perform visual Android UI automation without additional tooling. Large builds, huge
repositories, long context windows, and local model inference may be limited by RAM, storage, heat, battery, and network
quality.

Pi also ships **no permission system of its own**. Every tool call runs with the full permissions of the Termux process,
so a command that would need confirmation on a desktop will simply run. Approval gates are something you build with an
extension, not something Pi provides.

Treat model output as proposed work: inspect the diff, run tests, protect secrets, and confirm commands that delete
files, modify shared storage, publish code, change infrastructure, or spend money.

## Pi workflows worth building

Pi is most useful when surrounded by small, explicit workflows rather than treated as an unrestricted command executor:

- Put project conventions, build commands, test commands, and boundaries in `AGENTS.md`.
- Use skills for repeatable domain procedures and prompt templates for recurring requests.
- Use extensions for confirmation gates, Git checkpoints, secret protection, Android notifications, and project
  dashboards.
- Use MCP only for trusted integrations, with the smallest useful tool exposure.
- Use `--print` for one-shot reports, JSON mode for scripts, RPC and the SDK for applications, and sessions for iterative
  work.
- Have Pi explain a proposed change, make the smallest edit, run focused tests, then review the diff before committing.
- Export or summarize long sessions into project notes so important decisions do not remain trapped in chat history.

A useful mobile pattern is: **inspect, propose, approve, edit, test, review, commit**.

## Further reading

- [Pi documentation](https://pi.dev/docs/latest)
- [Command line reference](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/cli.md)
- [Sessions and context](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sessions.md)
- [Security and project trust](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/security.md)
- [MCP servers and tool exposure](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/mcp.md)
- [Extensions](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)
- [Codemode](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/codemode.md)
- [Pi on Termux](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/termux.md)
