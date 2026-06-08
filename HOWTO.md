# how i got spotify data into my repo (a future-me how-to guide)

Past me did this so future me doesn't have to figure it out again. Or so anyone who clones this repo can do it themselves. (charity work, like the synthetic data thing I mentioned in the README.)

Here's the order I actually did things in. Not the order it tells you in tutorials. The real one with the bugs and the confusion. Dummy-edition explanations included so future-me doesn't have to google what `if __name__ == "__main__"` means for the 400th time.

---

## 1. create a spotify developer app

Need this to get a client id + client secret. Without them, spotify just laughs at your API calls.

1. go to **developer.spotify.com** and log in with your normal spotify account (the one you actually listen on, not some throwaway).
2. top-right → profile → **Dashboard**. Or shortcut: developer.spotify.com/dashboard.
3. first time → accept the developer terms.
4. click **Create app** (top-right of the dashboard).
5. fill in:
   - **App name**: `ask-my-spotify`
   - **App description**: anything — `Personal RAG over my listening history`
   - **Website**: leave blank
   - **Redirect URIs**: `http://127.0.0.1:8888/callback` → **click Add** (if you don't click Add it doesn't save. ask me how i know.)
   - **APIs/SDKs**: tick **Web API** only
6. tick the terms box → **Save**.

Now you have an app. Click it → top-right **Settings** → there's your **Client ID** and (behind "View client secret") your **Client secret**.

> heads up: that long `BQD...` string everywhere in spotify's JS docs is an **access token**, not your client secret. It expires every hour. Ignore it. It's just an example.

---

## 2. drop credentials into .env

In the repo root, make a `.env` file (gitignored, never commit this thing):

```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

The redirect URI **must match what you typed in the dashboard, byte for byte**. `http` vs `https`, `127.0.0.1` vs `localhost`, trailing slash — all matter. Number one cause of "invalid redirect uri" errors.

Also make `.env.example` with placeholder values and commit *that* so future me knows what variables to set.

### dummy edition: what is a `.env` file anyway?

It's just a text file with `KEY=value` lines. Tools (and the `python-dotenv` library) read it and load those keys as **environment variables** — values that live in the shell/process and are accessible from code via `os.environ["KEY"]`. We use it to keep secrets out of the actual python files, so we don't accidentally commit them to github.

---

## 3. venv + install dependencies

Yes **pip**, not brew. (I keep wanting to brew install everything.)

```bash
cd ~/Desktop/ds-projects/ask-my-spotify
python3 -m venv .venv
source .venv/bin/activate    # prompt now shows (.venv)
pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` for v1 is just two lines:
```
spotipy>=2.23.0
python-dotenv>=1.0.0
```

### dummy edition: what's a venv?

A **venv** (virtual environment) is a per-project folder of installed packages. Without it, `pip install` puts everything into your system python and projects start fighting over versions ("project A wants pandas 1.5, project B wants pandas 2.0..."). With a venv, each project has its own isolated python + its own packages. You activate it with `source .venv/bin/activate` and your shell uses that python until you `deactivate`.

### dummy edition: what these two deps do
- **`spotipy`** — third-party library. A python wrapper around spotify's web api. Without it I'd have to write raw HTTP requests and do the whole OAuth dance by hand. With it, calling spotify is one method call like `sp.current_user_recently_played(limit=50)`.
- **`python-dotenv`** — third-party library. One purpose: read `.env` and stuff the keys into `os.environ` so the rest of the code can find them.

---

## 4. first fetch — just recently played

Write `scripts/fetch.py`. Start small, one endpoint, prove it works end-to-end before adding more.

```python
import json, os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT/"data"/"raw"/"recently_played"
CACHE_PATH = REPO_ROOT/".cache"/"spotify_token.json"

SCOPES = "user-read-recently-played"

def get_client():
    CACHE_PATH.parent.mkdir(exist_ok=True)
    auth = SpotifyOAuth(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIFY_REDIRECT_URI"],
        scope=SCOPES,
        cache_path=str(CACHE_PATH),
    )
    return spotipy.Spotify(auth_manager=auth)

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    sp = get_client()
    response = sp.current_user_recently_played(limit=50)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = RAW_DIR / f"{timestamp}.json"
    out_path.write_text(json.dumps(response, indent=2))
    print(f"saved {len(response['items'])} plays → {out_path.relative_to(REPO_ROOT)}")

if __name__ == "__main__":
    main()
