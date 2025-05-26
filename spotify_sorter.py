import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import time
import argparse
from datetime import datetime

# Set up authentication
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI', 'http://localhost:8888/callback')

# Set up cache path
cache_path = os.path.join(os.getcwd(), '.cache-spotify')

# Initialize Spotify client with necessary permissions
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="playlist-modify-public playlist-modify-private playlist-read-private",
    cache_path=cache_path
))

def handle_rate_limit(retries=5, initial_delay=60):
    """Much longer initial delay and exponential backoff"""
    for i in range(retries):
        delay = initial_delay * (2 ** i)  # This will give 60s, 120s, 240s, 480s, 960s
        print(f"Rate limit reached. Waiting {delay} seconds before retrying...")
        time.sleep(delay)
        return True
    return False

def apply_artist_spacing(tracks, min_spacing=5):
    """Reorder tracks to maintain minimum spacing between same artist while preserving popularity order"""
    final_tracks = []
    available_tracks = tracks.copy()
    artist_last_position = {}

    while available_tracks:
        current_position = len(final_tracks)
        # Find tracks that maintain the minimum artist spacing
        valid_tracks = [
            track for track in available_tracks
            if track['artist'] not in artist_last_position or 
            (current_position - artist_last_position[track['artist']]) > min_spacing
        ]

        if not valid_tracks:
            # If no valid tracks available, take the next available track
            track = available_tracks[0]
        else:
            # Take the highest popularity valid track
            track = max(valid_tracks, key=lambda x: x['popularity'])

        final_tracks.append(track)
        available_tracks.remove(track)
        artist_last_position[track['artist']] = current_position

    return final_tracks

def sort_single_playlist(playlist_id):
    try:
        spotify_tracks = []
        local_tracks = []
        offset = 0
        
        # Get all tracks with their details
        while True:
            try:
                time.sleep(5)
                results = sp.playlist_tracks(playlist_id, offset=offset, limit=20)
                
                for position, item in enumerate(results['items'], start=offset):
                    if item['track']:
                        if item['track'].get('is_local', False):
                            # Store local track with its position
                            local_tracks.append({
                                'position': position,
                                'name': item['track'].get('name', 'Unknown Local Track'),
                                'is_local': True
                            })
                        elif item['track'].get('uri'):
                            # Store Spotify track with all needed info
                            spotify_tracks.append({
                                'uri': item['track']['uri'],
                                'popularity': item['track']['popularity'],
                                'artist': item['track']['artists'][0]['name'],
                                'name': item['track']['name']
                            })
                
                if not results['next']:
                    break
                    
                offset += 20
                time.sleep(10)
                
            except spotipy.exceptions.SpotifyException as e:
                if e.http_status == 429:
                    if not handle_rate_limit():
                        raise
                    continue
                raise

        print(f"Successfully retrieved {len(spotify_tracks)} Spotify tracks and {len(local_tracks)} local tracks")
        time.sleep(30)

        # Sort and space out Spotify tracks
        valid_tracks = [track for track in spotify_tracks if 'spotify:track:' in track['uri']]
        sorted_tracks = sorted(valid_tracks, key=lambda x: x['popularity'], reverse=True)
        sorted_tracks = sorted_tracks[:500]
        
        # Apply artist spacing to sorted tracks
        spaced_tracks = apply_artist_spacing(sorted_tracks)
        
        # Get URIs maintaining the new order
        track_uris = [track['uri'] for track in spaced_tracks]

        # Process in chunks
        chunk_size = 10
        for i in range(0, len(track_uris), chunk_size):
            chunk = track_uris[i:i + chunk_size]
            retry_count = 0
            while retry_count < 3:
                try:
                    if i == 0:
                        sp.playlist_replace_items(playlist_id, chunk)
                    else:
                        sp.playlist_add_items(playlist_id, chunk)
                    print(f"Processed tracks {i+1} to {i+len(chunk)}")
                    time.sleep(15)
                    break
                except spotipy.exceptions.SpotifyException as e:
                    if e.http_status == 429:
                        if handle_rate_limit():
                            retry_count += 1
                            continue
                        raise
                    elif e.http_status == 400:
                        print(f"Skipping invalid tracks in chunk starting at {i+1}")
                        break
                    raise

        # Print summary of changes
        print(f"\nPlaylist updated with:")
        print(f"- {len(spaced_tracks)} Spotify tracks (sorted by popularity with artist spacing)")
        print(f"- {len(local_tracks)} local tracks preserved")
        
        return True

    except Exception as e:
        print(f"Error updating playlist: {e}")
        print(f"Error details: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int, help="Year of playlist to process")
    args = parser.parse_args()

    try:
        playlists = sp.current_user_playlists()
        target_playlist = None
        
        for playlist in playlists['items']:
            if playlist['name'] == str(args.year):
                target_playlist = playlist
                break

        if target_playlist:
            print(f"Processing playlist for year {args.year}")
            success = sort_single_playlist(target_playlist['id'])
            if success:
                print(f"Successfully sorted playlist for {args.year}")
            else:
                print(f"Failed to sort playlist for {args.year}")
        else:
            print(f"No playlist found for year {args.year}")

    except Exception as e:
        print(f"Error in execution: {e}")
        print(f"Error details: {str(e)}")

if __name__ == "__main__":
    main()







