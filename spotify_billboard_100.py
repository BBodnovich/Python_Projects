'''
Creates a spotify playlist for each year's Billboard Top 100 songs
Naming convention is 'Billboard 100 - <year>'

Usage:
1) Set up Spotify Developer API for your account
2) Make the modifications for your personal account data below
3) Enjoy some nostalgic music

Modifications:
    SPOTIFY_CLIENT_ID
    SPOTIFY_CLIENT_SECRET
    SPOTIFY_REDIRECT_URI
    SPOTIFY_USERNAME
'''


import requests
from bs4 import BeautifulSoup
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth


# Constants for use with Spotipy API
SPOTIFY_CLIENT_ID = "REDACTED"
SPOTIFY_CLIENT_SECRET = "REDACTED"
SPOTIFY_REDIRECT_URI = "REDACTED"
SPOTIFY_USERNAME = "REDACTED"


def get_playlist(date):
    '''
    Retrieves the Billboard top 100 songs for the given year.

    :params date: The date in format 'YYYY-MM-DD'.
    :return: List of tuples containing song/artist pairs for each song.
    '''
    agent = {"User-Agent":"Mozilla/5.0"}
    page_url = f"https://www.billboard.com/charts/hot-100/{date}/"
    page_data = requests.get(page_url, headers=agent, timeout=15).text
    soup = BeautifulSoup(page_data, "html.parser")

    song_titles = soup.select(selector="li  h3", class_="c-title")
    songs_list = [title.getText().strip() for title in song_titles[:100]]
    artist_list = []

    for num in range(100):
        parent = song_titles[num].parent
        artist = parent.span.getText().strip()
        artist_list.append(artist)

    return list(zip(songs_list, artist_list))


def add_spotify_playlist(input_list, year):
    '''
    Creates a Spotify playlist with the input list generated from get_playlist().

    param input_list: List of 100 song/artist tuple pairs.
    param year: The year of the playlist in format 'YYYY'.
    '''
    sp = Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-modify-private",
            redirect_uri=SPOTIFY_REDIRECT_URI,
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            show_dialog=True,
            cache_path="token.txt",
            username=SPOTIFY_USERNAME
        )
    )
    user_id = sp.current_user()["id"]

    song_uris = []
    for song, artist in input_list:
        results = sp.search(q=f"{song} {artist}", type='track', limit=1)
        if results['tracks']['items']:
            track_id = results['tracks']['items'][0]['id']
            song_uris.append(track_id)
        else:
            print(f"Could not find {song} by {artist} on Spotify.")

    playlist_name = f"Billboard 100 - {year.split('-')[0]}"
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)

    sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)


def main(billboard_years):
    '''
    Main function that takes query years and processes them through playlist lookup and creation.

    param billboard_years: List of years in format 'YYYY-MM-DD'.
    '''
    for single_date in billboard_years:
        song_artist_list = get_playlist(single_date)
        playlist_date = single_date.split('-')[0]
        add_spotify_playlist(song_artist_list, playlist_date)


if __name__ == '__main__':
    dates = [f'{item}-07-04' for item in range(2020,2021)]
    main(dates)