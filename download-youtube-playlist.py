#!/usr/bin/env python3

import os
import json
import subprocess

cur_dir = os.getcwd()

data = None

with open(os.path.join(cur_dir,'youtube_conf.json'),'r') as f:
    data = json.load(f)

playlist_id = data['playlist_id']
after_video_id = data['after_video_id']
exclude_ids = set(data['exclude_ids'])

result = subprocess.run(['youtube-dl', '--flat-playlist', '-J', 'https://www.youtube.com/playlist?list='+playlist_id], shell=False, check=True, capture_output=True)
video_list = json.loads(result.stdout)

video_list_new = []
for item in video_list['entries']:
    cur_id = item['id']
    if cur_id in exclude_ids: # skip
        continue
    if cur_id == after_video_id:
        break
    video_list_new.append(item)

print(json.dumps(video_list_new,indent=2))

new_after_id = after_video_id
has_failed = False

for item in reversed(video_list_new):
    new_id = item['id']
    if(new_id=='OFshAzE8KsI'): # test failure
        new_id = 'nosirvechafa'
    result = subprocess.run(
        ['youtube-dl', '-f', '140', 'https://www.youtube.com/watch?v=' + new_id], shell=False,
        check=False)
    if result.returncode == 0:
        if not has_failed:
            new_after_id = new_id
        exclude_ids.add(new_after_id) # exclude success ones for the future
    else:
        has_failed = True # current one failed, don't increase new_after_id anymore

data['after_video_id'] = new_after_id
data['exclude_ids'] = exclude_ids

with open(os.path.join(cur_dir,'youtube_conf_new.json'),'w') as f:
    json.dump(data,f,indent=2)

os.rename(os.path.join(cur_dir,'youtube_conf_new.json'),os.path.join(cur_dir,'youtube_conf.json'))