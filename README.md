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
  // will be removed after successful run, it must exists 
  // for the first run otherwise will try to download the whole list 
  "after_video_id": "youtubevideoid", 
  "exclude_ids": [
  ]
}
```