```

### dummy edition: what each import is for
- **`json`** — stdlib (built into python, no install). Converts python dicts ↔ json text. We use `json.dumps(x, indent=2)` to turn a dict into pretty json text for saving.
- **`os`** — stdlib. Lets us reach into the operating system. We use it for `os.environ["KEY"]` to read environment variables.
- **`datetime`, `timezone`** — stdlib. For building UTC timestamps for filenames so they sort chronologically.
- **`Path` from `pathlib`** — stdlib. File paths as objects, way nicer than gluing strings together. `Path("a") / "b" / "c.json"` just works on mac/linux/windows.
- **`load_dotenv` from `dotenv`** — third-party. Reads `.env` and shoves the keys into `os.environ`.
- **`spotipy`** + **`SpotifyOAuth`** — third-party. The spotify client itself + the helper that handles the OAuth dance.

### dummy edition: import syntax cheatsheet
- `import json` — pull in the whole module, call stuff as `json.dumps(...)`.
- `from dotenv import load_dotenv` — pull in just one specific thing, call it directly as `load_dotenv()`.
- `from datetime import datetime, timezone` — pull in two specific things from the same module in one line.

### dummy edition: anatomy of a function

```python
def get_client() -> spotipy.Spotify:
    auth = SpotifyOAuth(...)
    return spotipy.Spotify(auth_manager=auth)
```

- **`def`** = "define" — we're making a function.
- **`get_client`** = the function's name (we'll call it later as `get_client()`).
- **`()`** = parameters list (none here — function takes no inputs).
- **`-> spotipy.Spotify`** = a *type hint* — tells humans + tools "this function gives back a `spotipy.Spotify` object". Python doesn't enforce it. It's just documentation.
- **`:`** starts the function body. Everything indented after this is "inside" the function.
- **`return ...`** = hand back this value when called. If you don't `return` anything, python returns `None`.

### dummy edition: what's `def main()` and `if __name__ == "__main__"`?

- **`def main():`** — just a convention. There's nothing magic about the name `main`. Everyone uses it as "the function that runs when this script runs", so when you open someone's file you know exactly where to start reading.
- **`if __name__ == "__main__":`** — every python file has a built-in variable `__name__`. When you run the file directly (`python scripts/fetch.py`), `__name__` is automatically set to the string `"__main__"`. When the file is *imported* by another file, `__name__` is set to the module name instead. So this `if` block means: "only run this code if i was called directly, not if i was imported by something else". Standard pattern, you'll see it in 99% of python scripts.

### dummy edition: the constants at the top
- **`REPO_ROOT = Path(__file__).resolve().parent.parent`** — `__file__` is a built-in variable holding the path of the current `.py` file. `.resolve()` makes it absolute. `.parent` goes up one folder (from `scripts/fetch.py` to `scripts/`). Two `.parent`s = repo root. This means the script works no matter where you run it from.
- **`SCOPES = "user-read-recently-played"`** — a space-separated string of permissions we ask spotify for. Asking for fewer = smaller blast radius if a token ever leaks + less scary consent screen for the user.

### running it

```bash
python scripts/fetch.py
```

First run pops a browser tab → spotify login → "Agree" → page redirects to `http://127.0.0.1:8888/callback?code=...` which shows **"site can't be reached"**. **This is fine.** spotipy reads that URL. After this it saves a token to `.cache/spotify_token.json` and never bothers you again.

Terminal printed:
```
saved 50 plays → data/raw/recently_played/20260608T231315Z.json
```

50 plays. Hard cap, can't ask for more in one call. That's a spotify thing — there is literally no endpoint that gives you "every play ever". For that I need the extended export (see section 10).

---

## 5. bugs I hit (so future me doesn't repeat them)

Both were in `get_client()`, both stopped the script from even starting:

**1. missing comma after the first argument**
```python
client_id=os.environ["SPOTIFY_CLIENT_ID"]        # ← FORGOT THE COMMA
client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
```
SyntaxError. Python tries to read two lines as one expression.

**2. wrong capitalization**
```python
Client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],   # ← capital C
```
TypeError: unexpected keyword argument. Spotipy's param is lowercase `client_secret`. Case matters.

Lesson: read the diff one more time before running. Also: a linter would have caught both of these in 0.3 seconds.

---

## 6. comment the code while it's fresh

After the first run worked, I went back and added comments in the file. Not "this line does X" comments (the code already says that), but **why** comments — why save raw, why this folder structure, why this scope list. Future-me will thank current-me.

Style I'm using:
- lowercase, casual, `..` for trailing thoughts
- explain the gotcha, not the syntax
- one-liners over paragraphs

Example:
```python
#last 50 plays. rolling window, so we run this often.
def fetch_recently_played(sp):
    ...
```

---

## 7. add the rest of the fetchers

One file, one cron job, four endpoints. The auth client is shared so it's cheap to bundle.

First — pull the save logic into one tiny helper so it's not copy-pasted four times:
```python
def save_json(data: dict, subfolder: str) -> Path:
    out_dir = REPO_ROOT / "data" / "raw" / subfolder
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"{timestamp}.json"
    out_path.write_text(json.dumps(data, indent=2))
    return out_path
```

