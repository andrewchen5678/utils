# utils
utils

```
brew install id3lib
brew install ffmpeg
```

use ffmpeg_cut_off to cut off a couple second of each m4a file in a directory

# download youtube playlist through proxy

create `youtube_conf.json`:
```json
{
  "playlist_id": "playlistid",
  "after_video_id": "youtubevideoid", // will be removed after first successful run
  "exclude_ids": [
  ]
}
```
