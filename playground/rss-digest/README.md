# rss-digest

Fetch RSS or Atom feeds with the Python standard library and render a
plain-text digest. Feeds are cached on disk, so a second run works without a
network.

## Goal

Build a small reader that turns a handful of feeds into one text file you can
read in the terminal or open in any Android text editor. The point is to see
how a feed is fetched, cached, parsed, and rendered without any third-party
package.

## Skill taught

Reading XML with `xml.etree.ElementTree` and handling the two shapes that
matter: RSS 2.0 (`<rss><channel><item>`) and Atom (`<feed><entry>`), which
differ in tag names and in how a link is stored. You also get a practical
pattern for a cache that degrades to "last known copy" when the network is
gone.

## Time

30 minutes.

## Difficulty

Beginner to intermediate. The parsing is short; the interesting part is the
fallback behaviour when a feed fails to load.

## Setup

```sh
pkg update && pkg upgrade
pkg install python
```

No add-on application is required. No `pip install`, no `requirements.txt`.

The tool needs a feed list. Create one:

```sh
mkdir -p "$HOME/.config/rss-digest"
cat > "$HOME/.config/rss-digest/feeds.txt" <<'EOF'
# one feed per line, optionally "Name <url>"
Example Blog <https://example.com/feed.xml>
EOF
```

Run the tests (they use a local server on 127.0.0.1, not the internet):

```sh
cd playground/rss-digest
bash tests/run.sh
```

## Usage

```sh
# Render a digest from the configured feed file and write it to disk
bin/rss-digest

# Print without writing any file at all
bin/rss-digest --dry-run

# Fetch feeds given on the command line
bin/rss-digest --dry-run "Example <https://example.com/feed.xml>"

# Titles only, for a narrow screen
bin/rss-digest --brief

# Read only the cache; no network requests at all
bin/rss-digest --offline

# Change where the digest and the cache are written
bin/rss-digest --output "$HOME/digest.txt" --cache "$HOME/feeds.json"

# Fewer entries per feed
bin/rss-digest --limit 5
```

Useful environment variables:

```sh
export RSS_FEEDS_FILE="$HOME/.config/rss-digest/feeds.txt"
export RSS_DIGEST_OUT="$HOME/.local/share/rss-digest/digest.txt"
export RSS_CACHE_FILE="$HOME/.cache/rss-digest/feeds.json"
```

## Phone caveats

- **Screen width.** A digest with ten entries per feed is longer than a phone
  screen. Use `--brief` and `--limit 5`.
- **Network.** Mobile networks drop and stall. The default timeout is 20
  seconds per feed; lower it with `--timeout 8`. A failed feed falls back to
  the cached copy and prints a short error line, so one broken feed does not
  sink the whole digest.
- **Background execution.** `termux-job-scheduler` can run this daily, but
  Android decides when. A delayed run is normal, not a bug.
- **Storage.** The cache grows with the number of feeds and entries. It is a
  few kilobytes per feed.
- **Termux:API** is not needed. If you want the digest as a phone notification
  instead of a file, that is a separate experiment.

## Cleanup

```sh
rm -rf "$HOME/.cache/rss-digest" "$HOME/.local/share/rss-digest"
rm -f "$HOME/.config/rss-digest/feeds.txt"
```

Nothing is written outside your home directory.

## Safety notes

- Only reads URLs you configure, over http and https.
- Never deletes anything. The digest and cache are overwritten in place using
  a temporary file plus `mv`, so an interrupted run cannot leave a truncated
  file.
- `--dry-run` touches no files at all.
- No root, no system paths, no privileged ports. The test suite binds only to
  `127.0.0.1`.
- Feeds are fetched with a plain `urllib` request and a descriptive user
  agent; no cookies, no credentials.

## Sample output

```console
$ bin/rss-digest --dry-run --limit 2
rss-digest 2026-03-14 09:12

== Example Blog
   2026-03-14  A small release
       Fixed a crash on startup.
       https://example.com/posts/small-release
   2026-03-12  Working from a phone
       Notes on using a terminal on Android.
       https://example.com/posts/working-from-a-phone

$ bin/rss-digest
rss-digest 2026-03-14 09:12

== Example Blog
   2026-03-14  A small release
       Fixed a crash on startup.
       https://example.com/posts/small-release
   2026-03-12  Working from a phone
       Notes on using a terminal on Android.
       https://example.com/posts/working-from-a-phone

digest written to /data/data/com.termux/files/home/.local/share/rss-digest/digest.txt
```

When a feed cannot be reached, the output says so and still shows the cached
entries:

```console
== Example Blog
   ! network error: <urlopen error timed out>
   2026-03-12  Working from a phone
```

## Layout

```text
README.md       purpose, setup, usage, limitations
bin/            executable commands
src/            implementation
tests/          checks and sample data
.env.example    names of configuration values, never secrets
```
