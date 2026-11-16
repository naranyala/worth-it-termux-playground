# Contributing

This repository is a catalog of phone-sized experiments plus the code for a few of them. Contributions are welcome, and
the bar is deliberately about usefulness rather than polish.

## What an experiment needs

Every entry in the catalog, and every experiment in `playground/`, answers the same questions:

- **What is it?** One sentence, concrete.
- **What skill does it teach?** Something that transfers to the next project.
- **How long does it take?** Realistically, for one sitting.
- **How hard is it?** Easy, Medium, or Hard.
- **How do I set it up?** Exact `pkg install` commands.
- **How do I use it?** At least one real example.
- **What breaks on a phone?** Battery, screen width, background kills, shared storage permissions.
- **How do I undo it?** A cleanup command that removes everything it created.

## What a code contribution needs

- Python code uses the standard library only. No `pip install`, no `requirements.txt`.
- Shell code is POSIX `sh` or bash, passes `bash -n`, and supports `--help`.
- Scripts are idempotent, safe to interrupt with Ctrl-C, and never delete anything.
- Destructive work is opt-in: `--dry-run` by default, `--apply` to commit changes.
- Writes go to a temporary file and are moved into place, so an interrupted run cannot corrupt state.
- Tests run with `python3 -m unittest` or a plain shell test script. No pytest.
- Everything lives under `$HOME`. No system paths, no root, no privileged ports.

Start from `templates/experiment/`:

```sh
cp -r templates/experiment playground/my-experiment
```

Fill in every section of the template README, then register the experiment in `playground/INDEX.md` and, if it belongs in
the catalog, in `docs/catalog.md`.

## Documentation contributions

- Verify claims about packages, flags, and paths against upstream before writing them. The Pi CLI and the Termux
  package set both change often.
- Keep the tone: calm, concrete, honest about limits. No hype, no emoji beyond the `★` marker.
- Prefer narrow, declarative sentences. Short sentences translate well and scan well on a phone.
- Every new external link must resolve. CI checks this.

## Checks

```sh
python3 scripts/check-snippets.py     # shell blocks in the docs parse
python3 scripts/check-upstream.py      # Pi CLI flags and Termux Node packaging
```

CI also runs a link checker and a Markdown linter. All of them must pass.

## Pull requests

- One experiment or one documentation topic per pull request.
- Say how you tested it, and on which device and Termux version if you tested on hardware.
- If you changed a claim that was previously verified upstream, mention the source.
