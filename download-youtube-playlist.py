#!/usr/bin/env python3

import os
import json
import subprocess
import sys
from urllib.parse import urlparse
from yt_dlp import YoutubeDL
import yt_dlp
import pprint

from yt_dlp.postprocessor.common import PostProcessor

cur_dir = os.getcwd()

data = None

# ℹ️ See the docstring of yt_dlp.postprocessor.common.PostProcessor
class FFmpegFixupCloudFlare(yt_dlp.postprocessor.ffmpeg.FFmpegFixupPostProcessor):
    @PostProcessor._restrict_to(images=False, video=False)
    def run(self, info):
        if info.get('container') == 'm4a_dash':
            self._fixup('clean up so that cloudflare ipfs doesnt complaint', info['filepath'], [
                '-vn', '-c:a', 'copy', '-movflags', '+faststart'])
        return [], info

def download_fixed_m4a(url,dl_proxy):
    ydl_opts = {
        'format': '140',
        'proxy':dl_proxy,
        'verbose': True,
        'outtmpl': {
            'default':'%(title).75s [%(id)s].%(ext)s',
        },
        'postprocessors': [{
            # Embed metadata in video using ffmpeg.
            # ℹ️ See yt_dlp.postprocessor.FFmpegMetadataPP for the arguments it accepts
            'key': 'FFmpegMetadata',
            #'add_chapters': True,
            'add_metadata': True,
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.add_post_processor(FFmpegFixupCloudFlare())
        ydl.download([url])

def list_playlist(url,dl_proxy):
    ydl_opts = {
        'proxy':dl_proxy,
        'quiet': True,
        'dump_single_json': True,
        'extract_flat': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url)

if __name__ == "__main__":
    #download_fixed_m4a('https://www.youtube.com/watch?v=UvPit5rTDQc')
    #exit(0)
    dl_proxy = sys.argv[1]
    #print(sys.argv)
    parsed_url = urlparse(dl_proxy)
    #print(parsed_url)
    if(parsed_url.scheme!='socks5'):
        raise ValueError('need to pass socks5://host:port')
    with open(os.path.join(cur_dir,'youtube_conf.json'),'r') as f:
         data = json.load(f)

    playlist_id = data['playlist_id']
    after_video_id = data['after_video_id']
    exclude_ids = set(data['exclude_ids'])

    video_list = list_playlist(url='https://www.youtube.com/playlist?list='+playlist_id,dl_proxy=dl_proxy)

    #print(video_list['entries'][0])
    #exit(0)

    skip_rest = False

    video_list_new = []
    for item in video_list['entries']:
        cur_id = item['id']
        if skip_rest:
            exclude_ids.add(cur_id)
            continue

        if after_video_id and cur_id == after_video_id:
            exclude_ids.add(cur_id)
            skip_rest = True # skip everything after that
            continue

        if cur_id in exclude_ids: # skip
            continue
        video_list_new.append(item)

    print(json.dumps(video_list_new,indent=2))


    for item in reversed(video_list_new):
        new_id = item['id']
        try:
            returncode = download_fixed_m4a('https://www.youtube.com/watch?v='+new_id,dl_proxy)
            if returncode == 0:
                exclude_ids.add(new_id) # exclude success ones for the future
        except yt_dlp.utils.DownloadError as e:
            pass        

    data['after_video_id'] = None
    data['exclude_ids'] = sorted(exclude_ids)

    print('updating config',file=sys.stderr)

    with open(os.path.join(cur_dir,'youtube_conf_new.json'),'w') as f:
        json.dump(data,f,indent=2)

    os.rename(os.path.join(cur_dir,'youtube_conf_new.json'),os.path.join(cur_dir,'youtube_conf.json'))
