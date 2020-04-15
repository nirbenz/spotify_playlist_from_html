import re

import spotipy

import utils


class SpotifyHandler(object):
    """
    Superclass for spotify fun
    """
    def __init__(self, spotify_yaml_path):
        """
        see the parse_args function for documentation on the parameters.
        """
        self._spotify_yaml_path = spotify_yaml_path
        config = utils.read_yaml(self._spotify_yaml_path)
        self._user_id = config["user_id"]
        self._token = config["OAuth_Token"]
        self._sp = self._get_spotify_object(self._token)


    def _create_playlist_from_track_ids(self, user_id, playlist_name, playlist_description, is_public, track_ids):
        playlist_result = self._sp.user_playlist_create(user_id,
                                                  playlist_name,
                                                  public=is_public,
                                                  description=playlist_description)
        playlist_id = playlist_result['id']
        self._sp.user_playlist_add_tracks(user_id, playlist_id, track_ids)
        playlist_url = playlist_result['external_urls']['spotify']
        return playlist_url


    def _get_song(self, name, artist, album=None):
        # TODO use album as well if given
        try:
            result = self._sp.search(f"{artist} {name}")
            if not result['tracks']['items']:
                name = re.sub(r"[\(\[].*?[\)\]]", "", name).strip()
                result = self._sp.search(f"{artist} {name}")
            if not result['tracks']['items']:
                artist = artist.split('Vs.')[0].strip()
                result = self._sp.search(f"{artist} {name}")
            if not result['tracks']['items']:
                artist = artist.split('And')[0].strip()
                result = self._sp.search(f"{artist} {name}")
            for i in result['tracks']['items']:
                if any([i['artists'][0]['name'] == a for a in artist.split('&')]) and (i['name'] == name):
                    return i
            else:
                result['tracks']['items'].sort(key=lambda x: x['popularity'])
                return result['tracks']['items'][-1]
        except:
            return None


    def _get_spotify_object(self, token):
        sp = spotipy.Spotify(auth=token)
        try:
            sp.search('M')
        except spotipy.client.SpotifyException as e:
            print(f"Credentials error!", e)
            exit(-1)
        return sp