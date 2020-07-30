import argparse
import pandas as pd

# local
import utils
from spotify_abs_cls import SpotifyHandler

# constants
HTML_EXTENSIONS = ['html', 'htm']


def parse_args():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--spotify-yaml-path', '--spotify_yaml_path', '-s', help='Spotify credentials file',
                        default='./spotify.yaml', type=str)
    parser.add_argument('--html-file-path', '-f', type=str, help='HTML file path',
                        default='bidud_party.html', )
    parser.add_argument('--playlist-name', '-n', type=str, default='Bidud Party Tests', help='Playlist name')
    parser.add_argument('--playlist-description', '-d', type=str, default='Yayz', help='Playlist description')
    return parser.parse_args()


class HtmlToPlaylist(SpotifyHandler):
    """
    Create playlist from a given HTML page.
    """

    def __init__(self, spotify_yaml_path, html_file_path, playlist_name, playlist_description):
        """
        see the parse_args function for documentation on the parameters.
        """
        self._html_file_path = html_file_path
        #
        super().__init__(spotify_yaml_path, playlist_name, playlist_description)

    def run(self):
        playlist_table = self._parse_playlist_file()

        tracks = []
        for index, row in playlist_table.iterrows():
            song_uri_thinger = self._get_song(name=row['Title'], artist=row['Artist'], album=row['Release'])
            if song_uri_thinger is None:
                print(f"Skipping [{row['Artist']} - {row['Title']}]")
                continue
            tracks.append(song_uri_thinger)

        track_infos_no_dup = utils.remove_duplicates_keep_order(tracks)
        track_ids = utils.track_ids_from_infos(track_infos_no_dup)

        playlist_url = self._create_playlist_from_track_ids(track_ids)

        print(f"Success: Playlist URL at {playlist_url}")

    def _parse_playlist_file(self):
        if self._html_file_path.split('.')[-1] in HTML_EXTENSIONS:
            return self._parse_html_playlist()
        elif self._html_file_path.split('.')[-1] == 'csv':
            return self._parse_csv_playlist()
        else:
            raise RuntimeError("Only CSV and HTML playlists supported!")

    def _parse_html_playlist(self):
        with open(self._html_file_path, 'rb') as fid:
            html_text = fid.read()
        tables = pd.read_html(html_text)
        playlist_table = tables[0]
        playlist_table = playlist_table.rename(columns=playlist_table.iloc[0])
        playlist_table = playlist_table.drop(playlist_table.index[0])
        return playlist_table

    def _parse_csv_playlist(self):
        playlist_table = pd.read_csv(self._html_file_path)
        playlist_table = playlist_table.rename(columns=playlist_table.iloc[0])
        playlist_table = playlist_table.drop(playlist_table.index[0])
        playlist_table['Release'] = None
        return playlist_table


def main():
    args = parse_args()
    html_to_playlist_obj = HtmlToPlaylist(**vars(args))
    html_to_playlist_obj.run()


if __name__ == '__main__':
    main()
