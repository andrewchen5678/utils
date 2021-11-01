#!/usr/bin/env python3

import os
import json
import subprocess
import sys
from urllib.parse import urlparse

cur_dir = os.getcwd()

data = None

def get_youtube_dl_with_default_options(options):
    dl_proxy = sys.argv[1]
    #print(sys.argv)
    parsed_url = urlparse(dl_proxy)
    #print(parsed_url)
    if(parsed_url.scheme!='socks5'):
        raise ValueError('need to pass socks5://host:port')
    cmd = ['youtube-dl', '-v', '--proxy', dl_proxy ]+options
    print(cmd)
    return cmd


with open(os.path.join(cur_dir,'youtube_conf.json'),'r') as f:
    data = json.load(f)

playlist_id = data['playlist_id']
after_video_id = data['after_video_id']
exclude_ids = set(data['exclude_ids'])

result = subprocess.run(get_youtube_dl_with_default_options(['--flat-playlist', '-J', 'https://www.youtube.com/playlist?list='+playlist_id]), shell=False, check=False, capture_output=True)
if result.returncode != 0:
    raise ValueError(result.stderr)
video_list = json.loads(result.stdout)

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
    #if(new_id=='8giATJyk2lM'): # test failure
    #    new_id = 'nosirvechafa'
    result = subprocess.run(
        get_youtube_dl_with_default_options(['-f', '140', 'https://www.youtube.com/watch?v='+new_id]), shell=False)
    if result.returncode == 0:
        exclude_ids.add(new_id) # exclude success ones for the future

data['after_video_id'] = None
data['exclude_ids'] = sorted(exclude_ids)

with open(os.path.join(cur_dir,'youtube_conf_new.json'),'w') as f:
    json.dump(data,f,indent=2)

os.rename(os.path.join(cur_dir,'youtube_conf_new.json'),os.path.join(cur_dir,'youtube_conf.json'))