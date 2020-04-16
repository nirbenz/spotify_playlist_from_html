import argparse
import ast
import os
import sys
import time
from datetime import datetime
from os import listdir
from tqdm import tqdm

# local imports
import utils
from spotify_abs_cls import SpotifyHandler

# constants
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M'


def parse_args():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--spotify_yaml_path', '-s', help='Spotify credentials yaml file', required=True, type=str)
    parser.add_argument('--playlist_name', '-pn', type=str, help='Output playlist name', required=True)
    parser.add_argument('--playlist_description', '-pd', help='Output playlist description',
                        default='', type=str)
    parser.add_argument('--start_time', '-st', type=str, default='1970-01-01 12:00',
                        help=f'Start time in {DATE_TIME_FORMAT} format')
    parser.add_argument('--end_time', '-et', type=str, default='2070-01-01 12:00',
                        help=f'End time in {DATE_TIME_FORMAT} format')
    parser.add_argument('--spotify_data_path', '-d', type=str, help='Path to the Spotify MyData dir', default=None)
    return parser.parse_args()


class StreamingToPlaylist(SpotifyHandler):
    """
    Create playlist from streaming history, with defined time ranges.
    The scope in config.py must contain the following: "playlist-modify-private playlist-modify-public"
    """

    STREAMING_HISTORY_FILE_PREFIX = "StreamingHistory"

    def __init__(self, spotify_yaml_path, playlist_name, playlist_description, start_time, end_time,
                 spotify_data_path=None):
        """
        see the parse_args function for documentation on the parameters.
        """
        self._spotify_data_path = spotify_data_path
        self._start_time = self._date_string_to_datetime(start_time)
        self._end_time = self._date_string_to_datetime(end_time)
        #
        super().__init__(spotify_yaml_path, playlist_name, playlist_description)

    def run(self):
        if self._spotify_data_path is None:
            track_infos = self._get_streamings_direct()
        else:
            streamings = self._get_streamings_json()
            track_infos = self._search_json_tracks(streamings)

        print(f"Removing duplicate tracks")
        track_infos_no_dup = utils.remove_duplicates_keep_order(track_infos)

        track_ids = utils.track_ids_from_infos(track_infos_no_dup)

        print(f"Final tracks number: {len(track_ids)}")

        playlist_url = self._create_playlist_from_track_ids(track_ids)

        print(f"Done. Playlist created at URL: {playlist_url}")

    def _filter_streamings_by_time_range(self, streamings):
        filtered_streamings = []
        for streaming in streamings:
            track_datetime = streaming['datetime']
            if self._start_time <= track_datetime <= self._end_time:
                filtered_streamings.append(streaming)
        return filtered_streamings

    @staticmethod
    def to_unix_milliseconds(date_obj):
        return int(time.mktime(date_obj.timetuple()) * 1e3 + date_obj.microsecond / 1e3)

    @staticmethod
    def _date_string_to_datetime(date_string):
        return datetime.strptime(date_string, DATE_TIME_FORMAT)

    def _get_streamings_direct(self):
        print("This code currently isn't supported nor well understood", file=sys.stderr)
        start_unix = StreamingToPlaylist.to_unix_milliseconds(self._start_time)
        end_unix = StreamingToPlaylist.to_unix_milliseconds(self._end_time)
        all_songs = []
        for current_start in range(start_unix, end_unix, int(1.8e+6)):
            result = self._sp.current_user_recently_played(limit=50, after=current_start)
            after, before = result['cursors']['after'], result['cursors']['before']
            all_songs += result['items']

        result = self._sp.current_user_recently_played(limit=50, before=end_unix)
        all_songs += result['items']
        all_songs = utils.remove_duplicates_keep_order(all_songs)
        return [a['track'] for a in all_songs]

    def _get_streamings_json(self):
        """
        Returns a list of streamings form spotify MyData dump.
        Also adds a datetime field.
        """
        data_file_paths = [os.path.join(self._spotify_data_path, f) for f in listdir(self._spotify_data_path) if
                           os.path.isfile(os.path.join(self._spotify_data_path, f))]
        streamings_file_paths = [file_path for file_path in data_file_paths if
                                 self.STREAMING_HISTORY_FILE_PREFIX in os.path.basename(file_path)]

        all_streamings = []

        for streamings_file_path in streamings_file_paths:
            with open(streamings_file_path, 'r', encoding='UTF-8') as f:
                new_streamings = ast.literal_eval(f.read())
                all_streamings += [streaming for streaming in new_streamings]

        # adding datetime field
        for streaming in all_streamings:
            streaming['datetime'] = datetime.strptime(streaming['endTime'], '%Y-%m-%d %H:%M')
        return all_streamings

    def _search_json_tracks(self, streamings):
        print(f'Recovered {len(streamings)} streamings from history')

        streamings = self._filter_streamings_by_time_range(streamings)

        print(f"Number of tracks in history range: {len(streamings)}")

        print(f"Getting tracks info from Spotify")
        track_infos = []
        unknown_tracks_num = 0
        for streaming in tqdm(streamings):
            track_name = streaming['trackName']
            artist_name = streaming['artistName']
            if track_name == "Unknown Track" or artist_name == "Unknown Artist":
                unknown_tracks_num += 1
                continue
            track_info = self._get_song(track_name, artist_name, "")
            if track_info is not None:
                track_infos.append(track_info)

        print(f"Skipped {unknown_tracks_num} unknown tracks or artists in history range")
        return track_infos


def main():
    args = parse_args()
    streaming_to_playlist = StreamingToPlaylist(**vars(args))
    streaming_to_playlist.run()


if __name__ == '__main__':
    main()
