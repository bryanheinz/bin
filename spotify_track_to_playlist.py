#!/usr/bin/env python3
import getpass
import spotipy
import pathlib
from spotipy.oauth2 import CacheFileHandler, SpotifyOAuth

#
# Uses Spotipy
# https://spotipy.readthedocs.io
# https://github.com/plamere/spotipy
# https://pypi.org/project/spotipy/
# 
# Examples:
# https://github.com/plamere/spotipy/tree/master/examples
# 
# This script adds the current playing track to a Spotify playlist.
#


# Spotify playlist ID
playlist_id = ''

# Spotify dev creds
# https://developer.spotify.com/
client_id = ''
client_secret = ''

# https://spotipy.readthedocs.io/en/2.19.0/#redirect-uri
# using http, a local address, and specifying a port will spawn a webserver
# which will auto-accept the returned URI from Spotify.
# NOTE: https://127.0.0.1 needs to be added as a redirect URI on the app on the
# Spotify web developer portal.
redirect_uri = 'http://127.0.0.1:15061'

scopes = [
    'user-read-playback-state',
    'playlist-modify-public',
    'user-read-currently-playing'
]

cache_path = pathlib.Path(
    f'/Users/{getpass.getuser()}/Library/Application Support/spotipy/.cache'
)


def get_creds():
    # setup cache dir and return oauth creds
    cache_dir = cache_path.parent
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)
    # create a cache file handler
    # https://github.com/plamere/spotipy/blob/48d04f343b99014822a87d6ec4965c6c921be8ac/spotipy/oauth2.py#L338-L347
    cache_handler = CacheFileHandler(cache_path=cache_path)
    # create OAuth creds object
    oauth_creds = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scopes,
        cache_handler=cache_handler
    )
    return oauth_creds

def add_to_playlist():
    now_playing = now_playing_obj.get('is_playing')
    now_playing_type = now_playing_obj.get('currently_playing_type')
    # only add a track that is playing
    if now_playing is True and now_playing_type == 'track':
        # get a list of all track IDs in the playlist
        playlist_tracks = get_playlist_tracks()
        # get the current playing track ID
        track_id = now_playing_obj.get('item', {}).get('id')
        # validate the track isn't already in the playlist
        if track_id not in playlist_tracks:
            # add the track to the playlist
            sp.playlist_add_items(playlist_id, [track_id])

def get_playlist_tracks():
    # get all track IDs in the playlist
    playlist_tracks = []
    # get the first batch of 100 tracks in the playlist
    tracks = sp.playlist_items(
        playlist_id, fields="items(track.id),next", additional_types=['track'])
    append_track_ids(tracks, playlist_tracks)
    # if there are <100 tracks, this should immediately return with the playlist
    if tracks.get('next') is None:
        return playlist_tracks
    # there are >100 tracks, keep appending until we get them all
    while True:
        tracks = sp.next(tracks)
        append_track_ids(tracks, playlist_tracks)
        if tracks.get('next') is None: break
    return playlist_tracks

def append_track_ids(tracks, playlist_tracks):
    # loop through the tracks array and append each track ID to the array
    for track in tracks['items']:
        track_id = track['track']['id']
        playlist_tracks.append(track_id)


sp = spotipy.Spotify(oauth_manager=get_creds())
now_playing_obj = sp.currently_playing()
add_to_playlist()
