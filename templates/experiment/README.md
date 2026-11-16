# experiment-name

<!--
One-line summary of what this experiment does.
Replace every angle-bracket placeholder before opening a pull request.
-->

## Goal

<!--
What the reader will have working when they are done.
Two or three sentences. Concrete outcomes, not adjectives.
-->

## Skill taught

<!--
The one transferable thing this experiment teaches.
Name the concrete technique (for example: "writing a dry-run-first CLI in Python"
or "parsing JSON without jq"). One or two sentences.
-->

## Time

<!--
Rough time to finish: for example "20 minutes", "45 minutes", "one afternoon".
Include any waiting time separately, such as a scheduled job that runs the next morning.
-->

## Difficulty

<!--
Beginner / Intermediate / Advanced, plus one line explaining what makes it that level.
-->

## Setup

<!--
Exact commands, in order, that make the experiment run on a phone.

```sh
pkg update && pkg upgrade
pkg install python
```

List the required add-on applications (for example Termux:API) separately, and say
what happens when they are missing. Only use package names that really exist in Termux.
-->

## Usage

<!--
Exact commands with real arguments, plus the common variants.
Every command shown here must actually work.
-->

## Phone caveats

<!--
The things that will surprise someone on a narrow screen, with a background killer,
or with shared storage: screen width, battery, Android killing background work,
shared-storage permissions, thermal throttling, keyboard limitations.
-->

## Cleanup

<!--
One command, or a short list, that removes everything this experiment created.
Give the exact path that was written to.
-->

## Safety notes

<!--
What the script does and does not do: no deletes, no root, no network, loopback only.
State the boundaries honestly.
-->

## Sample output

<!--
A realistic terminal transcript, copied from a real run.
Do not invent output; run the command and paste it.
-->

## Layout

```text
README.md       purpose, setup, usage, limitations
bin/            executable commands
src/            implementation
tests/          checks and sample data
.env.example    names of configuration values, never secrets
```
