import argparse

# local imports
from spotify_abs_cls import SpotifyHandler


def parse_args():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--spotify_yaml_path', '-s', help='Spotify credentials yaml file', required=True, type=str)
    parser.add_argument('--playlist_name', '-pn', type=str, help='Output playlist name', required=True)
    parser.add_argument('--playlist_description', '-pd', help='Output playlist description',
                        default='', type=str)
    return parser.parse_args()


class AutoParty(SpotifyHandler):
    """
    """

    def __init__(self, spotify_yaml_path, playlist_name, playlist_description):
        """
        see the parse_args function for documentation on the parameters.
        """
        super().__init__(spotify_yaml_path, playlist_name, playlist_description)

    def run(self):
        start_track = {
            "name": "poker face",
            "artist": "lady gaga"
        }

        end_track = {
            "name": "the rock show",
            "artist": "blink 182"
        }

        start_genres = self._get_track_genres(start_track)
        end_genres = self._get_track_genres(end_track)

        for genres in [start_genres, end_genres]:
            print(f"genres: {genres}")
            track_infos = self._sp.recommendations(seed_genres=genres, limit=5)
            track_names = [track["name"] for track in track_infos["tracks"]]
            track_artist_names = [self._get_track_info_artists_string(track) for track in track_infos["tracks"]]

            track_full_names = [f"{artist} - {name}" for artist, name in zip(track_artist_names, track_names)]

            print(f"tracks: {track_full_names}")

    def _get_track_id(self, track):
        return self._get_track_info(track)["id"]

    def _get_track_info_artist_names(self, track_info):
        artist_names = [artist["name"] for artist in track_info["artists"]]
        return artist_names

    def _get_track_info_artists_string(self, track_info):
        return " & ".join(self._get_track_info_artist_names(track_info))

    def _get_track_genres(self, track):
        genres = []
        track_info = self._get_track_info(track)
        artist_ids = [artist["id"] for artist in track_info["artists"]]
        for artist_id in artist_ids:
            artist_info = self._sp.artist(artist_id)
            genres.extend(artist_info["genres"])
        return genres

    def _get_track_info(self, track):
        return self._get_song(track["name"], track["artist"])


def main():
    args = parse_args()
    streaming_to_playlist = AutoParty(**vars(args))
    streaming_to_playlist.run()


if __name__ == '__main__':
    main()
