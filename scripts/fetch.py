##this is the file for fetching my recent played songs.

#start with python libraries, as usuall drill.
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# reads .env into os.environ. without this the credentials are nowhere to be found.
load_dotenv()

#adding the paths without hard coding.. parent..
REPO_ROOT = Path(__file__).resolve().parent.parent

#raw json path once i fetch thats where it will be save
RAW_DIR = REPO_ROOT/"data"/"raw"/"recently_played"
CACHE_PATH = REPO_ROOT/".cache"/"spotify_token.json"

#permission spotify recent-played in the first batch is 50, top-read= my number ones.. lib-read the songs I saved..
SCOPES = "user-read-recently-played user-top-read user-library-read"

#define get client to spotip handles whole oauth

def get_client()-> spotipy.Spotify:
    #1. run will open a tab-browser after token cache makes it silent.. very smart of me..
    CACHE_PATH.parent.mkdir(exist_ok=True)
    auth = SpotifyOAuth(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIFY_REDIRECT_URI"],
        scope=SCOPES,
        cache_path=str(CACHE_PATH),
    )

    return spotipy.Spotify(auth_manager=auth)

#after recent 50 song added this as first
# small helper, every fetcher dumps raw json with a utc timestamp.
def save_json(data: dict, subfolder: str) -> Path:
    out_dir = REPO_ROOT / "data" / "raw" / subfolder
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"{timestamp}.json"
    out_path.write_text(json.dumps(data, indent=2))
    return out_path

    
def main() -> None:
    # make sure the folder exists, then go ask spotify for last 50 plays
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    sp = get_client()
    response = sp.current_user_recently_played(limit=50)

    #save raw json with a utc timestamp filename. raw on purpose will re-shape later, don't lose info now
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = RAW_DIR / f"{timestamp}.json"
    out_path.write_text(json.dumps(response, indent=2))
    print(f"saved {len(response['items'])} plays → {out_path.relative_to(REPO_ROOT)}")





# to fire the main lets call the file directly
if __name__ == "__main__":
    main()