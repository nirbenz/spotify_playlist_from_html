import re

import spotipy
import yaml


def get_spotipy_object(token):
    sp = spotipy.Spotify(auth=token)
    try:
        sp.search('M')
    except spotipy.client.SpotifyException as e:
        print(f"Credentials error!", e)
        exit(-1)
    return sp


def create_playlist_from_track_ids(sp, user_id, playlist_name, playlist_description, is_public, track_ids):
    playlist_result = sp.user_playlist_create(user_id,
                                              playlist_name,
                                              public=is_public,
                                              description=playlist_description)
    playlist_id = playlist_result['id']
    sp.user_playlist_add_tracks(user_id, playlist_id, track_ids)
    playlist_url = playlist_result['external_urls']['spotify']
    return playlist_url


def get_song(sp, name, artist, album=None):
    # TODO use album as well if given
    try:
        result = sp.search(f"{artist} {name}")
        if not result['tracks']['items']:
            name = re.sub(r"[\(\[].*?[\)\]]", "", name).strip()
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


def remove_duplicates_keep_order(lst):
    lst_no_dup = []
    [lst_no_dup.append(t) for t in lst if t not in lst_no_dup]
    return lst_no_dup


def track_ids_from_infos(track_infos):
    return [u['id'] for u in track_infos]
