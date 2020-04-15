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
        self._sp = utils.get_spotipy_object(self._token)
