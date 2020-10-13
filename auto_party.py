import argparse

import numpy as np
import pandas as pd

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
    TODO
    """

    AUDIO_FEATURES = ["danceability", "energy", "loudness", "liveness", "valence"]
    TIMESTAMP = "timestamp"

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

        start_timestamp = 0
        end_timestamp = 15

        track_infos, interpolated_features = self._interpolate_tracks(start_track, start_timestamp,
                                                                      end_track, end_timestamp)

        tracks_features = [self._get_features_from_track_info(info) for info in track_infos]
        track_full_names = self._get_full_track_names_from_infos(track_infos)

        print("\nResults:\n")

        for track_index, (name, features) in enumerate(zip(track_full_names, tracks_features)):
            input_features = interpolated_features.iloc[track_index].to_dict()
            del input_features[self.TIMESTAMP]
            print(f"{name}\ninput_features: {input_features}\nresult_features: {features}\n")

    def _interpolate_tracks(self, start_track, start_timestamp,
                            end_track, end_timestamp):
        interpolated_features = self._get_features_interpolated_df(start_track, start_timestamp,
                                                                   end_track, end_timestamp)
        start_genres = self._get_track_genres(start_track)
        print(f"start genres: {start_genres}")
        end_genres = self._get_track_genres(end_track)
        print(f"end genres: {end_genres}")

        all_genres = start_genres + end_genres
        print(f"using genre union as seeds: {all_genres}")

        track_infos = []
        for index, row in interpolated_features.iterrows():
            features_dict = row.to_dict()
            target_features_dict = dict()
            for key in features_dict.keys():
                if key == self.TIMESTAMP:
                    continue
                target_features_dict["target_" + key] = features_dict[key]
            track_infos.extend(
                self._sp.recommendations(seed_genres=all_genres, limit=1, **target_features_dict)["tracks"])

        return track_infos, interpolated_features

    def _get_features_interpolated_df(self, start_track, start_timestamp,
                                      end_track, end_timestamp):
        start_df = self.get_track_features_df(start_track, start_timestamp)
        end_df = self.get_track_features_df(end_track, end_timestamp)
        print(f"initial features:\n{pd.concat([start_df, end_df])}")
        for timestamp in range(start_timestamp + 1, end_timestamp):
            s = pd.Series([timestamp] + [np.nan] * len(self.AUDIO_FEATURES),
                          index=[self.TIMESTAMP] + self.AUDIO_FEATURES)
            start_df = start_df.append(s, ignore_index=True)

        total_df = pd.concat([start_df, end_df])
        total_df = total_df.interpolate(method='linear', limit_direction='forward', axis=0)
        print(f"interpolated features:\n{total_df}")
        return total_df.iloc[1:-1]

    def get_track_features_df(self, track, timestamp):
        features = self._get_track_features(track)[0]
        features[self.TIMESTAMP] = timestamp
        wanted_feature_names = [self.TIMESTAMP] + self.AUDIO_FEATURES
        filtered_features = {key: [value] for key, value in features.items() if key in wanted_feature_names}
        df = pd.DataFrame(filtered_features, columns=wanted_feature_names)
        return df

    def _get_full_track_names_from_infos(self, track_infos):
        track_names = [track["name"] for track in track_infos]
        track_artist_names = [self._get_track_info_artists_string(track) for track in track_infos]
        return [f"{artist} - {name}" for artist, name in zip(track_artist_names, track_names)]

    def _get_track_features(self, track):
        # example:
        # 'danceability': 0.851, 'energy': 0.806, 'key': 4, 'loudness': -4.62, 'mode': 1,
        #  'speechiness': 0.0787, 'acousticness': 0.118, 'instrumentalness': 1.64e-06,
        #  'liveness': 0.121, 'valence': 0.787, 'tempo': 118.999
        track_id = self._get_track_id(track)
        features = self._sp.audio_features([track_id])
        return features

    def _get_features_from_track_info(self, track_info, filter_features=True):
        track_id = track_info["id"]
        features = self._sp.audio_features([track_id])[0]
        if filter_features:
            features = {key: value for key, value in features.items() if key in self.AUDIO_FEATURES}
        return features

    def _get_track_id(self, track):
        return self._get_track_info(track)["id"]

    def _get_track_info_artist_names(self, track_info):
        artist_names = [artist["name"] for artist in track_info["artists"]]
        return artist_names

    def _get_track_info_artists_string(self, track_info):
        return " & ".join(self._get_track_info_artist_names(track_info))

    def _get_track_genres(self, track):
        # can try and obtain genre from album as well
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
