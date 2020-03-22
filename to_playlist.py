import argparse
import re
import sys

import pandas as pd
import spotipy
import yaml


def parse_args():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--html-file', '-f', type=str, help='HTML file path',
                        default='bidud_party.html',)
    parser.add_argument('--spotify-yaml', '-s', help='Spotify credentials file',
                        default='./spotify.yaml', type=str)
    parser.add_argument('--playlist-name', '-n', type=str, default='Bidud Party Tests', help='Playlist name')
    parser.add_argument('--playlist-description', '-d', type=str, default='Yayz', help='Playlist description')
    return parser.parse_args()


def get_song(sp, name, artist, album):
    try:
        result = sp.search(f"{artist} {name}")
        if not result['tracks']['items']:
            name = re.sub("[\(\[].*?[\)\]]", "", name).strip()
            result = sp.search(f"{artist} {name}")
        if not result['tracks']['items']:
            artist = artist.split('Vs.')[0].strip()
            result = sp.search(f"{artist} {name}")
        if not result['tracks']['items']:
            artist = artist.split('And')[0].strip()
            result = sp.search(f"{artist} {name}")
        for i in result['tracks']['items']:
            if any([i['artists'][0]['name'] == a for a in artist.split('&')]) and (i['name'] == name):
                return i
        else:
            result['tracks']['items'].sort(key=lambda x: x['popularity'])
            return result['tracks']['items'][-1]
    except:
        return None

def read_yaml(yaml_path):
    with open(yaml_path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            raise RuntimeError("YAML error")
    return config


def parse_html(html_file, spotify_yaml, playlist_name, playlist_description):
    with open(html_file, 'rb') as fid:
        html_text = fid.read()
    tables = pd.read_html(html_text)
    playlist_table = tables[0]
    playlist_table = playlist_table.rename(columns=playlist_table.iloc[0])
    playlist_table = playlist_table.drop(playlist_table.index[0])
    # with open(html_file[:-5] + '_playlist.txt', 'wb') as fid:
    #     for index, row in playlist_table.iterrows():
    #         fid.write("{} - {}\n".format(row['Artist'], row['Title']).encode("UTF-8"))
            # print(row['Artist'], row['Title'])

    config = read_yaml(spotify_yaml)
    user_id = config["user_id"]
    token = config["OAuth_Token"]

    sp = spotipy.Spotify(auth=token)
    try:
        sp.search('M')
    except spotipy.client.SpotifyException as e:
        print(f"Credentials error!", e)
        exit(-1)
    sp.trace = False
    tracks = []
    for index, row in playlist_table.iterrows():
        song_uri_thinger = get_song(sp, name=row['Title'], artist=row['Artist'], album=row['Release'])
        if song_uri_thinger is None:
            print(f"Skipping [{row['Artist']} - {row['Title']}]")
            continue
        tracks.append(song_uri_thinger)

    # remove duplicates keep order
    tracks_no_dup = []
    [tracks_no_dup.append(t) for t in tracks if t not in tracks_no_dup]


    playlist_result = sp.user_playlist_create(user_id, playlist_name, description=playlist_description)
    playlist_id = playlist_result['id']
    result = sp.user_playlist_add_tracks(user_id, playlist_id, [u['id'] for u in tracks])
    print(f"Success: Playlist URL at {playlist_result['external_urls']['spotify']}")


if __name__ == '__main__':
    args = parse_args()
    parse_html(**vars(args))
