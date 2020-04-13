import argparse
import ast
import os
from datetime import datetime
from os import listdir

import spotipy
from tqdm import tqdm

import utils

DATE_TIME_FORMAT = '%Y-%m-%d %H:%M'


def parse_args():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--spotify_data_path', '-d', type=str, help='Path to the Spotify MyData dir', required=True)
    parser.add_argument('--spotify_yaml_path', '-s', help='Spotify credentials yaml file', required=True, type=str)
    parser.add_argument('--playlist_name', '-pn', type=str, help='Output playlist name', required=True)
    parser.add_argument('--playlist_description', '-pd', help='Output playlist description',
                        default='', type=str)
    parser.add_argument('--start_time', '-st', type=str, default='1970-01-01 12:00',
                        help=f'Start time in {DATE_TIME_FORMAT} format')
    parser.add_argument('--end_time', '-et', type=str, default='2070-01-01 12:00',
                        help=f'End time in {DATE_TIME_FORMAT} format')
    return parser.parse_args()


class StreamingToPlaylist(object):
    """
    Create playlist from streaming history, with defined time ranges.
    The scope in config.py must contain the following: "playlist-modify-private playlist-modify-public"
    """

    STREAMING_HISTORY_FILE_PREFIX = "StreamingHistory"
    IS_PUBLIC_PLAYLIST = True

    def __init__(self, spotify_yaml_path, spotify_data_path, playlist_name, playlist_description, start_time, end_time):
        """
        see the parse_args function for documentation on the parameters.
        """
        self._spotify_data_path = spotify_data_path
        self._spotify_yaml_path = spotify_yaml_path
        self._playlist_name = playlist_name
        self._playlist_description = playlist_description
        self._start_time = self._date_string_to_datetime(start_time)
        self._end_time = self._date_string_to_datetime(end_time)

        config = utils.read_yaml(self._spotify_yaml_path)
        self._user_id = config["user_id"]
        self._token = config["OAuth_Token"]

        self._sp = spotipy.Spotify(auth=self._token)
        try:
            self._sp.search('M')
        except spotipy.client.SpotifyException as e:
            print(f"Credentials error!", e)
            exit(-1)

    def run(self):
        streamings = self._get_streamings()
        print(f'Recovered {len(streamings)} streamings.')

        streamings = self._filter_streamings_by_time_range(streamings)

        track_infos = []
        for streaming in tqdm(streamings):
            track_name = streaming['trackName']
            artist_name = streaming['artistName']
            if track_name == "Unknown Track" or artist_name == "Unknown Artist":
                continue
            track_info = utils.get_song(self._sp, track_name, artist_name, "")
            if track_info is not None:
                track_infos.append(track_info)

        track_infos_no_dup = utils.remove_duplicates_keep_order(track_infos)

        track_ids = utils.track_ids_from_infos(track_infos_no_dup)

        playlist_url = utils.create_playlist_from_track_ids(self._sp,
                                                            self._user_id,
                                                            self._playlist_name,
                                                            self._playlist_description,
                                                            self.IS_PUBLIC_PLAYLIST,
                                                            track_ids)

        print(f"Success: Playlist URL at {playlist_url}")

    def _get_streamings(self):
        """
        Returns a list of streamings form spotify MyData dump.
        Also adds a datetime field.
        """
        data_dir_path = self._spotify_data_path
        data_file_paths = [os.path.join(data_dir_path, f) for f in listdir(data_dir_path) if
                           os.path.isfile(os.path.join(data_dir_path, f))]
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

    def _filter_streamings_by_time_range(self, streamings):
        filtered_streamings = []
        for streaming in streamings:
            track_datetime = streaming['datetime']
            if self._start_time <= track_datetime <= self._end_time:
                filtered_streamings.append(streaming)
        return filtered_streamings

    @staticmethod
    def _date_string_to_datetime(date_string):
        return datetime.strptime(date_string, DATE_TIME_FORMAT)


def main():
    args = parse_args()
    streaming_to_playlist = StreamingToPlaylist(**vars(args))
    streaming_to_playlist.run()


if __name__ == '__main__':
    main()
