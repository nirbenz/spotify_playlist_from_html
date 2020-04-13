import argparse

import pandas as pd

import utils

IS_PUBLIC_PLAYLIST = True


def parse_args():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--html-file', '-f', type=str, help='HTML file path',
                        default='bidud_party.html', )
    parser.add_argument('--spotify-yaml', '-s', help='Spotify credentials file',
                        default='./spotify.yaml', type=str)
    parser.add_argument('--playlist-name', '-n', type=str, default='Bidud Party Tests', help='Playlist name')
    parser.add_argument('--playlist-description', '-d', type=str, default='Yayz', help='Playlist description')
    return parser.parse_args()


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

    config = utils.read_yaml(spotify_yaml)
    user_id = config["user_id"]
    token = config["OAuth_Token"]

    sp = utils.get_spotipy_object(token)
    sp.trace = False
    tracks = []
    for index, row in playlist_table.iterrows():
        song_uri_thinger = utils.get_song(sp, name=row['Title'], artist=row['Artist'], album=row['Release'])
        if song_uri_thinger is None:
            print(f"Skipping [{row['Artist']} - {row['Title']}]")
            continue
        tracks.append(song_uri_thinger)

    track_infos_no_dup = utils.remove_duplicates_keep_order(tracks)

    track_ids = utils.track_ids_from_infos(track_infos_no_dup)

    playlist_url = utils.create_playlist_from_track_ids(sp,
                                                        user_id,
                                                        playlist_name,
                                                        playlist_description,
                                                        IS_PUBLIC_PLAYLIST,
                                                        track_ids)

    print(f"Success: Playlist URL at {playlist_url}")


if __name__ == '__main__':
    args = parse_args()
    parse_html(**vars(args))
