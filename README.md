# Spotify Playlist Sorter

A Python script that automatically sorts your Spotify playlists by track popularity while maintaining artist spacing to avoid clustering songs from the same artist.

---

## What it Does

- **Sorts tracks by popularity:** Reorders songs based on Spotify's popularity score (0-100).
- **Artist spacing:** Ensures a minimum 5-song gap between tracks from the same artist.
- **Preserves local files:** Keeps local tracks in their original positions.
- **Rate limit handling:** Robust error handling for Spotify API limits.
- **Year-based playlists:** Designed for playlists named by year (e.g., `2020`, `2010`).

---

## Prerequisites

- Python 3.6+ installed
- Spotify Developer Account and app credentials
- [spotipy](https://spotipy.readthedocs.io/) Python package

---

## Setup

### 1. Install Dependencies

```bash
pip install spotipy
```

### 2. Get Spotify API Credentials

- Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
- Create a new app
- Note your **Client ID** and **Client Secret**
- Add `http://localhost:8888/callback` as a redirect URI in your app settings

### 3. Update Credentials

Replace the placeholder credentials in the script:

```python
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
```

> ⚠️ **Security Note:** Never share your credentials publicly. Consider using environment variables for production use.

---

## Usage

### Windows

Open Command Prompt and run:

```sh
python spotify_sorter.py [YEAR]
```
or
```sh
py spotify_sorter.py [YEAR]
```

### macOS

Open Terminal and run:

```bash
python3 spotify_sorter.py [YEAR]
```

### Linux

Open Terminal and run:

```bash
python3 spotify_sorter.py [YEAR]
```

#### Examples (All Platforms)

```bash
# Sort playlist named "2020"
python3 spotify_sorter.py 2020

# Sort playlist named "2010"
python3 spotify_sorter.py 2010

# Sort playlist named "1995"
python3 spotify_sorter.py 1995
```

> **Note:** On Windows, use either `python` or `py`. On macOS and Linux, use `python3` to ensure Python 3.x is used.

---

## How it Works

1. **Authentication:** Connects to your Spotify account (authorization required on first run).
2. **Playlist Discovery:** Finds the playlist matching the specified year.
3. **Track Analysis:** Retrieves all tracks and their popularity scores.
4. **Sorting:** Orders tracks by popularity (highest to lowest).
5. **Artist Spacing:** Rearranges to maintain 5-song minimum spacing between same artists.
6. **Playlist Update:** Replaces the playlist content with the sorted tracks.

---

## Features

- **Chunked Processing:** Processes tracks in batches of 10 to respect API limits.
- **Rate Limit Handling:** Automatically waits and retries when hitting API limits.
- **Progress Tracking:** Shows real-time progress during processing.
- **Error Recovery:** Handles various API errors gracefully.
- **Local File Support:** Preserves local files that can't be processed via API.

---

## Limitations

- Only works with playlists named as years (numeric names).
- Limited to 500 tracks per playlist.
- Local files are preserved but not sorted.
- Requires active internet connection.
- Subject to Spotify API rate limits.

---

## Troubleshooting

- **Rate Limit Errors:** The script will automatically wait and retry.
- **Missing Playlist:** Ensure your playlist is named exactly as a year (e.g., `2020`).
- **Authentication Issues:** Delete the `.cache-spotify` file and run again.
- **Connection Errors:** Wait a few minutes and retry.
- **Python Command Not Found:**
    - **Windows:** Try `py` instead of `python`.
    - **macOS/Linux:** Try `python3` instead of `python`.

---

## Example Output

```
Processing playlist for year 2020
Successfully retrieved 215 Spotify tracks and 6 local tracks
Processed tracks 1 to 10
Processed tracks 11 to 20
...
Playlist updated with:
- 215 Spotify tracks (sorted by popularity with artist spacing)
- 6 local tracks preserved
Successfully sorted playlist for 2020
```