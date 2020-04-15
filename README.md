# Spotify Playlist Creator from Various Sources 
@nirbenz
@ira7bar

## Spotify Authentication

Both modules require this. 
You need to create a file named `spotify.yaml` in this directory with your spotify login credentials.
It should look like this:
```yaml
OAuth_Token: <token>
user_id: <spotify user id>
```
To get your token, go [here](https://developer.spotify.com/console/get-recommendations/).

To get your Spotify user id, go into Spotify, click your Name, and in the account page that's click `Share->Copy Profile Link`. 

You'll get something like this: `https://open.spotify.com/user/<user_id>?<some_junk>` which has the `user_id` you need.

## Usage HtmlToPlaylist
Call this with `python to_playlist.py -h`. There are several optional arguments.

## Usage StreamingToPlaylist
To use the StreamingToPlaylist module, you need to download your spotify data. 
Enter your account dashboard at https://www.spotify.com/. In the privacy settings, apply for the download of your personal data. This might take a few days. When you get the mail, download the zip archive and place the MyData dir path as the spotify_data_path parameter.
