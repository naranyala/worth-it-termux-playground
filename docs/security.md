# Security, privacy, and trust

Termux is not a security boundary against code you voluntarily run. The same is true of every agent, extension, skill,
and package you install into it. This page describes what to check before you trust something, and what to keep out of
reach of the tools you run.

- [The trust model](#the-trust-model)
- [Third-party resources are code](#third-party-resources-are-code)
- [Pi specifics](#pi-specifics)
- [Secrets](#secrets)
- [Storage and permissions](#storage-and-permissions)
- [Networks](#networks)
- [Before approving a consequential action](#before-approving-a-consequential-action)

## The trust model

Your phone has one user, and you are it. Everything in Termux runs with the permissions of the Termux process, which
means it can read your files, use your network, and reach any Android capability you have granted to the app. There is no
privilege separation between "the agent" and "the shell", because they are the same process.

That means two rules carry most of the weight:

1. Treat model output as proposed work. Inspect the diff, run the tests, and read the commands before they run.
2. Treat every installed resource as code you are responsible for, whether it came from npm, a Git repository, a shared
   prompt file, or an MCP server.

The model is not a security reviewer. It can be wrong about the risk of a command in exactly the same way it can be wrong
about a function name.

## Third-party resources are code

Agents and their tooling can load resources that change what they do:

- `AGENTS.md` and `CLAUDE.md` files change the system instructions.
- Skills add reusable procedures, and may include scripts.
- Extensions add tools, slash commands, and event hooks that run with full process permissions.
- Prompt templates insert text into requests.
- MCP servers expose external tools and data, and can receive anything passed to them.
- npm and Git packages install code that runs during install and on every invocation.

Before trusting an unfamiliar resource:

- Read it. `AGENTS.md`, skills, extensions, and install scripts are plain text and short.
- Use project-local resources only in repositories you recognize.
- Review the diff a tool wants to apply, not just the command it wants to run.
- Prefer `pi --no-approve` in directories you do not trust: it ignores trust-gated project-local configuration.
- Install only the add-ons you need, and revoke them later.

## Pi specifics

Pi has no built-in permission system. Its tools run with the permissions of the process that started it, so a
file-editing tool or a shell command is not sandboxed and is not gated by default.

Pi does have a project-trust concept for the files it reads:

- Project-local `.pi/` resources and project `.pi/mcp.json` are only loaded for trusted projects.
- `pi --approve` trusts project-local configuration and resources for a single run.
- `pi --no-approve` ignores trust-gated project-local files, which is the safer default in a directory you just cloned.

Practical consequence: do not run an agent in an unfamiliar repository with project trust enabled, and do not install an
extension, skill, or MCP server whose source you have not read.

## Secrets

- Keep API keys and tokens in environment variables or a protected secret store, not in prompts, source files, logs, or
  Git history.
- Use separate test credentials and disposable directories for experiments.
- A prompt is a place where a secret can leak: it travels to the model provider, may be written into a session file, and
  may appear in JSON event output.
- Session files, exports, and shell history can all retain secrets. Review them before sharing a session or a log.
- Remember that shared storage is readable by other apps with storage permission.

## Storage and permissions

- Restrict shared-storage access and avoid granting more Android permissions than necessary.
- Keep working files inside `~`, where the sandbox applies.
- Review `~/.ssh`, `~/.gitconfig`, and `~/.pi` before backing them up to a repository. Never back up secrets to a public
  repository.
- If an experiment no longer needs an add-on, revoke it: `pm revoke` or the Android settings screen.

## Networks

- Use `127.0.0.1` for local services unless LAN access is deliberate and understood.
- Never expose an SSH server directly to the public internet; use a tunnel or a bastion.
- Use `nmap`, packet capture, and traffic interception only against devices and networks you own or have explicit
  permission to test.
- Never scan, exploit, brute-force, or intercept systems without authorization. A terminal is not a license.
- Remember that traffic from an agent-hosted server still carries whatever credentials you gave it.

## Before approving a consequential action

Review the diff, the command, the network destination, and the file paths before approving anything that:

- deletes or overwrites files,
- writes to shared storage,
- publishes code, pushes commits, or opens a pull request,
- changes infrastructure or sends messages on your behalf,
- installs packages or runs install scripts,
- transfers private data or spends money.

The safest workflow on a phone is the one that can be interrupted and inspected: make Pi propose a change, read it,
apply the smallest edit, run focused tests, then review the diff before committing.
