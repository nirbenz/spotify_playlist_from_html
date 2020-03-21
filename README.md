# Spotify Playlist Creator from HTML Table

## Usage
Call this with `python to_playlist.py -h`. There are several optional arguments.
You need to create a file named `spotify.yaml` in this directory with your spotify login credentials.
It should look like this:
```yaml
OAuth_Token: <token>
user_id: <spotify user id>
```
To get your token, go [here](https://developer.spotify.com/console/get-recommendations/).
To get your Spotify user id, go into Spotify, click your Name, and in the account page that's click `Share->Copy Profile Link`. 
You'll get something like this: `https://open.spotify.com/user/<user_id>?<some_junk>` which has the `user_id` you need.