Then the three new fetchers:
```python
def fetch_recently_played(sp):
    response = sp.current_user_recently_played(limit=50)
    save_json(response, "recently_played")

def fetch_top_tracks(sp):
    for tr in ("short_term", "medium_term", "long_term"):
        response = sp.current_user_top_tracks(limit=50, time_range=tr)
        save_json(response, f"top_tracks/{tr}")

def fetch_top_artists(sp):
    for tr in ("short_term", "medium_term", "long_term"):
        response = sp.current_user_top_artists(limit=50, time_range=tr)
        save_json(response, f"top_artists/{tr}")
```

### dummy edition: what `def save_json(data: dict, subfolder: str) -> Path:` means
- `data: dict` — first parameter named `data`, expected to be a dict (type hint, not enforced).
- `subfolder: str` — second parameter named `subfolder`, expected to be a string.
- `-> Path` — returns a `Path` object.

So this function takes a dict + a subfolder name, writes the dict to a json file in `data/raw/<subfolder>/<timestamp>.json`, and returns the path. Used by all four fetchers below.

### time ranges per spotify
- `short_term` = last ~4 weeks
- `medium_term` = last ~6 months
- `long_term` = years

### updated scopes (we need more now)
```python
SCOPES = "user-read-recently-played user-top-read user-library-read"
```

> ⚠️ if you changed scopes AFTER the first auth, the cached token doesn't have the new ones. Delete `.cache/spotify_token.json` and run again to re-auth. Otherwise some endpoints 403. Ask me how i know (again).

---

## 8. saved tracks — paginated + a jan 1 filter

Saved tracks (= liked songs) is the one endpoint that actually gives real timestamps (`added_at`). It also paginates because people have thousands of likes. And spotify returns it **newest first**, which means I can stop paginating early once I hit anything older than my cutoff.

Cutoff at the top of the file:
```python
SAVED_TRACKS_SINCE = datetime(2026, 1, 1, tzinfo=timezone.utc)
```

```python
def fetch_saved_tracks(sp):
    all_items = []
    response = sp.current_user_saved_tracks(limit=50)
    while True:
        for item in response["items"]:
            added_at = datetime.fromisoformat(item["added_at"].replace("Z", "+00:00"))
            if added_at < SAVED_TRACKS_SINCE:
                payload = {"items": all_items, "total": len(all_items),
                           "since": SAVED_TRACKS_SINCE.isoformat()}
                save_json(payload, "saved_tracks")
                return
            all_items.append(item)
        if not response["next"]:
            break
        response = sp.next(response)
    payload = {"items": all_items, "total": len(all_items),
               "since": SAVED_TRACKS_SINCE.isoformat()}
    save_json(payload, "saved_tracks")
```

### dummy edition: what's `while True:` doing?

`while True` means "loop forever, until something inside the loop says stop". Two ways out:
- `return` — exit the whole function (used here when we hit an item older than the cutoff).
- `break` — exit just the loop, but keep going in the function (used here when there are no more pages).

It looks scarier than it is. It's just "keep going until done".

### dummy edition: what's `response["next"]`?

The spotify API returns a dict like `{"items": [...], "next": "https://..." or None, ...}`. The `"next"` key holds the URL of the next page, or `None` if there are no more pages. spotipy's `sp.next(response)` follows that URL for you and returns the next page.

> ⚠️ this filter is on WHEN I LIKED a song, NOT when I played it. The saved-tracks endpoint has no idea about play history. For per-play data → wait for the extended export.

`main()` becomes:
```python
def main():
    sp = get_client()
    fetch_recently_played(sp)
    fetch_top_tracks(sp)
    fetch_top_artists(sp)
    fetch_saved_tracks(sp)
```

Run it → 8 prints, 8 JSON files saved into `data/raw/<endpoint>/<timestamp>.json`.

---

## 9. data layout after one full run

```
data/raw/
├── recently_played/<timestamp>.json
├── top_tracks/{short,medium,long}_term/<timestamp>.json
├── top_artists/{short,medium,long}_term/<timestamp>.json
└── saved_tracks/<timestamp>.json
```

Every file is the raw API response (with `"since"` added for saved_tracks). On purpose — re-shape later, don't lose info now. If I want a new column tomorrow it's probably already in there.

---

## 10. what's actually inside these JSON files (the entities)

All four endpoints share a handful of building blocks. Once you know these, the JSON everywhere starts looking familiar.

### the building blocks

**track** — a song. Same shape whether it comes from recently_played, top_tracks, or saved_tracks.
- `id` — spotify's unique track id (use for joins/dedupe later)
- `name` — song title
- `duration_ms` — length in milliseconds
- `popularity` — 0–100, how hot the track is on spotify right now
- `explicit` — true/false
- `uri` — `spotify:track:...`, opens the song in spotify
- `artists` — a **list** (collabs have multiple, hence list)
- `album` — the album object (below)

**artist** — a person/group. Same shape inside `track.artists` and as a top-level item in `top_artists`.
- `id`, `name`, `uri` — the basics, always there
- `genres` — list of genre strings (only present in `top_artists`, not inside `track.artists`)
- `popularity`, `followers.total` — only in `top_artists`
- `images` — list of artist pic URLs in different sizes

**album** — what a track belongs to.
- `id`, `name`, `uri`
- `release_date` — when the album dropped (e.g. `"2020-03-20"`)
- `images` — list of cover art URLs, usually 3 sizes (640, 300, 64 px)
- `album_type` — `"album"` / `"single"` / `"compilation"`

### the per-endpoint extras

**recently_played items** wrap a track with:
- `played_at` — UTC timestamp of when YOU played it (gold mine for time-based questions like "what time of day do I listen most?")
- `context` — what you were playing FROM. Either `null` (shuffle / standalone single) or an object with `type` (`"playlist"`, `"album"`, `"artist"`) and `uri`.

**top_tracks / top_artists items** are just the track / artist objects themselves. No wrapper.

**saved_tracks items** wrap a track with:
- `added_at` — UTC timestamp of when YOU liked it (this is what the Jan 1 filter uses)
- `track` — the track object

### the pagination wrapper (every response has this)

The whole response is one big dict with:
- `items` — the actual list of stuff you wanted
- `next` — URL of the next page (or `null` if last page) — spotipy's `sp.next(response)` follows this for you
- `total` — total count available (present in top_* and saved_tracks)
- `limit`, `offset`, `href` — paging metadata

### mental model

Think russian doll:
- **the response** has `items` →
- **each item** is either a track/artist directly, OR a wrapper like `{played_at, track, context}` / `{added_at, track}` →
- **a track** has `artists[]` and `album` nested inside →
- **an album** has `images[]` →
- timestamps are always UTC ISO 8601 (e.g. `"2026-03-04T10:23:45Z"` — the `Z` means UTC).

### a tiny real-shaped example (one recently_played item, trimmed)

```json
{
  "played_at": "2026-06-08T22:30:15.123Z",
  "context": {"type": "playlist", "uri": "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"},
  "track": {
    "id": "0VjIjW4GlUZAMYd2vXMi3b",
    "name": "Blinding Lights",
    "duration_ms": 200040,
    "popularity": 89,
    "explicit": false,
    "uri": "spotify:track:0VjIjW4GlUZAMYd2vXMi3b",
    "artists": [
      {"id": "1Xyo4u8uXC1ZmMpatF05PJ", "name": "The Weeknd"}
    ],
    "album": {
      "name": "After Hours",
      "release_date": "2020-03-20",
      "album_type": "album",
      "images": [{"url": "https://i.scdn.co/...", "height": 640, "width": 640}]
    }
  }
}
```

### what i'll probably actually use later

When I get to chunking, the useful fields are:
- `track.name` + `artists[].name` → for the text content of a chunk
- `played_at` or `added_at` → for time-based metadata filters
- `track.id` → for dedupe + joins back to the raw data
- `album.release_date`, `track.popularity` → maybe useful as filters ("songs from 2010s", "deep cuts only")
- `context.type` → "playlist vs album vs shuffle" listening patterns

Everything else I'll ignore for v1. It's there if I want it later.

---

## 11. what spotify will NOT let me do (annoying truths)

- **No "give me everything since Jan 1" for plays.** `recently_played` is a hard 50-track rolling window. The Jan→June data is gone unless I was already polling. Brutal.
- **No audio features for new apps.** Spotify deprecated `/audio-features` and `/audio-analysis` for apps created after Nov 2024. Tempo/energy/valence are off the menu via the Web API. Will need to come from the extended export or another source.
- **Top tracks "medium_term" ≈ last 6 months**, not strictly Jan→now. Closest proxy I have until the export arrives.

---

## 12. what i still need to do (tomorrow-me's problem)

- **cron** the fetch script every ~4 hours so recently_played doesn't lose data between runs.
- **request the extended streaming history** from spotify.com/account/privacy → Extended streaming history → takes up to 30 days but it's the only real Jan→now per-play source.
- **first notebook** in `notebooks/` — load the JSON into pandas, sniff at the shape, gut-check before chunking.

---

## tldr commands

```bash
source .venv/bin/activate
python scripts/fetch.py
```

That's it. Two lines for a daily refresh until cron is set up.
